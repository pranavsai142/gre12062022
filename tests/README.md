# Playwright E2E Testing for The Internet Party

This directory contains automated end-to-end tests using **pytest + Playwright**.

The tests exercise the **real full user flows** of the application (register → draft → submit to canidate → vote → promote → see results) by driving the actual Flask-rendered pages and JavaScript.

## Why This Matters

- Catches regressions when you edit pages, JS, Database logic, or governance rules.
- Provides living documentation of the expected behavior.
- Supports **scale testing** via the companion `npc/` harness (real authenticated test users).
- Easy to extend when you add new features.

## Quick Start

```bash
# Install (once)
pipenv install --dev
pipenv run playwright install chromium

# Run everything (starts the app automatically via live server fixture)
pipenv run pytest tests/e2e/ --browser chromium -q

# Headed (watch it run in a real browser)
pipenv run pytest tests/e2e/ --browser chromium --headed

# Specific test file
pipenv run pytest tests/e2e/test_smoke.py --browser chromium
```

The tests will automatically start a live instance of `PlotterApp` on a random port for isolation.

## Test Structure

- `tests/conftest.py` — Core test foundation:
  - `live_server` fixture: starts real `PlotterApp` in a background thread.
  - `base_url`, `page`, `context` fixtures.
  - `set_current_window_override` / cleanup helpers.
  - Auto-cleanup for `TEST-` and `SCALE-` windows + synthetic data.
- `tests/e2e/` — Actual test cases:
  - `test_smoke.py` — Basic navigation.
  - `test_auth_flows.py` — Register + login.
  - `test_drafts_library_amendments.py` — Drafting + submitting policies/amendments + visual diff.
  - `test_vote_operator_governance.py` + `test_governance_flow.py` — Full ballot + operator promote flows.

## Key Concepts for Writing/Extending Tests

### Isolation with Test Windows
```python
def test_something(page, base_url, test_window_id):
    # Force the entire live app (including /vote) to use this window
    from tests.conftest import set_current_window_override
    set_current_window_override(test_window_id)

    # ... do your test ...

    # Cleanup happens automatically for marked tests
```

Use unique windows so tests don't interfere with each other or real data.

### Modifiable Test Constants
Edit these in `tests/conftest.py`:

```python
TEST_BASE_EMAIL_DOMAIN = "e2e-test.theinternetparty.local"
TEST_DEFAULT_PASSWORD = "E2E_Test_Pass_123!"
TEST_WINDOW_PREFIX = "E2E-TEST"
```

### Running Against an Already-Started App
```bash
pipenv run pytest tests/e2e/ --base-url http://localhost:5000 --browser chromium
```

### Markers
- `@pytest.mark.e2e` — standard browser tests
- `@pytest.mark.scale` — tests that may be slower or use many NPCs

## Incorporating Testing Into New Work

**Golden rule:** When you make a meaningful change to the web application, add or update an E2E test.

Typical flow when adding a feature:

1. Implement the backend/frontend change.
2. Add a new test (or extend an existing one) that exercises the new behavior via real UI.
3. Run the suite.
4. For multi-user or load aspects, also add a scale scenario using the `npc/` tools.
