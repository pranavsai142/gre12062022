# TESTING.md — The Internet Party

**The two testing systems for this project:**

1. **Playwright E2E** (`tests/e2e/`) — Real browser automation for UI fidelity and full critical paths.
2. **NPCs + Driver** (`npc/`) — Real Firebase-authenticated synthetic users driven via the **exact same HTTP API** the browser uses. Great for scale, volume, and multi-participant scenarios.

Use both. They complement each other.

## Quick Start

### Prerequisites
- Firebase admin credentials (same as for running the app).
- Main app running locally (recommended via the relay script for network reach).
- Dev deps + browsers:
  ```bash
  pipenv install --dev
  pipenv run playwright install chromium
  ```

### Run E2E (Playwright)
```bash
# All E2E
pipenv run pytest tests/e2e/ -q --browser chromium

# Headed (watch it)
pipenv run pytest tests/e2e/ --browser chromium --headed

# Specific
pipenv run pytest tests/e2e/test_vote_flow.py -q --browser chromium
```

The `conftest.py` starts a real threaded `PlotterApp` on a free port and gives you `page` + `base_url`. Every test gets a unique test window via the override mechanism for perfect isolation.

### Run NPC Scale Harness
```bash
# Terminal 1: main app
export DATA_FOLDER=... 
./start_local_with_node_relay.sh

# Terminal 2: NPC dashboard + driver
pipenv run python -m npc.server
# Open http://localhost:5555
```

From the dashboard you can:
- Spawn arbitrary numbers of real NPC users.
- Trigger individual or bulk actions (draft, amend, vote YES/NO/random).
- Run "full governance cycle" scale scenarios (create drafters → submit to canidate → many voters on a test window → promote → metrics).

Or from Python/CLI:
```python
from npc.npc_manager import NPCManager
m = NPCManager()
clients = m.provision_batch(25, prefix="npc-scale-", concurrency=10)
for c in clients:
    c.vote_all("yes")          # fetches /ballot-items, builds the full choices map, casts one ballot
```

### Run the Full-Cycle Scale Scenario (the flagship)

```python
from npc.scenarios import run_full_cycle
metrics = run_full_cycle(base_url="http://127.0.0.1:5000",
                         n_drafters=3, n_voters=100, concurrency=25,
                         yes_fraction=0.6, no_fraction=0.25, cleanup=True)
```

Drafters propose real policies → N voters cast concurrent immutable ballots →
integrity checks (exact tallies, double-vote rejection) → operator promote →
metrics (p50/p95 latency, votes/sec, wall time). Or as a gated pytest:

```bash
# Against local gunicorn (start the app first via the relay script)
RUN_SCALE=1 pipenv run pytest tests/e2e/test_scale_voting.py -q -s --base-url http://127.0.0.1:5000 --browser chromium

# Against a deployed Render instance
RUN_SCALE=1 TARGET_BASE_URL=https://<your-app>.onrender.com \
  pipenv run pytest tests/e2e/test_scale_voting.py -q -s --browser chromium
```

**Safety rails (2026-07):** scenarios refuse non-`SCALE-`/`TEST-`/`E2E-` windows
(override with `ALLOW_REAL_WINDOW=1`), and promotion is skipped automatically if
real (non-scenario) canidate items are live on the ballot — so a scale run can
never promote real policies by accident, even against production.

**Validated baseline (2026-07-02, local gunicorn 1 worker × 4 threads):**
100 concurrent voters completed in ~14s wall (7.3 votes/sec, p95 3.7s), 0 errors,
tallies exact, double votes rejected, promotion correct. Production config
(2 workers × 8 threads) has 4× the request parallelism.

## Recommended Workflow (When Changing Things)

1. **Before you touch code** that affects flows (routes, pages, JS, Database voting/draft logic, promotion, etc.):
   - Read `TESTING.md`
   - Run the existing E2E suite to establish baseline.

2. **While editing**:
   - Use a dedicated test window (the override on /account or via NPC harness is perfect).
   - Prefer the real API surface for NPC scale work.

3. **After the change**:
   - Run `pytest tests/e2e/` (add or update a test if the change is meaningful).
   - Exercise the affected flow with a small NPC scale run if it involves participation, tallies, or promotion.
   - Clean up (the harness has prefix-based cleanup using existing dev-tools / Database helpers).

4. **For meta-policy work** (sunset, inactivity, majority-of-registered thresholds, etc.):
   - NPCs are the right tool. You can now realistically simulate the number of registered participants needed to make the rules meaningful.

## Key Patterns & Helpers

- **Window isolation**: Always use `TEST-` or `SCALE-` prefixed window IDs + the `meta/currentWindowOverride` lever. The whole live site (including /vote public page) instantly reflects the test data.
- **Cleanup**: Prefix-based deletion of voting data + drafts/canidates created by test uids + optional Firebase Auth user deletion for NPCs.
- **Auth for NPCs**: Real users via Firebase Admin + REST signin + `/validate-token`. This means drafts appear in the real `/drafts` for that uid, votes are real `participation/{uid}` records, etc.
- **Playwright specifics**: Uses `page`, `expect`, storage state where helpful. Tests exercise the actual rendered HTML/JS (diff colors, defaulted radios, conditional result boxes, etc.).
- **No new backdoors**: Everything goes through the public endpoints the browser already uses.

## When to Add / Extend Tests

- Any new public flow or significant change to an existing one.
- Anything touching the governance engine (draft → canidate, ballot recording, promotion).
- Operator surface changes.
- New constraints (length limits, categories, etc.).

Add the test in the same style as existing ones in `tests/e2e/`. Keep tests small, focused, and easy to read/modify.

For scale/regression around "many users": add a scenario in the NPC harness or a lightweight scale test.

## File Layout (After the 2026-07-02 production-readiness delivery)

```
tests/
  conftest.py          # live server + playwright fixtures + make_npc + auto NPC cleanup
  e2e/
    test_smoke.py               # navigation basics
    test_vote_flow.py           # real browser login → abstain default → cast → immutable
    test_governance_cycle.py    # full cycle via NPC harness (small, always-on)
    test_meta_enforcement.py    # server-side char limits + window gating
    test_scale_voting.py        # 100 concurrent voters (gated by RUN_SCALE=1)
  README.md

npc/
  npc_client.py        # the actor that speaks the real API (auth, drafts, /ballot-items, votes)
  npc_manager.py       # concurrent batch create / batch delete
  scenarios.py         # run_full_cycle + cleanup_scenario (shared by dashboard + tests)
  server.py            # dashboard + scenario runner on :5555
  README.md

pytest.ini
.github/workflows/ci.yml  # compile check always; full E2E once FIREBASE_SERVICE_ACCOUNT secret is set
TESTING.md             # this file
```

## Notes

- The harness is completely optional at runtime. Production deploys do not need pytest or playwright.
- All test/synthetic data should be clearly tagged (emails, window ids, custom claims) so accidental pollution of real data is obvious and easy to clean.
- This infrastructure was built precisely so future work on the "rules that bite" (char limits today, sunsets + participation thresholds later) can be developed with confidence.

See also:
- `notes/GROK/handoffs/2026-06-21-playwright-npc-testing-scale-harness.md`
- `npc/README.md`
- `tests/README.md`
