# The Internet Party (Party No. 3) - Dev Notes, Vision, and Implementation Status

**Project:** gre12062022 / The Internet Party  
**Location:** /Users/pranav/projects/gre12062022  
**Explored:** April 2026 (by Grok)  
**Git:** main branch, up to date with origin. Recent commits focus on amendments, account/my policies, drafts, DB ops, auth.

---

## PART 1: THE SOUL — VISION AND MISSION (Exact from Dev Notes)

> Party No. 3 (The Internet Party)
> The mainstream media still won’t capitulate anything regarding the 2020 election
>
> We need a parallel election system
>
> Party No. 3, The Internet Party
>
> Any human with access to the internet can join.
>
> Regular voting on party policies.
>
> What’s different? Policies will have word count limits. Policies are automatically sunsetted. 
>
> Candidates can sign on to the party
>
> The party will serve as accountability and a parallel system for the current US Election system 

### Platform
- **Truth**
- **Freedom**
- **Health**

"Party Number Three supports"

### Core MetaPolicies (Exact)
At any time, new ideas for policies or amendments to existing policies may be submitted using an online form. Weekly (on Sunday), an online voting procedure will take place to determine if an introduced policy has a majority vote to make it officially into the policy list. 

People are eligible to vote in the weekly election so long as they are registered members of The Internet Party. To be a registered member of the party one needs to supply a name and phone number from reputable carrier.

Electing a policy requires a quantity of votes equivalent to the majority of registered users of The Internet Party.

If a user does not vote for 3 consecutive weeks, he or she is dismissed from the party until they reactivate their account.

Policies expire after 365 days. As policies are reaching the end of their life, a vote will be held on if the policy should be extended for another 365 days.

Policy titles should be less than 100 characters.

Policy descriptions should be less than 10,000 characters.

### Example Policy Areas (from notes)
- First Amendment / Covid-19 Crisis: Audit Death Count, Research Vaccines, Serve RICO Case
- Criminal Justice Reform: Audit Police, End Prohibition of Drugs, Speed Class Action Lawsuits
- Economy/Jobs: American Basic Income (Liberty Dividend) — detailed vision on escaping poverty, individual liberty via money
- Standardize Employee Rights
- Education, Environment (microgrids, sustainable: Solar/Wind/Nuclear/etc.)
- Foreign Policy: Audit Foreign Aid (pie chart, spoiler: guns), End Imperial Violence (drones, bases, bring Americans home)
- Government Reform: Audit CIA (drugs/elections?), FDA, CDC (miracle cures?), NORAD (Cheyenne), Federal Reserve ("Fuck the Feds"), Pentagon (time travel?), TSA, End Patriot Act
- Healthcare, Immigration
- Voting/Legislation Reform: Character Count on Laws, Sunset Clause on every law, Let prisoners vote
- Women: First Lady elected position, renamed Madam President, more delegated work. "First Madam President: Rosanne Barr"

### Credits
Ron Paul, VA Shiva, Ayn Rand, Andrew Yang, Kanye West, Elon Musk, MF Doom, Rosanne Barr

### Other Aspirations
- Create Media Content: Youtube "Internet Party News", clipped from Infowars/Interviews/First hand/Text-to-speech
- Develop App: Multitabbed (Home, Current Policies, Vote) — "SEE META POLICIES. Base app of metapollicies."
- Growth section (empty in notes)

---

## PART 2: DEV LOG 2024 (Exact from Notes)

The project has been transitioned to a backend of pure python utilizing Flask.
Endpoints are created as functions, and the functions return an html string, that gets rendered using a special method
Via flask. The bottom line is all the html, css, javascript, all gone. Now all there is to create a webpage is an html string, (which can have css and javascript inside of it), and return that string as the return value of a python function.

10/25: To integrate database and authentication, firebase will be used. This requires some thought about the structure of the application. Flask is responsible for hosting endpoints that hit a python backend. This is the server. The server sends HTML render strings as responses to calls to the endpoints. It is sending these responses to the client side. 

For data retrieval tasks, the client side is not involved. The logic to call the firebase realtime database will be housed inside python. There is logic to authenticate the server using a certificate file. 

For authentication tasks, this requires the client side to do the processing. This is just how it has to be. The user is trying to log in, register, this information doesn’t need to come to the server at all. The only thing the server needs to serve is the html page that contains the sign in UI and button, plus javascript that upon click of a button, calls the firebase auth. 

Then there is a feedback loop. Upon a successful authentication, the javascript will send a post request to an endpoint hosted on the server side (Flask via Python). This endpoint is a token validation endpoint, as the client side will try and authenticate the user. If successful, it will get back a token. The token is encrypted and can be decrypted by the server side to validate it and retrieve the user id. Now the client side has user id information. Now the token can be held on to and passed around the app. 

The token has to be saved into a session. A session in Flask is a server side “cookie like” storage area that is specific to the client. Sessions are created client specific, a new one created for each time a client enters the app. They are also encrypted. So a session would be a good place to put the user id once it is retrieved. If a user id is in the session, then the user is logged in. If a user is not in the session, then the user is not logged in.

If a client is logged in, then the view pages that are rendered via the server will contain user specific information and user needed actions in them. If not, then it won’t show the user specific items.

Building Client Side:
The client side is initialized as a npm package using “npm init”. The package.json file is generated. The entry point set as index.js. ... What really matters is the webpack.config.js ...

Or, just use CDN’s defined in server side HTML render strings. Then call javascript file created in static/js. No need for client folder and client build.

... logic has been added to listen to a login button on the index page. When the button is pressed, the token is sent server side. Then the token is validated and the uid is saved in the session...

Separate the tasks of
1. Building all UI elements according to logical flow
2. Create visual theme (Can decide on the color of the drapes later)

**Key tasks remaining (develop in order of workflow)**

1. Add ballot generation function
    1. Generate a ballot items that contains all the acceptable candidates to be voted on. This is so anyone can see what would be on the ballot
    2. Generate a ballot for voting. This ballot is specific to the user and is not created if user already voted and if current time outside of voting block.
2. Add voting logic to tabulate ballot and promote eligible canidate policies to official policies.

Note: in this flow, the only place draft policies and amendments are accessed from

**Election Monitor TODO:**
Add state county graphs to election monitor

---

## PART 3: TASKS LISTS (Exact from Notes)

### Tasks: General
- Ensure site structure is circular with no dead ends
- Create about page
- Create site wireframe
- Consolidate CSS styles into importable python class
- Create User class to store user data in. (Parse and print functions) — "Just using decoded_token as “User” object. No need for extra complexity. Just directly reference the user json dictionary after saving into session."
- Create submit-draft endpoint to submit a draft. (Uses the submit candidate policy Database function)

### Login, Register, Reset, Account
- Create reset page using firebase auth
- Create account page (Add my policies button to access My Policies page)
- Add My Policies page (Contains status of all user submitted policies and amendments, and their current policy type. Accessible from account page. Contains link to draft page. Submit draft policies. Calls flask endpoint to submit policies for ballot.)

### Policy
- Create Policy class. (Add needed attributes: Title, submission date, content, history, amendment history, status [active, candidate, inactive, failed], submission user email)
- Create list to view candidate policies [Trending list]
- Create list to view active policies [Platform list]
- Create forum to submit amendments to existing policies [Draft, submitCanidateAmendment]
- Add categories for policies
- Create policy render string (Display all property attributes in a div)
- Create amendment viewing interface
- Add policy detail page (Add all policy metadata to policy detail page, including policyId. The policy detail page will serve to do operations on a policy. These only if the user is logged in: See user drafts, Edit and save a draft, Submit a draft to canidate, See, edit and submit amendment drafts. Create an amendment draft — New policy from draft page, new amendment from Policy Detail page.)

### Draft
- Modify forum for draft policy to save policy as well as submitting to draft. (Display a list on the side of Draft Policies that shows all of user’s draft policies. Clicking on one switches to editing that policy. Add save-draft flask endpoint. Create forum to submit draft policies [submitCanidatePolicy] [Adhering to metapolicies of Internet Party]. Create list of saved draft policies specific to user)
- Add policy amendment drafting

### Vote
- Create Vote class (House vote functionality. Data updates, getter functions for all available policies and amendments.)
- Create Ballot class (Ballot objects are created specific to the user. They can be saved in the session. Holds a list of policies eligible for vote, and how the user votes on each policy.)
- Create voting dashboard to vote on policies. [Active during voting events] (Display policies and amendments on the ballot. [Display a ballot] Get user voting option. Pay special attention to redundancy, security, and integrity)

### Database
- Add database error handling (For any functions that call database)
- Create submit candidate policy method (Fetches policy using getPolicy. Deletes policy in draft, recreates policy in canidates if eligible.)
- Add policy amendment structure
- Create getPolicies function (Take in optional parameters (data query, query limit, title query). Parameter to only return policies eligible for vote in upcoming session. Might end up being a collection of functions)
- Create getBallot function (Returns a ballot object list of policies eligible for vote instantiated to the user. If ballot has already been submitted in this voting session, then DO NOT CREATE BALLOT. Will use getPolicies functionality)
- Create setVote function (Takes as input an eligible ballot. Verifies its eligibility. Sets the vote based on the ballot. If it fails act accordingly. If it succeeds, mark the user as having voted.)
- Create data structure for voting policies where which way each voter voted is saved. (A dictionary with the user id and voting status integer)

### Notes (Exact)
- Firebase authentication via phone number: https://firebase.google.com/docs/auth/web/phone-auth?hl=en&authuser=0
- Firebase real-time database structure
  - policies: Title, description, enactment date, expiration date, authorId, amendments [list of amendment ids]
  - proposedPolicies: same fields as above without enactment or expiration date, voting date, votingId
  - proposedAmendments: same fields as below, voting date, vote total yay, vote total nay, vote total abstain, votingId
  - amendments: Policy id, authorId, diff, 
  - elections: VotingId, [amendment or policy ids], voting start datetime, voting end datetime

### Dev Log (Commands)
- To run emulator: firebase emulators:start --only auth
- to package: npx webpack
- to serve: serve dist

### Dev ToDo (older)
- Add account page
- Add sign out button
- Add register page
- Add reset password page
- Create ballot and policy class structure

### ToDo Develop Website (features)
Features: login, register, mandatory orientation video during registration., view enacted policies, view policies to be voted on, draft a new policy to be voted on, submit an amendment that modifies an existing policy (amendments must be voted on). Vote on policy during Election Day. (Ensure user only submits 1 vote.) (have live vote total tracking).

### Develop App
- Multitabbed app... (Home, Current Policies, Vote)

---

## PART 4: DONE (Exact from Notes)

- Create login javascript file
- Create register javascript file
- Create a menu to navigate site structure
- Create sign out button (Delete session data)
- Create register button
- Create realtime database in firebase
- Create login page using firebase auth
- Create register page using firebase auth
- Create Policy class. (Create Policy object that will contain policy attributes.)
- Create saved draft policies specific to user and upload to database
- Add policy detail page (Policy cards in policy page hyperlink to a policy detail page for that policy. Create policy detail endpoint that has parameter policyId. Add created and updated timestamp)
- Create getPolicy method (Takes as input policyId and retrieves from database)
- Create submitPolicy function (Submits a policy from draft. Validates the policy. Returns error codes if did not succeed)

---

## PART 5: MY FINDINGS — REPO EXPLORATION AND CURRENT IMPLEMENTATION STATUS (April 2026)

### Overall Architecture (Matches Dev Log Exactly)
- **Pure Python + Flask backend**: All "pages" are Python modules (e.g., IndexPage.py, PolicyPage.py) exporting a `render(user)` function that returns a full HTML string via `render_template_string(...)`.
- **No separate frontend build for core app**: Uses Firebase JS via CDN in HTML strings + static JS files in `/static/js/`. (No client/ webpack folder active in current source; notes discuss both approaches, current uses CDN+static.)
- **Auth flow exactly as described**:
  - Client: Firebase email/password (login.js, register.js) + onAuthStateChanged → POST /validate-token with ID token.
  - Server (PlotterApp.py:210): `auth.verify_id_token()` → `session["user"] = decoded_token`.
  - User object = raw decoded_token dict (see User.py: simple validateUser checking exp).
  - Logout: `session.clear()`.
- **Firebase Realtime DB** (admin SDK, cert at /data/theinternetparty-5b902-....json):
  - Structure in use: `policy/draft/`, `policy/canidate/`, `policy/official/`
  - Parallel: `amendment/draft/`, `amendment/canidate/`, `amendment/official/`
  - Matches notes' intent (draft → candidate → official) but uses "canidate" spelling everywhere (typo preserved), and "policy/" not "proposedPolicies".
  - No `elections/`, no voting tallies, no "proposedAmendments" collection yet.
- **Main entry**: `PlotterApp.py` — defines ALL routes, Firebase init, session secret, plot generation, monitor pages, + all party endpoints (/draft, /detail/<id>, /account, /vote, /validate-token, CRUD for drafts/amendments, etc.).
- **Dual-purpose app**: 
  - Internet Party platform (the soul).
  - 2020/2022-era election data monitors and live-ish plots (PresidentMonitor.py, ElectionMonitor.py scraping Reuters/ABC?, state data dirs like co/, ga/, az/ with demResults.txt/repResults.txt/countyResults.json, /monitor/<state> + /plot + /delta routes in PlotterApp).
  - This aligns with the "2020 election" motivation for a parallel system.

### Repo Structure
```
. 
├── PlotterApp.py          # THE APP (routes + Firebase + plots)
├── Database.py            # All get/create/update/submit for policy/amendment (draft/canidate/official)
├── Policy.py              # Class with DRAFT/CANIDATE/OFFICIAL, validateFor*, toDict, timestamps
├── Amendment.py           # Parallel class, with policyId link
├── User.py                # Minimal: validateUser() on decoded_token exp
├── *Page.py (14 files)    # Index, About, Account, Login, Register, Reset, Policy, Draft, DraftAmendment, Detail, DetailAmendment, Vote, NotFound
├── static/js/             # login.js, register.js, draft.js, detail.js, draft-amendment.js, detail-amendment.js
├── az/ co/ ga/ il/ pa/ ri/ ... # Election data dirs (results + county json)
├── chrome_install/        # Full portable Google Chrome (~for headless scraping in monitors)
├── PresidentMonitor.py, ElectionMonitor.py, Plotter.py # Data collection + viz
├── start.sh / stop.sh / kill_process.sh
├── requirements.txt (Flask, firebase-admin, matplotlib, etc.)
├── Pipfile / data.tar.xz / logs
└── (No package.json/webpack active for main app; no .env or firebase key in git)
```

**Site navigation**: Every page has identical menu bar + footer ("Brought to you by The Internet Party / Powered by Grok"). Links: Policy | About | Home | Vote | Account/Login. Detail pages, draft amendment, logout available contextually. Mostly circular; some dead-ends if not logged in (redirects in Account).

### Status Mapping (Tasks vs Reality)

**DONE (or largely done, per "Done" list + more):**
- Login/Register JS + pages with Firebase CDN + token validation + session (exact flow).
- Menu on every page.
- Sign out (logout route clears session).
- Realtime DB + Policy/Amendment classes + timestamps (created/updated/submitted) + getPolicy.
- Draft policies: create/update/remove/submit endpoints + UI in DraftPage + side list + DetailPage for drafts (edit/save/remove/submit).
- Account page: exists, shows grouped My Policies/Amendments by status (draft/canidate/official) for the logged-in user. Links to detail/draft-amendment. Has logout.
- Policy page: Lists Candidate Policies/Amendments + Official. Hyperlinks to /detail/<id> and /detail/amendment/<id>.
- Detail page: Full metadata + conditional UI (draft form vs read-only canidate/official). Amendment drafting link from canidate policy.
- Amendment full parallel flow: DraftAmendmentPage, DetailAmendmentPage, dedicated endpoints/JS/DB functions (create/update/remove/submit for amendments).
- submit-draft endpoint + DB submitDraftPolicy (moves draft→canidate, owner check).
- Policy detail has policyId displayed.
- Some visual consistency (orange #ff6600 accents, "Grok" footer).

**PARTIALLY IMPLEMENTED / EVOLVED:**
- "Create account page" + "My Policies": Account page *is* the My Policies view (no separate /my-policies route yet, but all status lists + links to draft are there). Notes wanted "Add my policies button to access My Policies page" — currently embedded.
- Policy class: Has core attrs (title, desc, userId, type, timestamps). Missing per notes: "history, amendment history, status [active,candidate,inactive,failed], submission user email". No categories. No word-count enforcement (meta: <100 title, <10k desc).
- Draft forum: Has save + side list of user's drafts (links to detail for edit, not "click switches editing in place" exactly, but functional via detail). No "save as well as submitting" unified yet in one form.
- Amendment drafting: Fully wired from policy detail → /draft/amendment/<policyId>.
- "Consolidate CSS": Not done — every single *Page.py duplicates ~50-80 lines of identical <style> (body flex, menu, footer, .content, .menu-item etc.). Huge tech debt.
- User: No full class with parse/print; just the validator + raw dict in session/templates. Matches the note's final decision ("Just using decoded_token...").
- Site structure: Mostly circular via persistent menu. No dead-ends for core flows if logged in. About/Vote/Reset are stubs. Monitor has 404 for bad states.
- "Create about page": Exists but empty stub ("<h2>About</h2>").
- "Create submit-draft endpoint": Yes, /submit-draft + DB logic.
- DB: Many getters (per-type + per-user filtered). submitDraft* logic with ownership validation. No general getPolicies(query, limit, title, "eligible for vote") yet. No error handling wrappers around db calls.

**NOT STARTED / KEY REMAINING (from "Key tasks remaining" + full lists):**
- **Voting / Ballot core (highest priority per notes)**: 
  - VotePage.py: Complete stub (just menu + "Vote" + footer). No dashboard.
  - No Vote class, no Ballot class.
  - No /getBallot, setVote, voting data structures (userId → vote status dicts).
  - No promotion logic from canidate → official.
  - No "eligible for vote in upcoming session", no weekly Sunday timing, no "only one vote per session", no live totals, no "if already voted this session → no ballot".
  - No elections/ collection, no vote totals on amendments/policies, no "tabulate and promote".
  - Meta: majority of *registered* users (current auth is email, notes wanted phone+name from carrier; no registration metadata stored).
- **Ballot generation**: None. "Generate a ballot items that contains all the acceptable candidates to be voted on" (public view) + user-specific.
- **Reset password**: Page exists (stub), no Firebase password reset UI/JS. Notes explicitly call for it.
- **Policy enhancements**: No categories, no amendment history on policies, no "Trending list" vs "Platform list" distinction beyond current canidate/official, no "policy render string" as separate, no visual "forum" for amendments beyond the draft page.
- **Enforcement of MetaPolicies**: No char limits, no 365-day sunset/renewal votes, no inactivity dismissal (3 weeks no vote), no mandatory orientation video on register.
- **Election Monitor**: /monitor/<state> + plots work (timeseries + delta for Dem/Rep). **TODO exact**: "Add state county graphs to election monitor". County data exists in some dirs (countyResults.json) but not visualized in the Flask monitor pages.
- **DB hardening**: No try/except wrappers on all db.reference calls.
- **Visual theme**: Basic Arial + orange accents + "Grok" footer everywhere. "Decide on color of drapes later" — still true. No wireframe doc.
- **"Create site wireframe"**: Not present as artifact.
- **Phone auth**: Not implemented (email/password only). Notes link to phone docs.
- **App (mobile) + Media (YouTube)**: Not in this repo (website focus now).
- **"submitCanidatePolicy" in DB**: Exists (stubby, has bug: always creates new uuid instead of using existing), unused.
- **"Ensure site structure is circular"**: Good enough via menu, but Vote/Reset/About are dead-ends for features.

### Additional Observations from Code
- Spelling: Consistently "canidate" (not "candidate") in classes, DB paths, UI, routes. PolicyType strings: "draft", "canidate", "official".
- Security/Integrity notes in todos ("Pay special attention to redundancy, security, and integrity" for voting) — nothing implemented yet; current draft submit has basic owner checks via validateFor*.
- Error handling: Minimal (many endpoints return generic "Server error! Something smells like fish..").
- Logging: Some print() in DB/PlotterApp.
- No "history" or "diff" for amendments (amendments store full title/desc snapshot, not diff as in old DB spec).
- Templates hardcode full <!doctype html> every time — no layout inheritance.
- Static assets: Only the 6 JS files + implicit Flask static.
- Chrome bundle + monitors: Functional for live election data collection (2020 skepticism roots of the project).
- "Mandatory orientation video": Nowhere.
- "Let prisoners vote", "First Madam President: Rosanne Barr" etc.: These are aspirational platform text, not yet in any /policy or /about content.

### Firebase DB Expected vs Actual
Notes spec had top-level collections with specific fields + votingId/yay/nay etc.
Current: Nested policy/{type}/{id} and amendment/{type}/{id} with the fields that Policy/Amendment classes serialize (userId, type, title, description, timestamps, + policyId for amendments).
Elections/voting not present. "proposedPolicies" not used (draft/canidate serve that role).

### How to Run (from code + notes)
- `pipenv shell && pipenv install` or pip install -r requirements.txt
- Need Firebase service account at /data/theinternetparty-5b902-firebase-adminsdk-....json (or edit DATA_FOLDER)
- `python PlotterApp.py` (serves on 0.0.0.0:5000)
- Monitors via start.sh (scrapers + app)
- For auth emulator (notes): firebase emulators:start --only auth (but app uses prod admin verify)
- No npm/webpack step active for the party site (CDNs used).

### Technical Debt & Soul vs Implementation Gap
The **soul** (parallel direct-democracy party with strict, self-sunseting policies as 2020 accountability tool) is alive in the architecture (draft→canidate→official flow, user-owned content, amendment support, account transparency) and branding.
But the **heart of the vision** — the actual *voting*, ballot, weekly majority-of-registered, sunset/renew, char limits, phone registration, live transparent tallies, promotion to official — is completely missing. The site currently lets people *propose and discuss* policies/amendments in a logged-in workspace, but has no *governance engine*.
Election monitor side is more mature (plots for multiple states) but missing the called-for county graphs.
CSS duplication and lack of theme make it feel like scaffolding, not a polished "Party No. 3" presence.

This matches the notes' own framing: "It’s all coming together. What is left now is a long series of ‘micro’ tasks that compound on each other." The micro-tasks for auth/draft/detail/account/amendments *are done*. The macro (ballot + vote + promotion + metapolicies enforcement) remain.

---

## PART 6: VOTING MVP — FULLY IMPLEMENTED (April 2026)

**This was the #1 remaining priority from the original dev notes.**

All of the following are now complete and wired end-to-end (draft → canidate → ballot → one immutable vote per ISO-week window → manual tally + promote to official):

- `Vote.py` — Vote class (the persisted "dictionary with the user id and voting status" the notes demanded, plus `computeTallies` + `getWinners`).
- `Ballot.py` — Ballot presentation object (public + per-user, with `toSessionDict` hook exactly as requested).
- Database additions: `getCurrentVotingWindowId()` (ISO week), `getBallotItems()`, `getBallotForUser()`, `hasUserVotedInWindow()`, `recordUserBallot()` (the `setVote` equivalent with full re-validation for integrity), `getWindowTallies()`, `promoteWinnersFromWindow()` (tabulate + copy canidate → official + delete from canidate).
- Two new endpoints in PlotterApp.py: `POST /submit-ballot` and `POST /close-window` (exact same JSON/session/"smells like fish" pattern as draft routes).
- `/vote` page is now a complete, first-class dashboard:
  - Always-visible public ballot (anyone can see what is eligible).
  - Logged-in users who have not voted this window see live radio buttons (Yes / No / Abstain) per item.
  - Tallies shown under every item.
  - "Cast My Ballot" button + JS collector + double-confirm.
  - "You already voted" + your choices state.
  - "Close Window & Promote Winners" operator button (yes > no rule per plan).
- `static/js/vote.js` — matches every other interactive JS file in the project.
- Cross-page notices added to PolicyPage + AccountPage ("Active ballot this week — go vote").
- New RTDB paths (additive, audit-friendly):
  ```
  voting/{windowId}/
      participation/{userId}
      votes/{userId}   ← full choices dict per voter
  ```
- Zero changes to existing draft/submit/detail/account flows. "canidate" spelling preserved everywhere.

The governance loop (the actual heart of Party No. 3) is now functional. A logged-in member can:
1. Draft a policy/amendment
2. Submit it to canidate status
3. See it appear on the live ballot at /vote
4. Cast one immutable vote for the ISO week
5. Watch tallies
6. Trigger promotion → the winner appears under Official on /policy

All decisions (window = ISO week, promotion threshold, immutable vote, manual close for v1, etc.) are documented in the session plan file.

---

## PART 7: REMAINING WORK (Prioritized per Notes' "develop in order of workflow")

(The original #1 is done. These are the logical follow-ons.)

1. Enforce meta constraints in Policy/Amendment creation (title <=100, desc <=10000 chars) + UI hints.
2. Add categories/tags to policies.
3. Flesh out About page with full platform text + MetaPolicies + credits.
4. Reset password + phone auth option.
5. Consolidate CSS into a shared Python string/class.
6. Add "My Policies" as dedicated page or prominent button from Account (currently embedded).
7. Election monitor: render county graphs using existing countyResults.json files.
8. DB error handling + rate limiting on votes.
9. Later: proper Election documents (start/end + explicit item snapshot), registered user count, Sunday-only gating, 3-week inactivity dismissal, 365-day sunset votes, etc.

3. Add categories/tags to policies.

4. Flesh out About page with full platform text + MetaPolicies + credits.

5. Reset password + phone auth option (or document shift from phone to email).

6. Consolidate CSS into a shared Python string/class (e.g., Styles.py or base template logic).

7. Add "My Policies" as dedicated page or prominent button from Account.

8. Wire public "ballot preview" (what's eligible to vote on, even for non-logged-in?).

9. Election monitor: render county graphs using co/countyResults.json etc.

10. DB error handling, input validation, rate limiting on votes.

11. Later: wireframe doc, visual theme (colors, typography for "Truth Freedom Health"), app, media channel, actual weekly election scheduler.

---

*This document exactly reproduces the user's provided dev notes/vision/todos (soul + technical) and maps them to the live codebase as of exploration. The Internet Party project has solid scaffolding for proposal workflows and a compelling "why". The revolutionary part — the actual parallel voting engine — is the exciting work ahead.*

**Generated from full repo exploration (all .py, static/, data dirs, git, structure) + user's pasted notes.**

---

## Post-Voting-Engine Phase (May 2026) — Dev Tools, Admin Console & Public Polish (Approved Plan Implementation)

**Per the approved plan (plan.md in session 019e4149...):**

- **Dev Tools** (`dev_tools/`):
  - `pipenv run prefab serve dev_tools/dev_dashboard.py` (beautiful visual dashboard with live/snapshot data).
  - `python -m dev_tools.cli` (primary agentic/CLI interface — real mutations):
    - `list-windows`
    - `seed --window 2026-W21 --count 5`
    - `clear --window XXX --confirm`
    - `simulate --window ...`
    - `promote --window ...`
  - Package structure: `__init__.py` + `cli.py` + `dev_dashboard.py` + fixed `spike.py`.
  - All actions delegate to new helpers in Database.py + centralized `ensure_firebase_initialized()`.

- **Admin Console** (`admin/`):
  - `pipenv run prefab serve admin/admin_console.py`
  - "God view": windows history + per-window full vote audit tables, current ballot, official platform, raw stats, operator action cards pointing to the CLI.
  - Sidebar-style navigation section + drill-down via searchable tables + latest-window details.

- **Public Website**:
  - Home, About (full MetaPolicies + mechanics), Congressional Library (Policy with search/filters/cards), polished Account — all brought to the same quality as the delivered VotePage.

**Centralized Firebase init** added to Database.py to eliminate repeated `initialize_app` warnings.

**Runnability**: All tools now launch end-to-end. CLI performs real DB mutations. Prefab UIs are rich visual + exact command surfaces.

**2026-05-20 run (IMPL 4229ea13)**: Per explicit user feedback, the *main website* (/account Operator Tools panel) is now the canonical live, real-time control surface for everything (windows, ballot, tallies, seed/clear/promote). Login/Register fully revamped to production card+form standard. Amendment detail now shows original policy text *under* the proposed change for every status. Prefab/CLI remain excellent secondary tools but with updated docs that put the website first and give crystal-clear one-command instructions. "Just open the site and do it" is now true.

See `/tmp/grok-impl-summary-4229ea13.md` for the full changed-files + operator run instructions for this delivery.

**Next backlog items remain the older ones above (CSS consolidation, etc.).**

---

## CURRENT OPEN POLISH & CORRECTNESS ITEMS (Documented per user request — May 2026)

**User explicitly asked:** "Id suggest documenting these in a todo, i hope you do that without me asking."  
These four items were captured during the planning turn that put the agent into plan mode for orientation. They are the immediate follow-up work after the Login/Register revamp + live Operator Tools surface on /account.

**Status legend:** Open | In Progress | Fixed | Wontfix

### 1. Amendment Detail page — Remove duplicate Targets/Original box + fix title typography
- **Files:** `DetailAmendmentPage.py`
- **Exact user feedback:** Keep the nice grey "Targets Policy" box (preview of existing policy). Remove the second "Original Policy Text" box that appears for draft / canidate / official. Place the single Targets Policy box **below the amendment description**. Title of the amendment must be bigger/bolder/black than the "Amendment Detail" label; keep the grey treatment for the target policy part.
- **Why it matters:** Current page has visual duplication and weak title hierarchy. The single box + proper typography gives the clean "before/after" experience when viewing any amendment.
- **Status:** Open
- **Related plan work package:** WP1

### 2. Login screen — Error message box should be conditional
- **Files:** `LoginPage.py` + `static/js/login.js`
- **Exact user feedback:** "there is always that box showing an error message on login. that box should only come if there is an actual error message."
- **Current problem:** `#errorMessage` is rendered with `display:block` + `min-height` even when empty.
- **Acceptance:** Fresh page load shows no box. Only a real failed login attempt (Firebase error or server) makes the red error box appear with text.
- **Status:** Open
- **Related plan work package:** WP2

### 3. Operator / Admin action buttons — Result box only for real messages + proper feedback text
- **Files:** `AccountPage.py` (the 🛠️ Operator & Dev Tools live panel)
- **Exact user feedback:** For actions like "Reset Specific User Votes", leaving the input blank (or cancelling the prompt) still makes the result box appear (often blank). "its ok to have the box we just dont want it to show up blank only show it if there is actually a message and if you have to create messages for these cases i am doing in the admin buttons specifically"
- **Current problem:** `showOpResult()` forces the box visible; some paths produce empty or technical strings.
- **Acceptance:** Blank/cancel paths never surface the box. Every real operator action (seed variants, clear, promote, reset-user) always produces a clear, human-readable one-line success or error message. The box only becomes visible when it has content.
- **Status:** Open
- **Related plan work package:** WP3

### 4. Policy Detail page revamp — Clean amendment history + candidate amendments sections for official & canidate policies
- **Files:** `DetailPage.py` (+ possible small helper in `Database.py`)
- **Exact user feedback (condensed):**
  - "revamp the policy detail page. For official or canidate policies, we need to make it cleaner to see the amendment history on the same page."
  - For official policies (main text already updated by enacted amendments): show history so users can click an amendment and "see the diff properly" on the amendment detail page.
  - "If an official policy has a canidate amendment then put that there too… a section still at bottom of page but above the history section with official amendments. this can be the canidate amendments section."
  - "for canidate policies, they can also have amendments. obviously they can only have canidate amendments."
  - "pressing on an amendment will just take you to detail page."
  - "maybe also implement the diff i was talking about correctly."
- **Current state:** DetailPage is still the old bare-bones version. No amendment lists or history at all.
- **Acceptance criteria:**
  - Official policy detail shows: current (post-enactment) text + "Pending Candidate Amendments" section (if any) + "Amendment History" (enacted amendments on this policy).
  - Canidate policy detail shows its related canidate amendments.
  - Every listed amendment is a nice clickable entry that lands on `/detail/amendment/<id>`.
  - The cleaned-up amendment detail page (item 1) provides the practical diff view via the single "Targets Policy" box placed under the amendment text.
- **Status:** Open
- **Related plan work package:** WP4

**Notes for implementers**
- Keep the "canidate" spelling everywhere.
- Match the exact recent visual language (`.detail-header`, `.detail-card`, `.target-policy` grey box, status pills, orange #ff6600 accents, action bars).
- Preserve all legacy form IDs and JS contracts on detail pages.
- After each item is fixed, update its Status line in this section to "Fixed" with the date and brief note.
- This section lives at the end of the file so it is the single source of truth for the current user-driven polish backlog.

**Plan file for this work:** The session plan at `.../019e4149-.../plan.md` was fully rewritten during this planning turn to reflect exactly these four items (old plan was from an earlier diff/CLI phase and is now superseded for orientation).

---

**End of current documented todos.** When the user says an item is done, mark it Fixed here and (if desired) run a short verification pass.
