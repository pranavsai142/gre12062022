# Agent Action Surface — How External Agents Drive the Party

This chapter is especially important for TheInternet simulator / dojo work. The goal is a faithful action surface so that learned agent behavior is meaningful for the real system.

## The Concrete Actions Agents Must Be Able to Perform

These map 1:1 to the real governance engine (the north star requirement):

1. **Create a draft policy or amendment**
   - POST to the draft endpoints (or direct `Database.createDraftPolicy` / `createDraftAmendment`).
   - Must supply title + description (subject to future char-limit enforcement).
   - Returns the new id; the draft is private to the agent's `userId`.

2. **Submit a draft to the canidate ballot**
   - `submitDraftPolicy(user, policyId)` or equivalent HTTP flow.
   - Ownership + validation enforced.
   - Moves the item into the live pool that will appear on the next ballot.

3. **Propose an amendment to an existing policy**
   - Same draft → submit flow, but the amendment carries a `policyId` target.
   - Agents (and humans) discover targets via the Congressional Library or detail pages.

4. **Vote on the current ballot**
   - The critical action: `recordUserBallot(user, windowId, choicesDict)`.
   - The backend will:
     - Enforce one-vote-per-window.
     - Re-validate every choice against the live canidate set.
     - Default any missing/untouched items to ABSTAIN.
   - This is the action whose outcomes (via promotion) affect the simulated world.

5. **(Operator role) Close window and promote winners**
   - `promoteWinnersFromWindow(windowId)`.
   - Agents playing "steward" or "operator" roles can trigger this to advance the simulation.
   - Winners move to `official/`, effects are applied in the world model.

## How to Drive These Actions (Three Equivalent Paths)

All three paths ultimately call the same Database helpers:

- **HTTP surfaces** (what a browser-based agent or the real frontend would use) — the various `/draft`, `/submit-draft`, `/submit-ballot`, `/close-window`, `/dev-tools/*` routes in PlotterApp.py.
- **Direct Python** (best for simulation inside the same process or via the CLI) — import `Database` after calling `ensure_firebase_initialized()`.
- **CLI / Prefab** — thin wrappers around the above for convenience in scripts and visual debugging.

## Critical Patterns for Simulation Fidelity

- **Window isolation**: Use synthetic window IDs (e.g. "2026-EPISODE-007") + the `currentWindowOverride` mechanism so episodes don't bleed into each other or real data.
- **Deterministic seeding**: The `seed_synthetic_choice_votes` family of helpers lets you create known electorates (e.g., "70% yes on this policy") before an agent episode runs.
- **Cleanup**: `reset_user_votes` or `clear_window_votes` (with extreme caution) between episodes.
- **Observation**: After promotion, read `getOfficialPolicies()` / `getOfficialAmendments()` and the full vote records under the window for reward calculation and audit.
- **Auth**: Agents need valid Firebase Auth identities (or synthetic uids that the system accepts in dev mode). The participation/vote records will store whatever uid/email you supply.

## Recommended Mental Model

An agent in TheInternet is not "simulating a user of some abstract democracy."

It is a real (synthetic) registered member of **this exact Party**, with a real uid, performing the exact same state transitions that a human member performs on the live site.

If the agent's learned policy produces better long-term societal metrics in the simulator when it participates this way, that is strong evidence that the same participation pattern would be beneficial if real humans adopted it — or that the meta-rules need adjustment.

## Future Tightening (for the dojo)

- Once char-limit enforcement lands, agents must respect (or learn to respect) the same limits.
- Once true sunset / inactivity / majority-of-registered rules are implemented, the simulator must mirror them exactly.
- The action space for agents should be enumerated in one place (probably a small `agent_actions.py` or similar) that both the real Party surfaces and the simulator import.

---

*Keeping this surface faithful is the single most important interface contract between the production Party and the research simulator.*