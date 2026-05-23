# handoffs/ — Session Memory & Context Transfer

This directory contains **dated handoff documents** produced by the `/done` skill at the end of productive sessions.

## Purpose

- Capture what was accomplished, why certain decisions were made, what remains open, and any context that would otherwise be lost when the chat session or agent thread ends.
- Provide the "what just happened" for the next human or agent who runs `/init`.
- Prevent re-deriving reality or overwriting prior work.

## Format (typical)

Each handoff is a markdown file with a timestamp + short session id in the name, containing:

- Summary of work done vs the active plan
- Key decisions & rationale (technical, UX, process)
- Updated status of todos / backlog items
- Any new hard-won lessons for `DEV_NOTES.md`
- Pointers to changed files, new artifacts, or tests
- Open items for immediate follow-up

## Lifecycle

- Written by `/done`
- Never manually edited after creation (treat as immutable record)
- When a major phase completes and its plan is archived, the related handoffs stay here as historical record (or can be summarized into `DEV_NOTES.md` if desired)

The existence of this directory + the `/done` ritual is what makes long-running, multi-session, multi-agent projects coherent without fragile external memory.

See sibling `ARCHIVE/` for completed plans and the parent `../README.md` for the operating system.