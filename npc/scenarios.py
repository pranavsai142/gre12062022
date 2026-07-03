"""
Reusable NPC scale scenarios (used by npc/server.py, tests/e2e scale tests, and ad-hoc runs).

The flagship scenario is run_full_cycle():
    draft -> canidate -> N voters cast real immutable ballots (concurrently,
    through the exact production HTTP surface) -> operator promote -> metrics.

Every network action goes through NPCClient (real Firebase auth + real endpoints),
so results reflect true gunicorn/Render behavior. Direct Database access is used
only for verification assertions and cleanup, per TESTING.md.

Safety: window ids must carry a test prefix (SCALE-/TEST-/E2E-) unless
ALLOW_REAL_WINDOW=1 is set, so a run can never pollute a real ISO-week window
by accident — even when targeting a deployed Render instance.
"""

import os
import time
import concurrent.futures
from typing import Dict, Any, Optional

from .npc_client import NPCClient
from .npc_manager import NPCManager

SAFE_WINDOW_PREFIXES = ("SCALE-", "TEST-", "E2E-")


def _assert_safe_window(window_id: str):
    if os.environ.get("ALLOW_REAL_WINDOW") == "1":
        return
    if not str(window_id).startswith(SAFE_WINDOW_PREFIXES):
        raise ValueError(
            f"Refusing to run a scenario on window '{window_id}'. "
            f"Use a {'/'.join(SAFE_WINDOW_PREFIXES)} prefixed window (or set ALLOW_REAL_WINDOW=1)."
        )


def _percentile(values, pct):
    if not values:
        return 0.0
    values = sorted(values)
    idx = min(len(values) - 1, max(0, int(round(pct / 100.0 * (len(values) - 1)))))
    return values[idx]


def run_full_cycle(
    base_url: str = "http://localhost:5000",
    window_id: Optional[str] = None,
    n_drafters: int = 3,
    n_voters: int = 12,
    concurrency: int = 20,
    yes_fraction: float = 0.6,
    no_fraction: float = 0.25,
    promote: bool = True,
    cleanup: bool = False,
    prefix: str = "npc-scale-",
) -> Dict[str, Any]:
    """Full governance cycle at scale. Returns a metrics dict.

    yes/no fractions are deterministic voter counts (remainder abstains), so the
    expected tallies — and therefore promotion — are exactly predictable.
    """
    window_id = window_id or f"SCALE-TEST-{int(time.time())}"
    _assert_safe_window(window_id)

    import Database  # verification + cleanup only

    mgr = NPCManager(base_url=base_url)
    metrics: Dict[str, Any] = {"window_id": window_id, "base_url": base_url,
                               "n_drafters": n_drafters, "n_voters": n_voters,
                               "concurrency": concurrency}
    t0 = time.time()

    # --- 0. Operator NPC points the whole site at the test window (real endpoint) ---
    operator = mgr.provision_batch(1, prefix=f"{prefix}operator-")[0]
    operator.set_window_override(window_id)

    created_policy_ids = []
    try:
        # --- 1. Drafters: create + submit policies (concurrently) ---
        t = time.time()
        drafters = mgr.provision_batch(n_drafters, prefix=f"{prefix}drafter-", concurrency=concurrency)
        metrics["provision_drafters_sec"] = round(time.time() - t, 2)

        t = time.time()
        with concurrent.futures.ThreadPoolExecutor(max_workers=concurrency) as ex:
            futures = [
                ex.submit(c.draft_and_submit_policy,
                          f"Scale Policy {window_id} #{i}",
                          f"Synthetic policy #{i} created by the NPC scale harness on window {window_id}.")
                for i, c in enumerate(drafters)
            ]
            for f in concurrent.futures.as_completed(futures):
                created_policy_ids.append(f.result())
        metrics["drafting_sec"] = round(time.time() - t, 2)
        metrics["policies_created"] = len(created_policy_ids)

        # --- 2. Voters: provision + everyone casts one real ballot (concurrently) ---
        t = time.time()
        voters = mgr.provision_batch(n_voters, prefix=f"{prefix}voter-", concurrency=concurrency)
        metrics["provision_voters_sec"] = round(time.time() - t, 2)

        n_yes = int(round(yes_fraction * n_voters))
        n_no = int(round(no_fraction * n_voters))
        choices = ["yes"] * n_yes + ["no"] * n_no + ["abstain"] * max(0, n_voters - n_yes - n_no)
        choices = choices[:n_voters]

        vote_latencies = []
        vote_errors = []

        def _cast(client, choice):
            start = time.time()
            try:
                res = client.vote_all(choice, window_id=window_id)
                vote_latencies.append(time.time() - start)
                return res
            except Exception as e:
                vote_errors.append(str(e))
                return {"success": False, "error": str(e)}

        t = time.time()
        with concurrent.futures.ThreadPoolExecutor(max_workers=concurrency) as ex:
            list(ex.map(_cast, voters, choices))
        metrics["voting_wall_sec"] = round(time.time() - t, 2)
        metrics["vote_errors"] = vote_errors
        metrics["votes_ok"] = len(vote_latencies)
        metrics["vote_latency_p50_ms"] = round(_percentile(vote_latencies, 50) * 1000)
        metrics["vote_latency_p95_ms"] = round(_percentile(vote_latencies, 95) * 1000)
        metrics["vote_latency_max_ms"] = round(max(vote_latencies) * 1000) if vote_latencies else 0
        metrics["votes_per_sec"] = round(len(vote_latencies) / metrics["voting_wall_sec"], 1) if metrics["voting_wall_sec"] else 0

        # --- 3. Integrity verification (direct read of the audit records) ---
        Database.ensure_firebase_initialized()
        details = Database.get_window_details(window_id)
        metrics["participation_count"] = details.get("participation_count", 0)
        metrics["vote_count"] = details.get("vote_count", 0)
        tallies = Database.getWindowTallies(window_id)
        metrics["tallies_sample"] = {k: v for k, v in list(tallies.items())[:3]}
        expected_keys = {f"policy-{pid}" for pid in created_policy_ids}
        metrics["tallies_match_expected"] = all(
            tallies.get(k, {}).get("yes", 0) == n_yes and tallies.get(k, {}).get("no", 0) == n_no
            for k in expected_keys
        )

        # Double-vote check: a second ballot from any voter must be rejected
        # (the app answers 400 "already cast", which the client raises on).
        if voters:
            try:
                second = voters[0].vote_all("yes", window_id=window_id)
                metrics["double_vote_rejected"] = second.get("success") is False
            except RuntimeError as e:
                metrics["double_vote_rejected"] = "already" in str(e).lower()

        # --- 4. Promote via the real operator endpoint ---
        # Guard: the ballot is the LIVE canidate pool. If items exist that this
        # scenario did not create, promoting would move *real* canidates to
        # official on the strength of NPC votes. Skip promote in that case.
        live_keys = {item["key"] for item in operator.get_ballot_items()["items"]}
        foreign_items = live_keys - expected_keys
        if promote and foreign_items and os.environ.get("ALLOW_PROMOTE_WITH_REAL_ITEMS") != "1":
            promote = False
            metrics["promote_skipped_foreign_items"] = sorted(foreign_items)

        if promote:
            t = time.time()
            promo = operator.close_window(window_id)
            metrics["promote_sec"] = round(time.time() - t, 2)
            metrics["promote_result"] = promo.get("result", promo)

        metrics["total_sec"] = round(time.time() - t0, 2)
        return metrics

    finally:
        # Always return the site to the real ISO week.
        try:
            operator.set_window_override(None)
        except Exception:
            pass
        if cleanup:
            try:
                cleanup_scenario(window_id, created_policy_ids, prefix=prefix)
            except Exception as e:
                metrics["cleanup_error"] = str(e)


def cleanup_scenario(window_id: str, policy_ids=None, prefix: str = "npc-scale-"):
    """Remove everything a scenario created: window votes, canidate/official test
    policies, and the NPC auth users (by email prefix)."""
    _assert_safe_window(window_id)
    import Database
    from firebase_admin import db as _db
    Database.ensure_firebase_initialized()

    Database.clear_window_votes(window_id, confirm=True)
    for pid in policy_ids or []:
        _db.reference(f"policy/canidate/{pid}").delete()
        _db.reference(f"policy/official/{pid}").delete()

    mgr = NPCManager()
    deleted = mgr.delete_all_test(prefix=prefix)
    return {"window_cleared": window_id, "policies_removed": len(policy_ids or []), "npcs_deleted": deleted}
