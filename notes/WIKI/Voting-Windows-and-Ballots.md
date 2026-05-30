# Voting Windows and the Ballot Engine

The voting system is deliberately simple, additive, and audit-friendly. One immutable ballot per registered user per ISO-week window.

## Window Identification

- **Normal operation**: `getCurrentVotingWindowId()` in Database.py returns `f"{year}-W{week:02d}"` from `datetime.now().isocalendar()`.
- **The powerful override lever** (added 2026-05-22): `meta/currentWindowOverride` in RTDB.
  - If present and non-empty, it completely replaces the real ISO week for the *entire site* (public `/vote`, tallies, Account panel, operator tools, everything).
  - Set/Clear via the Operator panel on `/account` (or `/dev-tools/set-window` endpoint).
  - This is dramatically more useful for testing and agent simulation than any parameter-only tool.

See Database.py:22-52 for the exact precedence logic.

## Core Invariants

1. **One immutable vote per user per window**
   - Enforced by the presence of `voting/{windowId}/participation/{uid}`.
   - `hasUserVotedInWindow` is the cheap guard.
   - Once recorded, the choices in `voting/{windowId}/votes/{uid}` are never mutated.

2. **Full audit record**
   - `participation/` record = "this user voted in this window" (timestamp + email).
   - `votes/{uid}/` = the complete `choices` dict + `submitted_at`.
   - This separation makes tallies + "who voted" queries cheap while preserving the full ballot for audits.

3. **Live ballot, live re-validation on submit**
   - The ballot is always the current contents of `canidate/` (policies + amendments).
   - `recordUserBallot` (Database.py:445) re-validates every submitted choice against the live set before writing. This prevents stale ballots from corrupting results.

4. **Abstain as the safe default (post 05-22 polish)**
   - In `recordUserBallot:474-481`:
     ```python
     for itemKey in liveKeys:
         choice = submitted.get(itemKey)
         if choice in (VOTE_YES, VOTE_NO, VOTE_ABSTAIN):
             cleanedChoices[itemKey] = choice
         else:
             cleanedChoices[itemKey] = VOTE_ABSTAIN
     ```
   - This satisfies the "every member must vote on every item" rule with almost zero friction for the voter. Untouched ballot submission = valid all-abstain ballot.

## Ballot Object (Ballot.py)

- Presentation helper that templates consume.
- Two construction paths:
  - Fresh ballot (no prior vote) → all items, no userChoices.
  - Already voted → loads prior choices so the page can show "You voted Yes / No / Abstain" in a read-only view.
- Also carries the `windowId` so the UI and submission know exactly which window they are acting on.

## Promotion & Tallies

- `getWindowTallies(windowId)` → `Vote.computeTallies(rawVotes)`
- `promoteWinnersFromWindow` (Database.py:531) calls `Vote.getWinners(tallies, minYes=1)`
- Current rule (simple MVP): `yes > no && yes >= 1`
- Winners are copied to `official/` with `enacted` timestamp and removed from `canidate/`.
- Non-winners remain in `canidate/` (they can be re-voted on in a future window or manually cleaned by operators).

## Operator Levers (see Operator-Surface.md for the full UI)

- View current window + live tallies + participation count.
- Arbitrary `currentWindowOverride` (affects the whole public site instantly).
- Seed deterministic batches (3 YES / 5 NO / 10 ABSTAIN, or fully synthetic per-choice).
- Clear a window's votes (nuclear, guarded).
- Per-user vote reset.
- Promote button (calls the same function the public Vote page uses).

## For Agent / Simulation Work

When building TheInternet dojo:
- Agents must be able to set a specific test `windowId` (or use the override) so multiple simulation episodes don't collide.
- The `recordUserBallot` path (or the equivalent POST) is the canonical way for an agent to "cast a vote".
- After promotion, the simulator can read `policy/official/` and `amendment/official/` to apply effects to the world model.
- The full vote records under `voting/{window}/votes/` give perfect ground truth for what the "democracy" decided in that episode.

---

*This subsystem is the mechanical heart that makes the parallel party real. Treat the immutability and audit records as sacred.*