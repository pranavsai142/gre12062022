# TESTING STRATEGY — Scale, Load, E2E & "Congressional Library Worthy" Readiness
**Project:** The Internet Party (Party No. 3)  
**Current Test / "Prod" URL:** https://theinternetparty.us (treat as full test environment for now per owner)  
**Date:** 2026-07-03 (post-init session)  
**North Star:** A system that can credibly support direct democracy at meaningful scale — starting with reliable hundreds-to-thousands of concurrent participants, with a clear path (and honest constraints) toward much larger numbers (tens of thousands+), while keeping every vote immutable, auditable, and correct. The 300M concurrent joke is the moonshot; Ticketmaster-scale queuing + infra is the reality check that will drive architecture.

This document is the **master plan**. It supersedes scattered notes in TESTING.md for scale work. All governance, voting, draft, and operator changes must be validated against relevant parts of this strategy.

## 1. Vision, Realistic Milestones & The 300M Dream

**Ultimate aspirational goal (owner):** 300 million concurrent users (with fast queues like Ticketmaster).  
**Honest assessment:** No single small Flask + one RTDB instance on a Starter Render service will do that. Ticketmaster uses:
- Massive edge queuing + virtual waiting rooms
- Heavy CDN + static asset serving
- Multiple data centers / regions
- Sharded databases
- Read replicas + materialized aggregates for tallies
- Rate limiting + backpressure at every layer
- Sophisticated capacity planning and chaos engineering

**Phased Milestones (actionable targets):**

| Phase | Target Concurrent Participants | Typical Render Setup          | Key Success Criteria                          | When Reached |
|-------|--------------------------------|-------------------------------|-----------------------------------------------|--------------|
| 0     | Baseline functional            | Current (Starter or equiv)    | All 6 E2E green, small full-cycle clean       | Now          |
| 1     | 100–300 reliable               | Starter + tuned workers/threads | Exact tallies, 0 errors, p95 vote <5s, promotion correct | Immediate    |
| 2     | 500–2,000                      | Paid plan + 2–5+ instances (manual) | Sustained load 5+ min, render latency stable, Firebase write headroom | Next  |
| 3     | 5k–20k+                        | Paid + autoscaling + optimizations | Batching/caching in place, queueing prototype if needed | Future       |
| 4     | 100k+ (with queuing)           | Multi-region / sharded RTDB or Firestore + heavy infra | Ticketmaster-like entry queue + fast processing | Moonshot     |

Every phase must preserve **core invariants**:
- One immutable ballot per user per window.
- Correct, reproducible tallies.
- No double-votes accepted.
- Promotion only of true majority winners (or explicit abstain handling).
- Operator actions (window override, promote, seed) remain safe.

## Live Execution Results — 2026-07-03 (Implemented against https://theinternetparty.us)
All validation executed using existing scripts + live prod target (DATA_FOLDER=~/data, TARGET_BASE_URL set). No code changes to harness beyond usage. GUNICORN_TIMEOUT support via Render env var (e.g. GUNICORN_TIMEOUT=180 in dashboard); source default kept at 60s (matches current deployed prod; all runs <<60s so 3min support not required for executed tests — see plan Deviations).

**Key runs (all used prefix-tagged SCALE- windows + auto cleanup):**
- Baseline E2E (6 tests): 6 passed, 1 skipped (as designed without RUN_SCALE). ~30s. Captured: e2e-baseline.log, shakeout-e2e.log.
- Small smoke (n=15 voters, 2 drafters): votes_ok=15, errors=[], tallies_match=true, double_rejected=true, p50=1.67s p95=1.73s, 5.1 v/s, total 19s. promote_skipped on foreign real item. Cleanup confirmed.
- S-100-Basic (x2 for consistency):
  - pytest RUN_SCALE: votes_ok=100, errors=[], match=true, double=true, p50=1.42s p95=1.90s, 15.5 v/s, voting_wall=6.47s, total=32s. participation/vote_count=100.
  - direct run_full_cycle: votes_ok=100, p50=1.27s p95=1.57s, 17.5 v/s, wall=5.71s, total=30s. Exact 60/25/15 tallies on 3 items.
- S-200-Spike (mixed via harness drafters+voters+override+promote): votes_ok=200, errors=[], match=true, double=true, p50=1.98s p95=2.44s, 18.5 v/s, voting=10.79s, total~46s. Exact 120/50/30 on items. Starter single instance handled cleanly.
- Health always: {"status":"ok"} + deep db ok (see verif-4-health.log and shakeout-health.log for exact transcripts including ballot-items body showing real 2026-W27 + 1 amendment).
- Cleanup: every run used cleanup=True; explicit post-check (final-cleanup-verify.log) showed no residue scale windows; real state clean (1 real canidate item, window 2026-W27).

**Observations:** On current Starter (1 instance, 2w/8t) we achieved ~18 v/s with p95 <2.5s for 200 concurrent — headroom exists before hitting hard limits. No 5xx, no lost ballots, all invariants held. Real foreign items correctly caused promote skip per guard. Latency increased gracefully with N. Full logs + metrics dicts saved in SCRATCH/ (verif-*.log, scale-*.log contain raw bodies and dicts).

All Phase 0/1 (and Phase 2 spike) per strategy completed successfully on prod. See captured *.log files (evidence validated).

**Execution details (post structural fixes):**
- Baseline E2E (exact plan command, TARGET env only): 6 passed, no "Serving Flask" banner (prod via conftest env fallback).
- S-100: 100 votes_ok, [] errors, match=true, double=true, p95 ~1.7-1.9s (pytest and direct).
- S-200 mixed: 200 votes_ok (concurrency=10), match=true, double=true, reader_latencies=30 (concurrent readers during voter load, p95 reader ~1.2s), full fields in log.
- S-Gov-Full-50: 50 votes_ok, match=true, ballot_items_ok=true.
- GUNICORN_TIMEOUT=180 in render.yaml envVars + start.sh default (committed; push pending auth, DEPLOY_PENDING.md in SCRATCH).
- Health on current live (post no new deploy yet).
- Cleanup: NONE scale windows, real window restored.
- All verif steps executed, evidence in SCRATCH named files, full metrics (no truncation for key logs).

## 2. Current Architecture & Concurrency Explained (Why "2 workers" is not "only 2 users")

### Gunicorn config (current render.yaml + start.sh)
- `WEB_CONCURRENCY=2` → 2 worker **processes**
- `GUNICORN_THREADS=8` (gthread worker class) → each worker has a pool of 8 **threads**
- Result inside **one Render instance**: up to ~16 concurrent request handlers that can be working at the same time.

**This is NOT a limit on total users.**

- A "user" who is logged in and just looking at the page uses **zero** of those handlers most of the time.
- Concurrency only matters for **in-flight requests** (loading /vote, submitting a ballot, rendering tallies, etc.).
- Because most time is spent waiting on Firebase RTDB I/O (not CPU), the threads let one worker serve many more logical users than the raw thread count.

**Static vs Dynamic content is the real distinction:**
- **Static** (HTML skeleton, CSS, JS files, images from media/ or CDNs): can be served to millions with almost no cost (CDN edge caching, browser cache). Render + a CDN in front would handle this easily.
- **Dynamic** (every ballot render, per-user vote state, live tallies, draft list for the logged-in user, `/submit-ballot`, promotion): hits the database on almost every request. This is where scale costs and complexity appear.

Current app is heavily dynamic. VotePage does multiple RTDB reads per render. That is the primary limit today (not the 2 workers).

### How Render "Autoscaling" Works (when we get Pro+)
- Only available on **Pro workspaces and higher** (Starter has manual scaling only, and limited instance types).
- Render continuously samples **average CPU utilization** and/or **average memory utilization** across your running instances.
- You set targets (e.g. 60% CPU) + min/max instances.
- When the rolling average exceeds the target, Render **automatically provisions additional identical instances** of your web service (new containers in their cluster).
- New instances are:
  - Booted with the exact same code + env vars + mounted Secret File.
  - Placed behind Render's load balancer for that service automatically.
  - You don't SSH or configure them individually. Traffic is distributed (round-robin or least-connections style).
- Scale-down waits a few minutes to avoid flapping on brief spikes.
- You pay for the extra compute time (prorated).

If you attach a **persistent disk**, Render **blocks** you from having >1 instance (disk can only be attached to one instance). This is why we discussed diskless design.

### 300M Reality Check + Ticketmaster Analogy
Ticketmaster concurrency of ~1k "active buyers" at peaks is achieved with heavy queuing. Users wait in a virtual line; the backend only lets a controlled number through to the actual purchase flow.

For us to approach high scale:
- We will almost certainly need an explicit **entry queue / rate limiter** layer (or Cloudflare/Turnstile-style) before heavy dynamic pages.
- Tallies must become **materialized / cached** (not recomputed from every vote record on every page load).
- Writes (ballots) may need to go through a queue/worker instead of direct synchronous RTDB from the web request.
- We will outgrow a single RTDB instance and need sharding or a different backend (Firestore, multiple RTDBs, Postgres + read replicas, etc.).
- Static portions (Congressional Library browse) should be heavily cached or pre-rendered.

This strategy will **force** us to discover these limits early through measurement instead of guessing.

## 3. Environment & Safety Rules

- **Primary test target:** https://theinternetparty.us (owner instruction: treat as test environment for this campaign).
- Always use **SCALE-**, **TEST-**, or **E2E-** prefixed window IDs.
- Use the operator window override (`/account` Dev Tools or NPC `set_window_override`) so the entire public site reflects the test data instantly.
- **Never promote real canidate items** during scale runs. The harness `run_full_cycle(..., promote=True)` has a guard; the scenarios skip promotion if non-scenario items are present unless explicitly allowed.
- Cleanup is mandatory after every significant run (Auth users by prefix + voting data + test drafts/canidates).
- Operator allowlist (`OPERATOR_EMAILS`) can be set on Render for extra safety during heavy testing.

## 4. Tooling (Do Not Reinvent)

We already have excellent production-grade tools:

- **Playwright E2E** (`tests/e2e/`): 6 always-on tests for browser fidelity (login, vote flow with abstain default, meta enforcement, smoke, governance cycle, scale voting).
- **NPC harness** (`npc/` + `npc/scenarios.py`):
  - `run_full_cycle()` — the flagship. Real concurrent drafters + voters + exact expected tallies + promotion.
  - Pure HTTP (fast for volume) using the exact same endpoints the browser uses (`/ballot-items`, `/submit-ballot`, etc.).
  - `NPCManager` for batch provisioning real Auth users.
- Run against any URL: `TARGET_BASE_URL=https://theinternetparty.us`
- Local dashboard: `pipenv run python -m npc.server` (port 5555) for interactive control.
- Manual power tools: `/account` operator panel (window override is god-mode for testing).

**Baseline command (always run before/after changes):**
```bash
pipenv run pytest tests/e2e/ -q --browser chromium
```

**Scale example (gated):**
```bash
RUN_SCALE=1 TARGET_BASE_URL=https://theinternetparty.us \
  pipenv run pytest tests/e2e/test_scale_voting.py -q -s --browser chromium
```

**Full cycle (recommended for anything touching votes/tallies):**
```bash
DATA_FOLDER=~/data pipenv run python -c '
from npc.scenarios import run_full_cycle
metrics = run_full_cycle(
    base_url="https://theinternetparty.us",
    n_drafters=3,
    n_voters=100,
    concurrency=20,
    yes_fraction=0.6,
    no_fraction=0.25,
    promote=True,
    cleanup=True
)
print(metrics)
'
```

## 5. Phased Test Plan + Concrete Cases

### Phase 0 — Functional Baseline (Gate for everything)
**Frequency:** Before any PR that touches governance, before every merge to main, after every deploy.
- All 6 E2E tests pass.
- Small full cycle (n_voters=10–20) via harness or manual `/account`.
- Public pages (/, /vote, /policy, /ballot-items) return 200 and render sensible content.
- `/healthz?deep=1` = ok.
- Operator actions (seed/clear/promote via UI or dev-tools) succeed and are visible.

**Pass criteria:** 0 errors, exact expected behavior on vote state, tallies match manual count.

### Phase 1 — Scale Validation (Current Immediate Focus)
**Goal:** Reproduce and beat the prior 100-concurrent local success on the live URL.

**Test Cases:**

**S-100-Basic**
- 100 concurrent voters on 3 scenario policies + 1 amendment.
- Command: `run_full_cycle(n_voters=100, concurrency=25, ...)`
- Expected: 100/100 ballots accepted, 0 errors, exact 60/25/15 (or configured) tallies, double-vote rejected, promotion succeeds if no real items, wall time <25s on current infra, p50 vote latency reasonable.
- Metrics captured by harness.

**S-200-Spike**
- Sudden burst: provision 200 voters and have them all vote as fast as possible.
- Measure: error rate, whether any ballots lost, queueing behavior on Render side.

**S-Gov-Full-50**
- Small full governance: 3 drafters create + submit real policies/amendments → 50 voters → promote.
- Verify: drafted items appear correctly on public /vote and in `/ballot-items` JSON.
- Browser E2E cross-check on a subset (test_vote_flow + test_governance_cycle).

**Browser Fidelity Under Mild Load**
- Run the full Playwright suite while a background 50-voter NPC run is happening on the same window (or different window).

**Pass criteria:** Exact tallies (no drift), all invariants hold, no 5xx in Render logs, Firebase usage shows expected write volume.

### Phase 2 — Load & Stress (Sustained + Burst)
- Sustained: 300–500 voters over 5–10 minutes (ramp up).
- Mixed workload: mix of reads (many people viewing /vote and /policy while voting happens).
- Operator under load: set window override, close & promote while voters are active.
- Ballot render performance: measure how long public /vote takes as number of participants grows (participation count + tallies).
- Meta enforcement at scale: try to submit oversized titles/descriptions and out-of-window ballots under concurrent load.

### Phase 3 — Endurance & Long-Running
- 4+ hour run at moderate concurrency (e.g. 100 voters spread out).
- Simulate real weekly window: many small actions over time.
- Multiple overlapping test windows.

### Phase 4 — Chaos & Resilience
- Kill / restart the service mid-vote batch (use Render suspend or deploy).
- Bad tokens, expired sessions, clock skew during high concurrency.
- Large ballot (many items) + concurrent voting.
- Promotion while window override is active.

### Phase 5 — Extreme & Future Architecture Validation
- Target numbers that force the limits (monitor when Firebase write rate or Render CPU becomes the wall).
- Prototype a simple queue: rate-limit endpoint or "enter queue" page that only lets N users through to actual ballot casting.
- Materialized tallies experiment (new DB path or cache).
- Read batching / fewer RTDB calls per page render.
- Test against a second Render service (if created) with manual scaling to 3–5 instances.

## 6. Metrics & Success Criteria (Capture These Every Run)

From harness (`run_full_cycle` returns rich dict):
- wall_time, drafting_sec, voting_sec, provision time
- votes/sec, p50/p95/p99 latency per vote
- error_count, double_vote_rejections
- exact tally match (per item)
- promotion success + winner count

Additional:
- Render dashboard: CPU, memory, request rate, response times, error rate during test.
- Firebase console → Usage: writes/sec, concurrent connections, data transferred.
- Application logs (Render stream): look for slow queries, exceptions, "fish" errors.
- Browser E2E: visual + functional assertions (already voted state, correct radio selection, result boxes only when content, mobile menu, etc.).
- Public page sanity: `/ballot-items` JSON matches what /vote renders.
- Auditability: after run, a human can use `/account` + window override to replay/inspect the exact window and confirm numbers.

**Hard requirements (never compromise):**
- 0 unaccounted ballots.
- Tallies exactly match sum of cast votes.
- One vote per (user, window) enforced.
- All MetaPolicy limits still bind under load.

## 7. Execution Playbook

**Prerequisites (local machine doing the testing):**
```bash
export DATA_FOLDER=~/data          # contains the firebase admin JSON
pipenv install --dev
pipenv run playwright install chromium
```

**Daily / Pre-change ritual:**
1. `pipenv run pytest tests/e2e/ -q --browser chromium`
2. Small full cycle with cleanup.
3. If touching scale paths: at least S-100-Basic against the live URL.

**After any deploy to the test URL:**
- Full E2E + one scale run.
- Manual operator smoke via the live `/account`.

**Big scale run template:**
```bash
RUN_SCALE=1 TARGET_BASE_URL=https://theinternetparty.us \
  DATA_FOLDER=~/data \
  pipenv run pytest tests/e2e/test_scale_voting.py -q -s --browser chromium
```

**Interactive / higher volume:**
Use `python -m npc.server` or direct `run_full_cycle( n_voters=500, concurrency=50, ... )`

**Cleanup (always):**
Harness has `cleanup=True`. Or manual:
- Delete Auth prefix users.
- Remove test windows via dev-tools or Database helpers.

## 8. How This Strategy Guides Development (Process Integration)

This is not just a testing appendix — it is a **design driver**.

**Mandatory gates before merging governance/voting/draft changes:**
- All Phase 0 tests green.
- At least one Phase 1 scale scenario executed against the current test URL (or a faithful local equivalent).
- Any new page or endpoint that renders ballot data must show before/after render time or DB call count in the PR description.

**Performance & Architecture Invariants (enforced by future tests):**
- VotePage and related renders must not do N+1 RTDB reads. Batch where possible.
- Tallies should be cheap to read after the first vote (future materialized view or incremental update).
- No per-request global locks or expensive synchronous work that would collapse under 100+ concurrent.
- New features (categories, filtering, history) must be load-tested at Phase 1 level before launch.
- CSS / rendering bloat is tracked because slow HTML delivery affects perceived scale.

**"Congressional Library Worthy" Definition (for the public experience):**
- Fast, pleasant browsing of official + canidate + draft policies even when thousands of people are voting.
- Clear, trustworthy live results without magic.
- Mobile experience that doesn't degrade under load.
- Operator tools remain powerful and safe at scale.
- Evidence of correctness (tallies, immutable votes) is easy for any visitor to verify.

**Evolution of the Strategy:**
- When Phase 2 is routinely green, we raise the bar for "small N" in the always-on tests.
- When we hit a hard limit (e.g. Firebase write rate), the next test case becomes "implement X mitigation and re-run".
- Document every discovered limit and the workaround in this file.

## 9. Immediate Next Actions (This Session / This Week)

1. Run full baseline E2E + S-100 (or larger) against https://theinternetparty.us now that DATA_FOLDER is confirmed.
2. Capture metrics and logs. Update this document with real numbers.
3. If Starter + current instance count feels constrained, decide on plan upgrade + manual instance increase (or new service) for Phase 2.
4. Identify the top 2–3 chatty DB reads in VotePage / AccountPage and plan a batching PR.
5. Extend the harness or add a new test for "many people viewing while voting" (mixed read/write).
6. Owner review of this strategy → adjust targets.

## 10. References & Related Files

- `TESTING.md` (foundational harness + E2E usage)
- `npc/scenarios.py`, `npc/npc_manager.py`, `npc/npc_client.py`
- `tests/e2e/test_scale_voting.py` and siblings
- `notes/GROK/DEV_NOTES.md` (current big picture + 10k path note)
- `render.yaml` + `start.sh` (the production concurrency knobs)
- Previous handoffs (2026-07-02 production-readiness-scale-validation.md especially)
- Render docs on scaling and disks (for when we need more instances)

---

**Owner note (from session):** We are treating the current https://theinternetparty.us deployment as the primary test vehicle. The harness + existing E2E suite is the instrument. The goal of this strategy is both to validate the current platform **and** to ruthlessly drive the changes that will make the Congressional Library experience trustworthy at real scale.

Run it. Measure it. Fix the bottlenecks it reveals. Repeat.

*This document is living — update it with every major test run and every architectural decision.*
