# DEV_NOTES — The Internet Party (Living Project Reality)

**Last major update:** 2026-05-22 — Additional high-signal UX polish round on top of the 05-21 foundation: title+description visual diff with unchanged messages, simplified target-policy box, long-content hardening on cards & vote descriptions, Abstain as safe default for mandatory ballots, and real "Target Window" override in the live Operator panel (meta/currentWindowOverride + Set/Clear). Rich history in `handoffs/2026-05-22-post-polish-ux-operator-power.md`. This document stays deliberately short and forward-looking.

## Current Big Picture

The project has delivered the **core governance engine** that was the #1 priority in the original 2024 dev notes:

- Full draft → canidate ("canidate" spelling preserved) → official lifecycle for both Policies and Amendments.
- `Vote.py` + `Ballot.py` + Database helpers for ISO-week voting windows.
- One immutable vote per user per window (participation + votes stored under `voting/{windowId}/`).
- Public ballot view + logged-in voting UI on `/vote`.
- Live tallies, "you already voted" state, and operator "Close Window & Promote Winners" (simple yes > no rule).
- Promotion copies winners from canidate → official and cleans up.
- Operator & Dev Tools live control surface is now **on the main website itself** (`/account` after login) — seed, clear, promote, reset-user-votes, inspect windows/ballots/tallies. This is the canonical, real-time surface (CLI and prefab dashboards remain excellent secondary tools).
- Login/Register fully production-grade (card UI, conditional error boxes, etc.).
- Amendment detail page shows original policy text cleanly; policy detail page is next for history/pending sections.

The revolutionary heart — actual parallel voting with integrity — is functional. People can propose, amend, vote weekly, and see winners become official policy.

**Dual nature of the repo** is still present:
- The Internet Party platform (the soul).
- 2020-era election data monitors/plots (PresidentMonitor, ElectionMonitor, state data dirs, chrome bundle for scraping). These are secondary but not abandoned.

**Next phase focus:** Polish & correctness (the four open items below), then enforcement of meta-policies (char limits, categories, sunset mechanics, etc.), and fleshing out the public-facing "Congressional Library" / About experience to match the quality of the delivered Vote and Account pages.

## Hard-Won Lessons (Do Not Re-Learn These)

- **"canidate" is now a convention, not a bug.** The entire codebase, DB paths, UI, classes, and JS use "canidate" consistently. Do not attempt to rename it to "candidate" — it will break everything and erase history. Preserve it everywhere.
- **The live website is the primary operator surface.** After the 2026-05 delivery, the human explicitly wants "just open the site and do it." CLI (`python -m dev_tools.cli`) and prefab dashboards are powerful for agents/scripts, but the Account page Operator panel is the blessed real-time control surface. Documentation and UX must reflect this.
- **CSS duplication is the largest visible tech debt.** Every *Page.py duplicates 50-80 lines of identical `<style>`. The next polish wave should consolidate this (Styles.py or base template logic) without changing rendered output.
- **Small, focused, verifiable increments win.** The voting engine, dev tools, admin console, login revamp, and amendment detail polish were all delivered cleanly because they were broken into WP1–WP4 style packages with explicit acceptance criteria and `todo_write` tracking.
- **Context discipline + handoffs are non-negotiable** for a project this long-lived. Without `/init` + `/done` + `notes/GROK/`, every new session or agent would waste tokens re-deriving the voting window logic, the "canidate" rule, the operator surface decision, etc.
- **Firebase Realtime DB + Flask render-string architecture is the contract.** No client build step for the main party site (CDNs + static/js). All mutations go through Database.py helpers. Centralized `ensure_firebase_initialized()` prevents duplicate init warnings.
- **Error/feedback UX matters.** Empty result boxes, always-visible error containers, and silent failures destroy trust in operator tools. The four current open items are mostly about making feedback conditional and human-readable.
- **Always harden text containers early.** User-generated titles and descriptions will eventually contain long or unbreakable strings; adding `word-wrap: break-word`, `overflow-x: auto`, and `pre-wrap` on the first sign of trouble prevents surprising layout breakage on cards, ballot items, and diffs.
- **Default to the required safe choice on mandatory forms.** Pre-selecting Abstain (and having the backend defensively default missing items) satisfies "every member must vote on every item" while making an untouched ballot a valid, low-friction submission.
- **A real window override lever is extremely powerful.** Letting the operator type any window ID (including empty/test ones), hit Set/Enter, and have the *entire live site* (including public /vote) instantly reflect it is far more useful for testing and demos than parameter-only tools.

## Information Architecture (Where Everything Actually Lives)

### Core Application
- `PlotterApp.py` — THE app. All routes, Firebase bootstrap, session handling, `/validate-token`, every party endpoint (`/draft`, `/detail/<id>`, `/vote`, `/account`, `/submit-ballot`, operator actions, etc.). Also hosts the legacy monitor routes.
- `Database.py` — All persistence. Policy/Amendment CRUD by type, voting window helpers (`getCurrentVotingWindowId`, `getBallotForUser`, `recordUserBallot`, `promoteWinnersFromWindow`, etc.), centralized Firebase init.
- `Policy.py`, `Amendment.py`, `Vote.py`, `Ballot.py` — Domain classes with validation, serialization, tallies, winner logic.
- `*Page.py` (14 files) — Each exports `render(user)` that returns a complete HTML string. No layout inheritance yet.
- `static/js/` — 7 focused JS files (login, register, draft, detail, vote, draft-amendment, detail-amendment). All follow the same "collect form → POST → handle response" pattern.
- `User.py` — Minimal validator on decoded Firebase token.

### Operator / Agent Power Tools (Secondary but Excellent)
- `dev_tools/` — `cli.py` (primary agent interface), `dev_dashboard.py` (visual prefab), `spike.py`.
- `admin/` — `admin_console.py` (god-view tables + action cards).

### Data & Monitors (Secondary Heritage)
- `az/`, `co/`, `ga/`, `il/`, `pa/`, `ri/` — State election result files (txt + countyResults.json).
- `PresidentMonitor.py`, `ElectionMonitor.py`, `Plotter.py` — Scraping + matplotlib viz.
- `chrome_install/` — Portable Chrome bundle for headless scraping.

### Firebase RTDB Structure (Current)
```
policy/{draft,canidate,official}/{id}/
amendment/{draft,canidate,official}/{id}/
voting/{ISO-week-windowId}/
    participation/{userId}
    votes/{userId}          ← full ballot choices
```

No `elections/` collection yet (the windowId + ISO week logic lives in code). Voting data is append-only/audit-friendly.

### Pragmatic Memory Layer (This Directory)
- `notes/GROK/SOUL_DRIVER.md` — North star + philosophy (changes rarely).
- `notes/GROK/DEV_NOTES.md` — This file. Current reality + lessons + backlog (updated by `/done`).
- `notes/GROK/handoffs/` — The durable memory layer (dated session records from `/done`). Legacy `PLANNING/` structure is archived under `ARCHIVE/PLANNING/`.
- `notes/GROK/ARCHIVE/` — Retired large artifacts (old 500-line dev notes live here now).

### How to Run (Canonical)

**Production (Render / after SSH to box):**
```bash
./start.sh
# or
pipenv run gunicorn --bind 0.0.0.0:$PORT --workers 2 --threads 4 PlotterApp:app
```

**Local dev (persistent server, full LAN/network access with macOS firewall ON):**
```bash
export DATA_FOLDER=/path/with/cert   # if not /Users/pranav/data/
./start_local_with_node_relay.sh
```
- Runs gunicorn on `127.0.0.1:5001` + Node TCP relay on `0.0.0.0:5000`.
- Access locally: http://127.0.0.1:5000
- Access from other devices on same network: http://YOUR_LAN_IP:5000
- Firewall can stay enabled (no GUI entries or whitelist needed — Node is the public listener).

**Kill everything (gunicorn, relay, ports, rogue processes):**
```bash
./kill_all.sh
```

Secondary tools: `python -m dev_tools.cli --help` and prefab dashboards.

Firebase admin cert required at `$DATA_FOLDER/theinternetparty-...json`.

## How to Work Here (Pragmatic Loop + Project Conventions)

1. **Always start with `/init`** — reads SOUL_DRIVER + DEV_NOTES + active plan + latest handoff. Never dive into code first.
2. **Use `todo_write` for anything with 3+ steps or real complexity** — gives the human visibility and prevents batching mistakes.
3. **Make the change, then immediately verify** — run the server, click the button, check the DB via dev tools, etc. Minimum gold-plating.
4. **When ambiguous, ask** — use `ask_user_question` for narrow decisions rather than guessing.
5. **End meaningful work with `/done`** — it will:
   - Capture what happened
   - Update this DEV_NOTES.md and SOUL_DRIVER if needed
   - Write a dated handoff into `handoffs/`
   - Archive any completed plan
6. **Never let chat history or `~/.grok` override the repo docs.** The notes/GROK/ layer is the durable truth.

### Project-Specific Rules
- Preserve the word "canidate" everywhere (DB, classes, UI, routes, docs).
- Website Operator panel is primary; document CLI/prefab as power-user supplements.
- All new UI should match the recent visual language (`.detail-header`, `.detail-card`, status pills, orange #ff6600 accents, target-policy grey box).
- Keep feedback conditional: only show result/error boxes when there is actually content.
- For voting-related work, always think auditability + "one immutable vote per window" first.
- Local dev network access: always use `./start_local_with_node_relay.sh` (gunicorn internal + Node relay). Keeps firewall ON and server persistently reachable on LAN. No whitelist or GUI firewall entries required.

## Next / Forward Backlog (Distilled — Short by Design)

We keep this list deliberately short. Historical status of completed items lives in dated handoffs under `handoffs/`.

1. Enforce meta constraints at creation time (title ≤100 chars, description ≤10k) with live UI hints and counters.
2. Add categories/tags to policies + filtering/sorting on the Congressional Library.
3. Deepen the public experience (stronger empty states, registered-user visibility, clearer "how voting works" moments).
4. Later true MetaPolicy enforcement (365-day sunset renewal votes, 3-week inactivity dismissal, stricter Sunday window gating, etc.).
5. CSS consolidation (the largest remaining tech debt — every *Page.py still duplicates the base styles).
6. Election monitor county graphs from the existing `countyResults.json` files (heritage feature).

The next natural wave is making the rules actually bite while keeping the proposal + voting experience delightful.

## Historical Note

The original `DEV_NOTES_AND_IMPLEMENTATION_STATUS.md` (now in `ARCHIVE/`) contained the full 2024 vision dump + exhaustive 2026 exploration mapping + the voting engine delivery log. It was the unedited source artifact. This `DEV_NOTES.md` + `SOUL_DRIVER.md` are the distilled, living, agent-optimized versions that `/init` will actually ask future sessions to read.

---

*If you are an agent reading this after `/init`: you now know the soul, the current mechanical reality, the short forward backlog, and the non-negotiable conventions. Go do good work. When you're done, run `/done`.*