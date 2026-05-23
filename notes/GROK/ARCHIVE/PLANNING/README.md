# PLANNING — Active Plans & Session Work

This directory is the home for all **active planning documents** in the project.

## Contents

- `plan.md` (or numbered/ dated plan files): The current approved implementation plan(s) for the active phase or feature.
- `handoffs/`: Session handoff notes and summaries written by `/done` at the end of meaningful work. These capture decisions, rationale, open items, and context for the next session or agent.
- `ARCHIVE/`: Completed or superseded planning documents are moved here once a phase is truly finished and the work has been integrated. Never delete history — archive it.

## Workflow

1. When a new body of work begins (after `/init`), the agent or human creates or updates the active plan file in this directory.
2. During implementation, use `todo_write` (or equivalent) to track granular tasks against the plan.
3. At the close of a session or major milestone, run `/done`:
   - It updates the living driver docs (`SOUL_DRIVER.md`, `DEV_NOTES.md`).
   - Creates a dated handoff in `handoffs/`.
   - If the plan is complete, moves the plan file to `ARCHIVE/`.
4. Future sessions (or subagents) start by reading the drivers + the latest handoff + the active plan.

## Naming

- Keep plan files descriptive (e.g., `voting-engine-mvp.md`, `2026-05-polish-wp1-wp4.md`).
- Handoffs are auto-dated by the `/done` skill (e.g., `2026-05-21-019e4149-handoff.md`).

This structure ensures no plan state is lost in chat history or `~/.grok` memory. The repo itself is the durable source of truth.

See `../README.md` for the full pragmatic meta system overview.