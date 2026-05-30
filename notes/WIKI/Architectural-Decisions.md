# Architectural Decisions and Tradeoffs

## 1. Pure Flask `render_template_string` + No Client Build Step

**Decision**: Every page (`*Page.py`) returns a complete HTML string via `render_template_string`. There is no webpack, Vite, React, or any bundler in the main party experience. All JS is thin CDN-loaded files in `static/js/`.

**Rationale**:
- Matches the original 2024 vision and keeps the barrier to running the project extremely low (just `pipenv run python PlotterApp.py`).
- Enables the extremely fast iteration cycles that delivered the full governance engine + major UX polish in 2026-05.
- The duplicated CSS (~50-80 lines per Page) is accepted tech debt for now (see CSS-Tech-Debt.md).

**Consequences**:
- Every page is self-contained (menu, footer, base styles repeated).
- Circular navigation is maintained by hand in each file.
- Visual consistency (orange #ff6600 cards, status pills, detail headers) is achieved through copy-paste discipline rather than components.

## 2. "canidate" Spelling Is a Sacred Preserved Convention

**Decision**: The entire codebase, RTDB paths, class constants (`Policy.CANIDATE`, `Amendment.CANIDATE`), UI text, JS, docs, snapshots, and even error messages use the non-standard spelling "canidate" everywhere.

**Rationale** (from DEV_NOTES and handoffs):
- It became part of the project's identity during the long implementation.
- Renaming it would touch 100+ locations across DB, code, UI, tools, and historical artifacts.
- The cost of the rename far exceeds any aesthetic benefit.

**Rule for all future work**: Never "fix" it. If you see it in a new file or doc, keep it.

## 3. Website Operator Panel Is the Primary Surface

See the full rationale and implications in Operator-Surface.md. This was an explicit post-engine human decision.

## 4. Centralized Database.py + Thin Route Delegation

All party data mutations and complex queries live in `Database.py`. `PlotterApp.py` routes are deliberately thin (auth + JSON parsing + call helper + render Page or return JSON).

This makes the core logic:
- Testable in isolation (CLI and prefab tools prove it)
- Easy for agents to drive directly
- The single place that must be kept correct when meta-policy enforcement is added later

## 5. Additive, Audit-First Voting Records

The `voting/{window}/participation/` + `votes/{uid}/` split (instead of a single "cast vote" record that gets updated) was chosen for auditability and simplicity of "has voted" checks. Full choices are preserved forever under the window.

This design directly supports the future research use case in TheInternet (perfect labeled data for what the simulated democracy decided).

## 6. Live Canidate Pull + Re-validation on Submit (No Ballot Snapshotting)

The ballot is always the current contents of `canidate/`. On submit, every choice is re-checked against the live set.

Tradeoff: A policy that is promoted mid-voting-window disappears from in-progress ballots (acceptable in v1; future windows will be stricter).

## 7. Idempotent Firebase Initialization

`ensure_firebase_initialized()` can be called safely from the main app, every CLI command, every prefab dashboard, and agent scripts. It uses the same credential path and has graceful snapshot fallback.

This removes an entire class of "double init" warnings and "works on my machine" problems for the growing set of tools and the future simulator.

---

These decisions are the accumulated wisdom that lets the project move fast while staying coherent. Future major changes (CSS consolidation, real meta-policy enforcement, client framework adoption) should be discussed against this list.