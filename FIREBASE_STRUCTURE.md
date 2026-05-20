# Firebase Realtime Database Structure — The Internet Party

**Last updated:** 2026-05-19 (from live export `database_snapshot/theinternetparty-5b902-default-rtdb-export.json` + current codebase + post-voting implementation)

This document is the single source of truth for the RTDB tree. It is critical for building reliable **Dev Tools** and the **Admin Console** (both will be Prefab dashboards).

---

## 1. High-Level Tree

```
/ (root)
├── policy/
│   ├── draft/
│   ├── canidate/          (note the consistent spelling "canidate" everywhere in the app)
│   └── official/
│
├── amendment/
│   ├── draft/
│   └── canidate/
│   (official/ expected in the future)
│
└── voting/
    └── {windowId}/          e.g. "2026-W21"
        ├── participation/
        │   └── {uid}/
        └── votes/
            └── {uid}/
```

**No top-level `users` collection.**  
User identity lives entirely in **Firebase Authentication** (ID tokens). The Flask app only stores the decoded token in `session["user"]`.

---

## 2. Detailed Schemas

### 2.1 `policy/{status}/{policyId}`

Common fields (present on most records):

- `title`: string (< 100 chars per MetaPolicy)
- `description`: string (< 10,000 chars)
- `type`: "draft" | "canidate" | "official"
- `userId`: Firebase uid of the author
- `created`: timestamp (float seconds)
- `updated`: timestamp
- `submitted`: timestamp (set when moved from draft → canidate)

`policyId` is a UUID hex (generated client-side on creation).

### 2.2 `amendment/{status}/{amendmentId}`

Almost identical to policy, plus:

- `policyId`: the policy this amendment targets (required for amendments)
- All other fields same as above.

### 2.3 `voting/{windowId}/`

Window IDs are currently ISO week strings (`2026-W21`).

#### `participation/{uid}` (one record per user who voted in the window)
```json
{
  "email": "pranavsai142@gmail.com",
  "voted_at": 17792...,
  "windowId": "2026-W21"
}
```

#### `votes/{uid}` (the actual ballot — the "dictionary with the user id and voting status" from the original notes)
```json
{
  "userId": "6MXW4fbK2aUfgCDOTeJjGPYTMy12",
  "email": "...",
  "windowId": "2026-W21",
  "submitted_at": 17792...,
  "choices": {
    "policy-c923f6f8b60a43999c5759e05b894590": "yes",
    "amendment-660dd1a23d18442bb697a60e6b6ee0f4": "abstain",
    ...
  }
}
```

This is the authoritative audit record for every vote.

---

## 3. How the Application Uses the Tree (Current Code)

- **Draft flow**: `policy/draft/` and `amendment/draft/` (private to `userId`)
- **Promotion to ballot**: `submitDraft*` moves from `draft/` → `canidate/`
- **Ballot / Voting**: Live `canidate/` items become the ballot for the current ISO week.
- **One-vote enforcement**: Presence of `voting/{window}/participation/{uid}`
- **Cast vote**: Full choices written to `voting/{window}/votes/{uid}`
- **Promotion to official**: `promoteWinnersFromWindow` copies qualifying `canidate` items to `official/` (and deletes from `canidate/`)

All of this logic lives in `Database.py` (plus the `Vote.py` and `Ballot.py` helpers added in the previous phase).

---

## 4. Auth vs Data

- **Firebase Authentication** (email/password today, phone planned)
  - Produces the ID token you see in the "User Info" example the user pasted:
    ```json
    {
      "uid": "6MXW4fbK2aUfgCDOTeJjGPYTMy12",
      "email": "pranavsai142@gmail.com",
      "email_verified": true,
      ...
    }
    ```
- **Realtime Database** only stores the `userId` (the uid) as a foreign key.
- The Flask session stores the entire decoded token under `session["user"]` for the lifetime of the browser session.

**Implication for tools**: Any admin/dev tool that wants to show "nice names" must either:
- Store a minimal user profile in RTDB (future), or
- Use the Admin SDK `auth.get_user(uid)` calls (possible but slower), or
- Just show the uid + email when we have it from the vote record (good enough for v1 admin tools).

---

## 5. Implications for the New Work

1. **Dev Tools** need safe "nuclear" buttons:
   - Clear `voting/{window}/` subtree (participation + votes)
   - Move items between draft/canidate/official with audit
   - Seed realistic data while preserving the foreign keys

2. **Admin Console** can give a beautiful read-mostly view of exactly the tree above, with drill-down into any window's full vote history.

3. **Public website** (Policy library, Account, etc.) should surface:
   - Official = the enacted platform (the law)
   - Canidate = what is currently being voted on
   - Draft = private to the logged-in user

4. **Prefab dashboards** are the right place for the complex admin/dev UIs because they give us DataTable, Charts, reactive forms, etc. with almost zero frontend code.

---

## 6. Snapshot vs Live

The provided `database_snapshot/...json` is a point-in-time export.  
All tooling and the admin console should connect **live** to the RTDB using the same service account as `PlotterApp.py` (`/data/theinternetparty-5b902-...json`).

The snapshot is primarily useful for:
- Offline reasoning
- Writing tests against realistic data
- Bootstrapping the structure documentation

---

**Next step (already in the active todo):** Use this document as the foundation while building the Prefab Dev Tools and Admin Console.

This structure is simple, clean, and exactly matches the original 2024 vision in the dev notes. We just need great interfaces on top of it.

---

## 7. Snapshot Contents (as of the provided export)

From `database_snapshot/theinternetparty-5b902-default-rtdb-export.json`:

- **voting/**: 1 window (`2026-W21`)
  - participation: 1 user
  - votes: 1 full ballot record
- **policy/**:
  - draft: 2
  - canidate: 5
  - official: 1
- **amendment/**: present (counts vary; structure matches policies)

These numbers are used by the Dev Tools spike and full dashboards for realistic demo data when live RTDB is not reachable (e.g. missing service account JSON in a fresh agent environment). All Prefab tools prefer live connection via the same credential path used by PlotterApp.py (`/Users/pranav/data/theinternetparty-5b902-firebase-adminsdk-qlzzx-3864b82b40.json`).

**For Dev Tools / Admin authors**: Always support a graceful snapshot fallback so the dashboards are runnable "out of the box" for testing and agentic use without requiring the private admin JSON on every machine.

---

## 8. Dev Tools & Admin Implications

- `get_all_voting_windows()` should scan `voting/` keys (or synthesize from current ISO week + snapshot).
- `clear_window_votes(windowId)` deletes `voting/{windowId}/` subtree (participation + votes) — use with extreme caution; only in dev tools.
- Seed functions create synthetic participation/votes under test window IDs (e.g. `2026-DEV-01`).
- Admin console can safely read everything; mutations should log intent.
- Live tallies and promoteWinnersFromWindow already exist in Database.py and are re-used by both tools and the public Vote page "operator" button.

All future changes to the RTDB shape **must** be reflected here first.