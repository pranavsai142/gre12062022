# Project Wiki — The Internet Party (Party No. 3) — Living Documentation

**North Star (from SOUL_DRIVER.md):** Parallel direct democracy "Party No. 3" — any internet user can join (name + reputable phone). Strict self-enforcing meta-policies: word limits (title <100, desc <10k), automatic 365-day sunsets with renewal votes, weekly majority-of-registered voting on ISO-week windows, 3-consecutive-week inactivity dismissal. Serves as accountability/transparency layer for US elections. Platform: Truth • Freedom • Health.

**Current Mechanical Reality (2026-05, from DEV_NOTES + handoffs):** Full end-to-end governance engine is **live and production-grade for testing**: draft → canidate (preserved spelling) → live ballot (canidate/* items) → immutable one-vote-per-user-per-ISO-week window → manual promote (yes > no) to official. The **live website `/account` Operator & Dev Tools panel is the PRIMARY control surface**. Secondary power tools (CLI in `dev_tools/`, admin/admin_console.py prefab) exist and share the same Database.py backend. Public experience (Congressional Library `/policy`, `/vote`, `/drafts`, detail pages with real difflib diffs) is high-quality and circular. Pure Flask `render_template_string` + Firebase RTDB (no client build). Agents can (and will) drive actions for simulation.

**This wiki captures the deep "why", non-obvious invariants, and painful lessons** so future humans + Grok sessions (especially agent-integration work) never re-learn them. Historical detail lives in dated `notes/GROK/handoffs/`. Living reality in `DEV_NOTES.md` + `SOUL_DRIVER.md`.

## Quick Mental Models (Read These First)
- **Lifecycle in one sentence**: Private drafts → submit to public "canidate" ballot → weekly window vote (one immutable ballot) → operator "Promote Winners" moves yes>no items to official platform (losers stay in canidate for later).
- **"Canidate"**: Not a typo. Sacred preserved convention across DB paths, classes, UI, JS, docs. Changing it breaks the universe.
- **Operator surface**: Just open the running site, log in, go to `/account`. Everything (seed deterministic yes/no/abstain batches, clear, promote, arbitrary window override that affects the whole public site, live tallies) is there. CLI/prefab are supplements.
- **Voting window**: ISO week string (e.g. "2026-W21"). Overrideable via `meta/currentWindowOverride` for testing. One participation + one full choices record per uid per window. Abstain is safe default for untouched mandatory ballots.
- **Auditability**: Every ballot is a complete, timestamped, email-attached `choices` dict under `voting/{window}/votes/{uid}`. Participation is the "already voted" flag. Tallies computed on demand via Vote.computeTallies.
- **Architecture in one sentence**: Every mutation goes through Database.py helpers on top of Firebase RTDB. Every page is a self-contained `render_template_string` with duplicated base styles/menu. JS is always thin form-collect → POST → handle.
- **Dual repo**: Governance engine + delightful public party surfaces (the soul) vs. 2020 election monitor heritage (PresidentMonitor, ElectionMonitor, az/co/ga/ etc. data + /monitor routes). Prioritize the former.

## Recommended Reading Order for New Sessions / Agent Work
1. `notes/GROK/SOUL_DRIVER.md` + `DEV_NOTES.md` + latest 1-2 handoffs (the `/init` contract).
2. This INDEX + Governance-Lifecycle.md + Voting-Windows-and-Ballots.md + Data-Model-and-Firebase.md.
3. Operator-Surface.md + Agent-Action-Surface.md (for simulation/testing).
4. Hard-Won-Lessons.md + Architectural-Decisions.md.
5. Source: PlotterApp.py (routes), Database.py (everything), the four domain models, AccountPage.py + VotePage.py (primary surfaces), FIREBASE_STRUCTURE.md.

## Wiki Chapters (High-Signal Only)
(See sibling .md files for full depth.)

- [Governance-Lifecycle.md](Governance-Lifecycle.md) — Exact state machine, transitions, promotion rule, amendment diff experience, what is *not yet* enforced.
- [Voting-Windows-and-Ballots.md](Voting-Windows-and-Ballots.md) — ISO-week mechanics, override lever, immutability + audit records, Abstain defaults, tallies/winners, Ballot object.
- [Data-Model-and-Firebase.md](Data-Model-and-Firebase.md) — Complete RTDB tree (with quotes from FIREBASE_STRUCTURE.md + snapshot), every Database.py helper categorized, auth vs. data split.
- [Architectural-Decisions.md](Architectural-Decisions.md) — Why render_template_string + duplication, "canidate" preservation, operator primacy decision (with handoff rationale), no-build constraint, centralized firebase init.
- [Operator-Surface.md](Operator-Surface.md) — `/account` god-mode (full button inventory + JS flows), why it replaced separate dashboards.
- [Agent-Action-Surface.md](Agent-Action-Surface.md) — CLI commands, prefab consoles, seed patterns for deterministic simulation, calling the same Database helpers agents will use.
- [Hard-Won-Lessons.md](Hard-Won-Lessons.md) — Conditional feedback, text hardening, "fish" errors, choice normalization war stories, small-increment philosophy.
- [MetaPolicies-Original-vs-Current.md](MetaPolicies-Original-vs-Current.md) — SOUL_DRIVER vision (365 sunsets, inactivity dismissal, true majority-of-registered, char limits) vs. today's MVP (window promotion only).
- [Public-UI-Patterns-and-Navigation.md](Public-UI-Patterns-and-Navigation.md) — Card aesthetic, diff UX, Library filters, circular nav, empty states.
- [CSS-Tech-Debt.md](CSS-Tech-Debt.md) — Quantified duplication across *Page.py files + consolidation plan (does not change output).
- [Legacy-Monitors.md](Legacy-Monitors.md) — Dual-nature boundaries; safe places to extend vs. ignore.

## How to Maintain This Wiki
- When a session reveals a "I wish I had known..." (especially around voting windows, operator actions, or "canidate"), add or update the relevant chapter + link from INDEX.
- End meaningful work with `/done` (it updates handoffs + DEV_NOTES; consider a wiki delta).
- Prioritize depth on the democracy engine. Legacy monitor details belong in their own thin chapter.

**Last major sync:** 2026-05-30 (post full 2026-05 governance + polish delivery + deep wiki seed). This wiki + the GROK/ layer is the durable memory that survives context loss.

*High-signal updates only. Short by omission where possible; rich where confusion historically occurred.*