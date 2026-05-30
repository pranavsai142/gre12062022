# Operator & Dev Surface — The Primary Control Plane

**Critical convention (reinforced in every 2026-05 handoff and DEV_NOTES):** The live website itself (`/account` after login) is the canonical, real-time operator and dev tools surface. Everything else (CLI, prefab dashboards) is excellent secondary tooling.

## Why the Website Became Primary

The human was explicit: "just open the site and do it." Having to remember CLI commands or launch separate dashboards broke the desired flow for real-time control and demos. After the governance engine landed, the `/account` page was given a full-featured Operator & Dev Tools panel that can:
- Inspect the current window, live tallies, participation count
- Set an arbitrary `currentWindowOverride` (affects the entire public site instantly, including `/vote`)
- Seed deterministic test votes (famous "3 YES / 5 NO / 10 ABSTAIN" buttons + fully synthetic per-choice seeds)
- Clear a window's votes (nuclear option, guarded)
- Reset a specific user's votes
- Trigger promotion
- Refresh views

All of these call the exact same Database.py helpers that the public voting flow and the CLI/prefab tools use.

## Where the Operator Panel Lives

- `AccountPage.py` — renders the full panel (current window snapshot + all the action cards + result boxes).
- Thin JS in the page (or shared) handles the Set/Clear window, seed buttons, etc.
- Result boxes are **conditional** (only appear when they have real content — a hard-won polish lesson).

## The Three Surfaces (all equivalent under the hood)

1. **Website Operator Panel** (`/account`) — primary, real-time, what the human wants to use day-to-day.
2. **CLI** (`python -m dev_tools.cli`) — agent-first, scriptable, excellent for reproducible simulation episodes.
3. **Prefab dashboards** (`admin/admin_console.py` and `dev_tools/dev_dashboard.py`) — visual god-view tables + action cards. Still point back to the website as the blessed surface.

All three share `Database.py` + the same `ensure_firebase_initialized` path + snapshot fallback for when the private service account JSON is absent.

## Key Operator Endpoints (PlotterApp.py)

- `/dev-tools/*` family (seed, clear, reset-user, set-window, etc.)
- `/close-window` (the promote action, also callable from the public Vote page when privileged)
- `/submit-ballot` (used by both normal users and seeded test ballots)

## For Agents and Simulation (TheInternet)

When training or evaluating agents:
- Use the CLI or direct Database helper calls for reproducible setup/teardown of windows.
- Use the website override mechanism (or pass explicit `windowId`) so agent episodes are isolated.
- After promotion, read the resulting `official/` state to compute world-model effects and reward.
- The deterministic seed helpers (`seed_synthetic_choice_votes` etc.) are perfect for creating known-good or known-bad electorates to test against.

Never treat the CLI or prefab as "the" operator surface in docs or mental models — the website panel is the one the project has declared primary.

---

*This decision (website as primary) is one of the most important high-level architectural choices made after the core engine was delivered. It must be respected.*