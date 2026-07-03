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

## Scale Scenarios

The server and manager support full-cycle runs:
- Point site at a dedicated test window (via operator panel or direct).
- Spawn drafters → they submit policies/amendments.
- Spawn voters → they cast ballots.
- Promote.
- Report participation, timings, winners.

Use `TARGET_BASE_URL` env var if the main app is not on 5000.

## Cleanup

Everything is prefix-based (`npc-scale-`, `TEST-`, `SCALE-` windows). Use the dashboard "Cleanup" or call manager methods. Prefer test windows + the existing dev tools clear/reset endpoints.

## Notes

- NPCs use the **real** auth + API surface only. No shortcuts.
- They show up properly in `/drafts` (for their uid), `/vote`, tallies, etc.
- Great for exercising "majority of registered", participation rules, promotion logic, etc. at scale.
