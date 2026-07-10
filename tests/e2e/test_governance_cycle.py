"""
Full governance cycle test at small scale, through the exact production HTTP
surface (NPC harness): draft → canidate → concurrent immutable ballots →
integrity checks → operator promote → official.

This is the fidelity anchor for the scale suite: the same scenario code runs
with 100+ voters in tests/e2e/test_scale_voting.py.
"""

import pytest

from npc.scenarios import run_full_cycle


@pytest.mark.e2e
def test_full_governance_cycle_small(base_url: str, test_window_id):
    metrics = run_full_cycle(
        base_url=base_url,
        # test_window_id is already E2E-TEST-* (see conftest); do not double-prefix
        window_id=test_window_id,
        n_drafters=2,
        n_voters=5,
        concurrency=5,
        yes_fraction=0.6,   # 3 yes / 1 no / 1 abstain — deterministic
        no_fraction=0.2,
        cleanup=True,
    )

    assert metrics["policies_created"] == 2
    assert metrics["votes_ok"] == 5
    assert metrics["vote_errors"] == []
    assert metrics["participation_count"] == 5
    assert metrics["vote_count"] == 5
    assert metrics["tallies_match_expected"] is True
    assert metrics["double_vote_rejected"] is True
    # Both scenario policies won (yes > no) and were promoted — unless real
    # canidate items were live, in which case promote is deliberately skipped.
    if "promote_skipped_foreign_items" not in metrics:
        assert metrics["promote_result"]["promoted"] == 2
