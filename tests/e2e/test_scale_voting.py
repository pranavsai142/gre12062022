"""
Scale validation: 100 real NPC users cast concurrent immutable ballots through
the production HTTP surface (gunicorn path), with integrity + latency metrics.

Not part of the default suite (slow + creates 100 Firebase Auth users).

Run against the local gunicorn/relay:
    RUN_SCALE=1 pipenv run pytest tests/e2e/test_scale_voting.py -q -s

Run against a deployed Render instance (safe: SCALE- window isolation +
foreign-item promote guard still apply):
    RUN_SCALE=1 TARGET_BASE_URL=https://your-app.onrender.com \
        pipenv run pytest tests/e2e/test_scale_voting.py -q -s
"""

import os
import json
import pytest

from npc.scenarios import run_full_cycle

RUN_SCALE = os.environ.get("RUN_SCALE") == "1"


@pytest.mark.scale
@pytest.mark.skipif(not RUN_SCALE, reason="set RUN_SCALE=1 to run the 100-user scale scenario")
def test_100_concurrent_voters_full_cycle():
    base_url = os.environ.get("TARGET_BASE_URL", "http://127.0.0.1:5000")

    metrics = run_full_cycle(
        base_url=base_url,
        window_id=None,          # unique SCALE-TEST-<ts>
        n_drafters=3,
        n_voters=100,
        concurrency=25,
        yes_fraction=0.6,        # 60 yes / 25 no / 15 abstain
        no_fraction=0.25,
        cleanup=True,
    )
    print("\nSCALE METRICS:\n" + json.dumps(metrics, indent=2))

    # Every voter got exactly one immutable ballot recorded
    assert metrics["votes_ok"] == 100
    assert metrics["vote_errors"] == []
    assert metrics["participation_count"] == 100
    assert metrics["vote_count"] == 100
    # Tallies are exactly the deterministic split on every scenario policy
    assert metrics["tallies_match_expected"] is True
    assert metrics["double_vote_rejected"] is True
    # Throughput sanity: the whole electorate must finish within the window
    assert metrics["voting_wall_sec"] < 120
