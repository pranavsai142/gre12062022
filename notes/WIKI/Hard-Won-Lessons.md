# Hard-Won Lessons (Code & Process Level)

These are the painful, repeatedly re-learned truths that the wiki exists to prevent future sessions from rediscovering.

## 1. Conditional Feedback Is Non-Negotiable for Operator Trust

Empty result boxes or always-visible error containers destroy the feeling that "I can just open the site and control the election cycle."

**Rule**: Result/error containers start hidden or empty. Only populate and show them when there is actually content. The 2026-05 polish round made this systematic across login, operator actions, and form submissions.

## 2. Harden Text Containers on First Sight of Long User Content

User-generated titles and descriptions will eventually contain long words, URLs, or deliberate unbroken strings. The first time layout broke on a card, ballot item, or diff, we added:
- `word-wrap: break-word`
- `white-space: pre-wrap`
- `overflow-x: auto`

Do this proactively on any new container that will display arbitrary user text.

## 3. "canidate" Is Not a Bug — It Is Project History

See Architectural-Decisions.md and DEV_NOTES. Attempting to normalize the spelling will cause widespread breakage and erase legitimate history. Preserve it religiously.

## 4. Small, Focused, Verifiable Increments Win

The voting engine, the major public UX overhaul, the diff experience, the operator panel, and the 05-22 polish round were all delivered cleanly because they were broken into explicit work packages with acceptance criteria and `todo_write` tracking.

Big speculative refactors have historically produced more mess than progress on this project.

## 5. The Website Operator Panel Is the Real Surface

Documentation, mental models, and agent tooling must treat `/account` (after login) as primary. CLI and prefab are powerful supplements, not the blessed path.

## 6. Choice Normalization War (int vs str, missing keys)

Early seed buttons returned "Invalid choice" because of type mismatches between frontend strings and backend expectations. The fix (normalization in both places + defensive defaults) only landed after the bug was hit in real operator use.

**Lesson**: On any voting-related surface, normalize early and defensively default missing items to ABSTAIN.

## 7. The "fish" Error String

The placeholder "Server error! Something smells like fish..." appears in many places. It is a deliberate, memorable marker. When you see it in logs or UI, treat it as "we hit the generic catch-all path" and improve the specific error handling.

## 8. Context Discipline via /init + /done + notes/GROK/ + This Wiki

Without the ritual and the durable layer, every new session (human or agent) wastes tokens re-deriving the window override, the promotion rule, the "canidate" convention, the primacy of the website surface, the exact RTDB shape, etc.

This wiki + the GROK drivers + rich handoffs are the mechanism that makes multi-month, multi-agent work on a complex governance system feasible.

## 9. Snapshot Fallback Is a First-Class Feature

Every tool, dashboard, and future simulator must run gracefully when the private Firebase admin JSON is absent, using the database_snapshot. This is what makes the project portable and agent-friendly across machines.

---

Add to this list whenever a session produces a "never again" moment. Link the new lesson back to the specific code paths or handoff that revealed it.