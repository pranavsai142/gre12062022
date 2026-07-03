# Session Handoff — 2026-06-21 (Playwright E2E Testing + NPC Scale Harness)

**Project:** The Internet Party (Party No. 3)  
**Session Type:** Major infrastructure delivery — automated testing + synthetic user system for scale  
**Started with:** Approved plan from plan mode + /parallel-implement execution of the bundles

---

## What Was Accomplished

Delivered a complete, production-grade automated testing + NPC simulation system for the live governance application.

### 1. Playwright E2E Test Suite (`tests/`)
- Full coverage of critical user flows using real browser automation:
  - Auth (register with name/email/password + token exchange + redirect)
  - Drafting + submitting policies and amendments (to canidate)
  - Congressional Library browsing + Amendment detail with real visual diff (green/red)
  - Voting page: ballot rendering, **Abstain as safe default**, submit-ballot (once per window), "already voted" state, live tallies
  - Operator actions on `/account` (window override, promote)
  - Complete end-to-end governance cycle tests (draft → canidate → vote window → promote → verify in official + history)
- Infrastructure:
  - `tests/conftest.py`: live threaded Flask server fixture (starts real `PlotterApp` on free port), Playwright integration, test window helpers, prefix-based cleanup for `TEST-` / `SCALE-` windows + synthetic data.
  - Easy to run: `pipenv run pytest tests/e2e/ --browser chromium` (or `--headed`).
- All tests are **modifiable** (constants in conftest, clear structure).

### 2. NPC Synthetic Users ("real test users") + Driver
- `npc/npc_client.py`: `NPCClient` that creates **real** Firebase Auth users and then drives the application using the **exact same HTTP surface the browser uses**:
  - Firebase REST signup/signin (using the public web API key)
  - `POST /validate-token` to get real Flask session cookies
  - Identical JSON POSTs as `static/js/` for `/create-draft`, `/submit-draft`, `/create-draft-amendment`, `/submit-ballot`, etc.
- `npc/npc_manager.py`: `NPCManager` for batch provisioning (`provision_batch`), listing, and safe deletion of test NPCs. Tags with synthetic/npc metadata. NPCs own real private drafts and cast real ballots.
- These are not fake DB records — they are full participants.

### 3. Little Python Server + Dashboard for Management & Scale
- `npc/server.py` (runs on port 5555 by default):
  - Web dashboard (orange card aesthetic) to arbitrarily create N NPCs, trigger actions (draft policy, propose amendment, vote), run bulk operations.
  - Scale scenarios + "full governance cycle" runner (N drafters + M voters on a dedicated test window override → submit → promote → report metrics: participation, timings, promoted count).
  - Uses `concurrent.futures` for realistic parallel action.
  - Can target the main app via `TARGET_BASE_URL`.
- CLI runnable: `pipenv run python npc/server.py`

### 4. Documentation & Reference Material (easy to use going forward)
- `tests/README.md` — how to run E2E, structure, how to extend.
- `npc/README.md` — how to use NPCClient, NPCManager, the dashboard, and scale patterns.
- **Root `TESTING.md`** — the single reference page for "how do I incorporate testing when I edit/add features to the web app?":
  - Two systems explained (Playwright for fidelity, NPCs for scale/multi-user).
  - Recommended workflow when making changes.
  - "Always add a test" guidance + concrete patterns (test windows, markers, combining both systems).

All work followed project rules: "canidate" preserved, no unnecessary changes to core (PlotterApp/Database), website remains primary surface, small focused verifiable increments, heavy use of `todo_write` inside the parallel implementers.

## Key Decisions & Hard-Won Lessons
- **Hybrid approach is powerful**: Playwright for UI-correctness and full flows (including JS-rendered diffs, form behavior, abstain defaults). Pure API NPCs (via exact browser comms) for scale and volume without the cost of many browsers.
- Test isolation via the existing `meta/currentWindowOverride` + `TEST-`/`SCALE-` prefixes + auto cleanup is extremely effective (lets you point the entire live site at throwaway data).
- Parallel implementation (5 bundles) delivered fast but created some duplication (two server files, overlapping client work). Lesson: when using parallel agents, define clearer file ownership up front.
- Making NPCs use the *real* auth + API (instead of direct DB writes) gives much higher confidence that scale tests reflect production behavior.
- `TESTING.md` + per-component READMEs are the durable way to make the new capability actually get used on future work.

## Current State
- You can run a full Playwright suite that exercises the governance engine end-to-end.
- You can spin up fleets of real NPC users from code or a dashboard and have them draft, amend, and vote at scale.
- You have clear docs (`TESTING.md` is the entry point) so future technical edits, overhauls, or feature additions have a low-friction path to add regression protection and scale validation.
- The testing layer is opt-in for development (does not affect the main runtime).

## Forward Direction / How to Use Going Forward
- Before/after any non-trivial change to routes, pages, JS, Database logic, or governance rules: run the E2E suite and consider adding a test.
- When you need "what happens with 30 voters?" or "can we reach promotion thresholds?": use the NPC harness.
- Consult `TESTING.md` first when starting new work. It tells you exactly where and how to add coverage.
- The infrastructure is ready for future meta-policy work (sunsets, inactivity, registered-majority thresholds) — you can now simulate the participant counts and histories those rules will need.

See the created `TESTING.md`, `tests/README.md`, and `npc/README.md` for concrete commands and patterns.

---

**Files & Artifacts of Note (this session)**
- New: `tests/README.md`, `npc/README.md`, `TESTING.md`
- Harness: `tests/conftest.py` + `tests/e2e/*`, `npc/npc_client.py`, `npc/npc_manager.py`, `npc/server.py`, `npc/templates/dashboard.html`
- Supporting: updates to support clean execution (minor manager alignment, etc.)

This session turned "we test by clicking and seeding fake votes" into a proper automated + scalable testing capability.

*Written as part of the `/done` ritual on 2026-06-21.*
