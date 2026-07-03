# NPC Test Users & Scale Harness

This directory provides **real authenticated synthetic ("NPC") users** for testing and scale simulation of The Internet Party app.

NPCs are **full citizens**:
- Created as real Firebase Auth users (with uids)
- Log in using the *exact same* browser API flow (`/validate-token` + session cookies)
- Own private drafts, submit real ballots under their uid
- Can draft policies, propose amendments, vote, etc. via the public HTTP API

This is much more powerful than the old synthetic vote seeding (which bypassed auth).

## Quick Start

```bash
# 1. Make sure the main app is running
pipenv run python PlotterApp.py
# (or ./start_local_with_node_relay.sh)

# 2. In another terminal, run the management dashboard + server
pipenv run python -m npc.server
# Open http://localhost:5555 in your browser
```

Or use from Python:

```python
from npc.npc_manager import NPCManager

mgr = NPCManager(base_url="http://localhost:5000")

# Create 5 real NPC users
clients = mgr.provision_batch(count=5)

# Have them all vote YES on the current ballot (using a test window)
for c in clients:
    c.submit_ballot(window_id="SCALE-TEST-42", choice="yes")  # or use helpers
```

## Components

- `npc_client.py`: `NPCClient` — one user. Handles Firebase REST signin + session establishment + high level actions mirroring `static/js/*`.
- `npc_manager.py`: Batch create/list/delete + tagging.
- `server.py`: Flask dashboard on 5555 for interactive control and running scale scenarios.

## Scale Scenarios (`scenarios.py` — the real engine since 2026-07)

`run_full_cycle()` executes the whole governance loop through the production
HTTP surface and returns a metrics dict:

1. An operator NPC sets the site-wide window override to an isolated `SCALE-` window.
2. Drafters create + submit real policies (concurrent).
3. Voters each cast one immutable ballot via `/ballot-items` + `/submit-ballot` (concurrent, deterministic yes/no/abstain split).
4. Integrity checks: exact tallies, participation == votes == N, double-vote rejected.
5. Operator promotes via `/close-window`; skipped automatically if real canidate items are live.
6. Optional full cleanup (window data, scenario policies, NPC auth users) + override cleared.

Used by the dashboard button, `tests/e2e/test_governance_cycle.py` (small, always-on)
and `tests/e2e/test_scale_voting.py` (100 voters, `RUN_SCALE=1`).

Use `TARGET_BASE_URL` env var if the main app is not on 5000 (including a
deployed Render URL). Safety: non-`SCALE-`/`TEST-`/`E2E-` windows are refused
unless `ALLOW_REAL_WINDOW=1`.

## Cleanup

Everything is prefix-based (`npc-scale-`, `TEST-`, `SCALE-` windows). Use the dashboard "Cleanup" or call manager methods. Prefer test windows + the existing dev tools clear/reset endpoints.

## Notes

- NPCs use the **real** auth + API surface only. No shortcuts.
- They show up properly in `/drafts` (for their uid), `/vote`, tallies, etc.
- Great for exercising "majority of registered", participation rules, promotion logic, etc. at scale.
