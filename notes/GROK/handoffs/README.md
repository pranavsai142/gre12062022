# handoffs/ — The Durable Memory Layer

Dated handoff documents are the **single source of truth** for project state that survives `~/.grok` flushes and travels with the repository.

> **2026-07-14:** Project **given up**. Prefer  
> [`2026-07-14-what-we-learned-give-up.md`](./2026-07-14-what-we-learned-give-up.md)  
> (learnings close — **no work to continue**) and the investigation archive over any pre-abandonment feature handoff.

## Naming

- `YYYY-MM-DD-<topic>-handoff.md`
- `YYYY-MM-DD-session-close.md`

## How It Works

- `/done` creates a new handoff at the end of meaningful work (or mid-plan checkpoints).
- A handoff usually contains: what was accomplished, key decisions, hard lessons, current focus, open questions, and what the next session should start on.
- A **give-up** handoff may instead carry only learnings and an explicit **no next build work** instruction.
- `/init` makes you read the most recent 1–3 handoffs + the two driver files.

## Important

The agent's own `plan.md` files (created during plan mode) stay in `~/.grok/sessions/...`. We do **not** copy them here. A handoff may optionally note the path if the full trace is useful later.

This directory + the three skills (`seed`, `init`, `done`) is the complete portable meta-system. Copy it to any project.