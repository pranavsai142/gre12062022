# ARCHIVE/ — Long-term Project History

This is the top-level archive under `notes/GROK/`.

It holds completed or retired artifacts that are no longer active drivers but are worth preserving for context, onboarding, or archaeology:

- Old comprehensive dev notes / vision dumps (e.g., the original `DEV_NOTES_AND_IMPLEMENTATION_STATUS.md` before it was seeded into the living `DEV_NOTES.md` + `SOUL_DRIVER.md`).
- Superseded architecture diagrams, old DB schemas, wireframes.
- Historical session summaries or large research dumps that have been distilled.
- Any other "we may need this later" material.

## Policy

- Do not let this become a junk drawer. Only move things here when they have been properly summarized or superseded in the living driver documents (`SOUL_DRIVER.md`, `DEV_NOTES.md`).
- Prefer distillation over raw storage: if a 400-line historical file can be reduced to two crisp paragraphs + a pointer in `DEV_NOTES.md`, do the reduction and archive the original.
- Git history is the ultimate backup; this is for convenient human/agent access.

The pragmatic meta system (`/seed` → `/init` → work → `/done`) is designed so that the *living* documents in the parent `GROK/` directory are always sufficient for an agent to become productive immediately. The archive exists for completeness and to honor the principle "never lose signal."

The previous `PLANNING/` structure (with its handoffs/ and ARCHIVE/) is now archived under `ARCHIVE/PLANNING/` as a historical snapshot of the old layout. All active session memory lives in the top-level `handoffs/`.