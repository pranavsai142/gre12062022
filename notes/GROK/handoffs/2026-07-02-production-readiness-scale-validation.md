# Session Handoff — 2026-07-02 — Production Readiness + Scale Validation

**Project:** The Internet Party (Party No. 3)
**Session Type:** Production hardening push (runtime, MetaPolicy enforcement, harness maturation, 100-user scale validation, Render deploy framework)
**Started with:** Full `/init` (SOUL_DRIVER, DEV_NOTES, both 2026-07-02 handoffs, the 2026-06-21 testing handoff, WIKI chapters, TESTING.md, all runtime + mechanics sources)

## What Was Accomplished

### Phase 1 — Runtime hardening (PlotterApp.py, Database.py, start.sh, render.yaml)
- **Fixed the multi-worker session bug**: `app.secret_key = os.urandom(12).hex()` regenerated per process, so with `--workers 2` on Render each worker rejected the other's session cookies (random logouts). Now: `SECRET_KEY` env var, falling back to a deterministic SHA-256 of the private service-account file (stable, secret, not in repo), falling back to random only for single-process dev.
- **Centralized Firebase init**: PlotterApp now uses `Database.ensure_firebase_initialized()` (which also recognizes an app initialized elsewhere via `firebase_admin._apps`) and raises a clear RuntimeError at startup if the cert is missing, instead of crashing cryptically or 500ing every request. Added `Database.get_service_account_path()` as the single path rule.
- **`/healthz` endpoint**: shallow by default, `?deep=1` verifies RTDB connectivity. Wired as `healthCheckPath` in render.yaml.
- **`start.sh` rewritten for Render reality**: `exec`s gunicorn in the **foreground** (the old script backgrounded it — Render would treat the exited script as a crash), logs to stdout/stderr for the Render stream, and is env-tunable (`WEB_CONCURRENCY`=2, `GUNICORN_THREADS`=8 — requests are RTDB-I/O-bound — `GUNICORN_TIMEOUT`, `PORT`). SSH users can `nohup ./start.sh &`.
- **`render.yaml` blueprint added**: python runtime, `./start.sh` start command, `/healthz` health check, auto-generated `SECRET_KEY`, `DATA_FOLDER=/etc/secrets/` (Render Secret Files mount). **One manual step remains**: connect the repo as a Blueprint and upload the admin JSON as a Secret File named `theinternetparty-5b902-firebase-adminsdk-qlzzx-3864b82b40.json`.
- **Auth robustness**: `verify_id_token(..., clock_skew_seconds=10)` (freshly minted tokens intermittently failed as "used too early" — found live during NPC provisioning); `/validate-token` now catches all exceptions → 401 (firebase-admin raises `InvalidIdTokenError`, which is NOT a ValueError; bad tokens were becoming 500s).
- Untracked `.DS_Store`.

### Phase 2 — NPC/E2E harness matured from scaffolding to real
- **`npc/server.py` was broken at import** (`from flask import render_string` — doesn't exist). Fixed; dashboard now runs the real full-cycle scenario with metrics output.
- **`npc/npc_client.py` payload keys were wrong** (`draft_id`/`target_policy_id` vs the real `id`/`policyId` the routes + DraftsPage JS use). All actions now mirror the browser exactly. `vote_all()` is real (was a placeholder): fetches the live ballot, builds the full choices map, casts one immutable ballot. Added `draft_and_submit_policy`, `close_window`, `set_window_override`, signin retry.
- **Additive API surface**: `/create-draft` and `/create-draft-amendment` now return the new `id` (browser ignores it; NPCs need it to chain). New public read-only **`/ballot-items`** JSON route (same data /vote renders, respects the override) so pure-HTTP clients can discover the ballot — this is what makes NPC runs against a remote Render URL work without scraping.
- **New `npc/scenarios.py`** — the shared engine: `run_full_cycle()` (operator NPC sets override → concurrent drafters → concurrent voters with deterministic yes/no/abstain split → integrity checks → promote → metrics) and `cleanup_scenario()`. Safety rails: refuses non-`SCALE-`/`TEST-`/`E2E-` windows without `ALLOW_REAL_WINDOW=1`; **skips promotion if real (non-scenario) canidate items are live on the ballot** — an NPC electorate can never promote real policies by accident.
- **`npc/npc_manager.py`**: concurrent provisioning (fleet wall-time), batch Auth deletion via `delete_users` (the one-by-one loop was unusable post-100-NPC runs).
- **E2E suite completed** (was 2 files, one placeholder): `test_vote_flow.py` now drives the REAL browser flow (login form → abstain default checked → vote YES → confirm dialogs → "You voted: YES" immutable state); new `test_governance_cycle.py` (always-on small full cycle) and `test_scale_voting.py` (100 voters, gated by `RUN_SCALE=1`). Fixed conftest: `base_url` session-scope (pytest-base-url ScopeMismatch), `sys.path parents[1]` bug, window cleanup actually passes `confirm=True`, override cleared on teardown, `make_npc` helper, autouse session fixture deletes `npc-e2e-*` Auth users.

### Phase 3 — First MetaPolicies now bind
- **Server-side char limits** on all four draft create/update routes (policy + amendment): title ≤100, description ≤10,000, clear per-field error messages with the actual length. UI already had counters + maxlength; the server is now the teeth for any client.
- **Window gating on `/submit-ballot`**: a ballot whose `windowId` differs from the effective current window (real ISO week or operator override) is rejected with a refresh hint. This closes a real integrity hole — "one immutable vote per window" was bypassable by POSTing arbitrary windowIds.
- Covered by `tests/e2e/test_meta_enforcement.py` (limits incl. boundary values, gating incl. the current window still accepting the one ballot).

### Phase 4 — Scale validation + Render readiness
- **100-concurrent-voter full cycle PASSED** against local gunicorn via the relay (the real production request path): 100/100 ballots, 0 errors, exact 60/25/15 tallies on all 3 scenario policies, double-vote rejected, 3 promotions correct, ~13.7s voting wall time (7.3 votes/sec, p50 3.3s / p95 3.7s) — on the LOCAL 1-worker × 4-thread config. Production (2×8) has 4× the parallelism. 100-concurrent on Render: comfortable.
- **10k path documented** (DEV_NOTES backlog + render.yaml comments): raise instance count (Render autoscaling), reduce per-request RTDB chattiness (VotePage does several reads per render — cache/batch), then sharding. The harness is the measuring tool (`run_full_cycle` at higher N against `TARGET_BASE_URL`).
- **CI skeleton** `.github/workflows/ci.yml`: compile job (no secrets), full E2E job that activates once the `FIREBASE_SERVICE_ACCOUNT` secret is added.
- **Cleaned June harness residue from the shared RTDB/Auth** (inspect-then-delete, convention-tagged only): 7 synthetic "NPC Policy …" official items, 5 `NPC-SCALE-*` windows, 27 leftover NPC auth users. Human-created test entries were left alone. DB now: 3 windows (2026-W21/W25/W99), 13 official items, all human.

### Phase 5 — Operator auth alignment
- Optional **`OPERATOR_EMAILS`** allowlist (comma-separated) on all operator endpoints (`/close-window`, `/dev-tools/seed|clear|promote|reset-user|set-window`): logged-in non-operators get 403. **Unset = v1 behavior (any logged-in member)** so nothing changes until configured on Render.

## Verification Performed (all on the live app via the canonical relay script)
- `pipenv run pytest tests/e2e/ -q --browser chromium --base-url http://127.0.0.1:5000` → **6 passed** (smoke, public ballot preview, full browser vote flow, governance cycle, both enforcement tests), scale test correctly gated.
- `RUN_SCALE=1 … test_scale_voting.py` → **1 passed** with the metrics above.
- `/healthz` + `/healthz?deep=1` return ok; home//vote//policy 200; `/ballot-items` correct.
- Deterministic secret key verified identical across processes; operator allowlist logic unit-verified (case-insensitive, default-open).
- Post-run residue checks: scenario cleanup restored windows/canidate/Auth to pre-run state.

## Contracts Preserved
"canidate" everywhere (incl. all new code/tests/docs); render_template_string no-build architecture (zero page changes except none needed — UI counters already existed); website `/account` operator panel remains primary (NPC operator actions call the same endpoints it uses); one immutable vote per window (now *stronger* via gating); all mutations through Database.py helpers.

## Open Questions / Remaining Manual Steps
1. **Connect Render** (Blueprint from render.yaml + Secret File upload + optionally set `OPERATOR_EMAILS`). Then run the targeted scale test against the live URL:
   `RUN_SCALE=1 TARGET_BASE_URL=https://<app>.onrender.com pipenv run pytest tests/e2e/test_scale_voting.py -q -s --browser chromium`
2. Add the `FIREBASE_SERVICE_ACCOUNT` GitHub secret to activate the CI E2E job.
3. Decide when to flip `OPERATOR_EMAILS` on (it will hide nothing in the UI — non-operators just get 403 on operator actions).

## For the Next Session
- Start with `/init`; this handoff + DEV_NOTES are current.
- **The testing layer is the delivery gate**: run the 6-test E2E suite (~30s) before/after changes; use `npc/scenarios.run_full_cycle` for anything touching participation/tallies/promotion. TESTING.md is the entry point and is up to date.
- Natural next increments: Render connection + live-URL scale run, then categories/tags or the deeper MetaPolicy rules (sunsets, inactivity, majority-of-registered — the harness can now simulate those electorates).

*Handoff created as part of `/done` on 2026-07-02.*
