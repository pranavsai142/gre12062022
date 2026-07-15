"""
MetaPolicy enforcement tests (server-side teeth, via the real HTTP surface).

- Title <= 100 chars, description <= 10,000 chars on all draft create/update routes
  (the Drafts UI already enforces client-side; these prove the server binds for
  ANY client — NPCs, curl, future apps).
- Window gating: ballots can only be cast into the effective current window.
"""

import pytest
from product_status import is_discontinued

pytestmark = [
    pytest.mark.e2e,
    pytest.mark.skipif(
        is_discontinued(),
        reason="product discontinued — e2e governance flows retired with full give-up",
    ),
]


import pytest

from tests.conftest import set_current_window_override, make_npc


def _expect_rejected(fn, *args, needle="MetaPolicy"):
    with pytest.raises(RuntimeError) as e:
        fn(*args)
    assert "400" in str(e.value)
    assert needle.lower() in str(e.value).lower()


@pytest.mark.e2e
def test_title_and_description_limits_enforced_server_side(base_url: str):
    npc = make_npc(base_url)

    long_title = "T" * 101
    _expect_rejected(npc.create_draft, long_title, "ok description", needle="100 characters")

    long_desc = "D" * 10001
    _expect_rejected(npc.create_draft, "OK Title", long_desc, needle="10,000 characters")

    # Boundary values are accepted (100 / 10,000 exactly) — and cleaned up.
    created = npc.create_draft("T" * 100, "D" * 10000)
    assert created.get("success") is True
    draft_id = created["id"]
    npc._post("/remove-draft", {"id": draft_id})


@pytest.mark.e2e
def test_ballot_rejected_for_non_current_window(base_url: str, test_window_id):
    npc = make_npc(base_url)
    policy_id = npc.draft_and_submit_policy(
        f"Gating Policy {test_window_id}", "Window gating enforcement test."
    )
    set_current_window_override(test_window_id, base_url)
    try:
        # Voting into a different (non-current) window must be rejected.
        with pytest.raises(RuntimeError) as e:
            npc.submit_ballot("2020-W01", {f"policy-{policy_id}": "yes"})
        assert "400" in str(e.value)
        assert "current window" in str(e.value).lower()

        # And the current window still accepts the one immutable ballot.
        ok = npc.submit_ballot(test_window_id, {f"policy-{policy_id}": "yes"})
        assert ok.get("success") is True
    finally:
        import Database
        Database.ensure_firebase_initialized()
        Database.db.reference(f"policy/canidate/{policy_id}").delete()
