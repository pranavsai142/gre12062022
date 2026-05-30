# Data Model and Firebase RTDB

**Authoritative source**: The file `FIREBASE_STRUCTURE.md` at the project root (last updated 2026-05-19 from live snapshot + code). This wiki chapter is a companion that adds code-level usage patterns and agent implications.

## High-Level Tree (exact)

```
/ (root)
├── policy/
│   ├── draft/
│   ├── canidate/          ← note the spelling
│   └── official/
│
├── amendment/
│   ├── draft/
│   ├── canidate/
│   └── official/          (populated on promotion)
│
├── voting/
│   └── {windowId}/        e.g. "2026-W21" or "2026-DEV-TEST-01"
│       ├── participation/
│       │   └── {uid}/
│       └── votes/
│           └── {uid}/
│
└── meta/
    └── currentWindowOverride   (string or absent)
```

**No top-level `users/` collection.** Identity lives only in Firebase Authentication. RTDB stores only `userId` (uid) + email as foreign keys.

## Detailed Schemas (from FIREBASE_STRUCTURE.md + code)

### policy/{status}/{policyId} and amendment/{status}/{amendmentId}
Common fields:
- `title`, `description`
- `type`: "draft" | "canidate" | "official"
- `userId`
- `created`, `updated`, `submitted` (timestamps)
- `enacted` (only on official after promotion)
- For amendments: `policyId` (required foreign key)

`policyId` / `amendmentId` are UUID hex strings generated client-side on draft creation.

### voting/{windowId}/
- `participation/{uid}`: `{ "voted_at", "email", "windowId" }` — existence = user has voted this window.
- `votes/{uid}`: the full audit record `{ "userId", "email", "windowId", "submitted_at", "choices": { "policy-xxx": "yes", "amendment-yyy": "abstain", ... } }`

This is "the authoritative audit record for every vote."

## All Mutations Go Through Database.py Helpers

Never write raw RTDB references from pages or tools for party data. The helpers are the contract.

Key categories (see full source for signatures):
- Window management: `getCurrentVotingWindowId`, `setCurrentVotingWindowOverride`
- Per-status getters + cross-status `getPolicy` / `getAmendment` (draft → canidate → official search)
- User-scoped draft getters
- Ballot: `getBallotItems`, `getBallotForUser`, `hasUserVotedInWindow`, `getUserVotesInWindow`
- Voting: `recordUserBallot` (the big one — re-validation + dual write)
- Tallies & promotion: `getWindowTallies`, `promoteWinnersFromWindow`
- Dev / agent tools: `get_all_voting_windows`, `get_window_details`, `clear_window_votes`, `seed_test_votes`, `seed_synthetic_choice_votes`, `reset_user_votes`
- Centralized init: `ensure_firebase_initialized` (idempotent, snapshot fallback)

## Auth vs Data Split

- Firebase Auth (email/password today) → ID token → server-side validation → `session["user"]` (full decoded token).
- RTDB only ever sees the uid + email.
- Implication for tools/agents: if you need nice display names, either fetch via Admin SDK `auth.get_user(uid)` or just display the email/uid that is already stored in the vote records.

## Snapshot vs Live Usage

The `database_snapshot/theinternetparty-5b902-default-rtdb-export.json` is used for:
- Offline reasoning
- Bootstrapping docs
- Running tools/dashboards when the service account JSON is not present

All production paths and the real operator surface prefer live connection via the same credential used by PlotterApp.py.

## Implications for Agent / Simulation Work (TheInternet dojo)

- Agents should drive behavior exclusively through the Database helpers (or the HTTP surfaces that call them) so that simulation stays faithful to production.
- Use synthetic `windowId` values (e.g. "2026-DEV-EPISODE-042") + the override mechanism for isolated episodes.
- After `promoteWinnersFromWindow`, the simulator can directly inspect `policy/official/` and `amendment/official/` to apply world effects.
- Full vote records under `voting/{window}/votes/` give perfect labeled data for reward modeling ("what the democracy actually decided").

---

**Always keep this chapter in sync with FIREBASE_STRUCTURE.md at the root.** If the RTDB shape ever changes, both documents must be updated before any code that depends on the shape.