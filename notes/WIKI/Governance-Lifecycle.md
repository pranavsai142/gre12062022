# Governance Lifecycle — Draft → Canidate → Ballot → Vote → Promote

**Core mental model for the entire project.** This is the implemented state machine that realizes the Party No. 3 vision (with some MVP simplifications).

## The Implemented State Machine (2026-05)

```
Private (user)          Public / Ballot                     Official Platform
┌─────────────┐     submitDraft*()      ┌──────────────┐     promoteWinners()
│   DRAFT     │ ─────────────────────▶  │   CANIDATE   │ ─────────────────────▶  │   OFFICIAL   │
│ (per user)  │                         │  (live pool) │                         │  (enacted)   │
└─────────────┘                         └──────────────┘                         └──────────────┘
      ▲                                       │                                        │
      │                                       │ getBallotItems()                       │ (winners only)
      └───────────────────────────────────────┴────────────────────────────────────────┘
                              (non-winners stay in canidate for future windows)
```

### Transitions (with exact code anchors)

1. **Draft Creation / Edit**
   - `createDraftPolicy` / `createDraftAmendment` (Database.py:259+)
   - Private under `policy/draft/{id}` or `amendment/draft/{id}`, keyed by `userId`.
   - Full ownership + validation in the Page + Database helpers.

2. **Submit Draft → Canidate** (the "propose" step)
   - `submitDraftPolicy(user, policyId)` (Database.py:290)
   - `submitDraftAmendment(user, amendmentId)` (Database.py:337)
   - Checks ownership via `getDraft*` + `validateForSubmission(userId)`.
   - Copies the record to `canidate/`, deletes from `draft/`, sets `submitted` timestamp.
   - Now visible to everyone on the ballot and in the Congressional Library.

3. **Ballot Formation** (live, no snapshotting)
   - `getBallotItems()` (Database.py:393) = all current `canidate/` policies + amendments.
   - Always live pull on every render and every vote submission (integrity via re-validation in `recordUserBallot`).

4. **Voting (per ISO-week window)**
   - See [Voting-Windows-and-Ballots.md](Voting-Windows-and-Ballots.md) for the full immutability + audit story.
   - One ballot per user per `windowId` (enforced by participation record).
   - `recordUserBallot` (Database.py:445) performs live re-validation of every choice against current canidates, defaults missing to ABSTAIN, writes both `participation/` and `votes/{uid}/choices`.

5. **Close Window + Promote Winners** (manual operator action in v1)
   - `promoteWinnersFromWindow(windowId)` (Database.py:531)
   - Computes tallies via `Vote.computeTallies` + `Vote.getWinners(tallies, minYes=1)`
   - Rule (from Vote.py): `yes > no && yes >= 1`
   - For each winner:
     - Copy to `official/` (set `type`, `submitted`, `enacted` timestamps)
     - Delete from `canidate/`
   - Losers remain in `canidate/` (eligible for future windows or re-proposal).
   - Called from:
     - Public Vote page "Close Window & Promote" (when logged in as operator)
     - `/close-window` route (PlotterApp.py)
     - Operator panel buttons on `/account`
     - CLI: `python -m dev_tools.cli promote ...`
     - Prefab consoles

### Amendment Special Handling

Amendments are first-class citizens on the ballot but carry a `policyId` foreign key.

On the Amendment Detail page (`DetailAmendmentPage.py`):
- Clean "Targets Policy" box (lean after 05-22 polish).
- Real visual diff (title + description) using `difflib.SequenceMatcher`.
- Green/red highlighting, "Title unchanged." / "Description unchanged." messages when only one side differs.
- Long-text hardening (`word-wrap: break-word; white-space: pre-wrap`).

Policy Detail pages now surface:
- "Pending Candidate Amendments" section (live links to amendment detail).
- "Amendment History" section (official amendments that previously targeted it).

### What Is NOT Yet Enforced (Backlog)

Per DEV_NOTES and SOUL_DRIVER:
- Title ≤100 chars / description ≤10k at creation time (UI hints + backend enforcement).
- 365-day sunset + renewal votes.
- 3-consecutive-week inactivity dismissal.
- True "majority of all registered users" (current promotion is simple per-window yes > no).
- Strict Sunday-only voting windows (current `isVotingOpen` is an MVP stub that returns True if candidates exist).
- Categories/tags + Library filtering.

These are the next natural wave after the engine + UX polish are solid.

## Key Files

- `Database.py:368-584` — The entire voting engine comment block + all the functions above.
- `Vote.py` — `computeTallies`, `getWinners`.
- `Policy.py` / `Amendment.py` — state constants (`DRAFT`, `CANIDATE`, `OFFICIAL`) + validators.
- `PlotterApp.py:392-423` — the `/submit-ballot` and `/close-window` routes (thin delegation).
- `Ballot.py` — presentation object that templates consume (fresh vs already-voted paths).

## Mental Model for Agents / Simulation Work

An agent that wants to "participate in the democracy" must drive the exact same transitions:
1. Create draft (POST to draft endpoint or call helper).
2. Submit it to canidate.
3. (In a simulated window) cast a ballot via `recordUserBallot` (or the `/submit-ballot` surface).
4. (As operator) call `promoteWinnersFromWindow`.
5. Observe the effect on `official/` and on any simulated world metrics.

This is exactly why the action surface must stay faithful to the real Party (see Agent-Action-Surface.md).

---

*This page exists because the lifecycle is the heart of the project. Any future change to transitions, promotion rules, or ballot formation must be reflected here first.*