# ARCHIVE/ (under PLANNING) — Completed Plans

When a planning document (plan.md or equivalent) reaches full completion — all work items verified, integrated, and the phase closed — it is moved from the parent `PLANNING/` directory into this `ARCHIVE/` subfolder.

## Why Archive Instead of Delete

- Project memory is durable. Old plans contain rationale that explains *why* the current code or architecture looks the way it does.
- Future agents running `/init` + reading `DEV_NOTES.md` can trace the history without digging through git.
- Legal, audit, or "what were we thinking" moments are preserved.

## Contents

Only finished, superseded, or explicitly closed plans go here. Active or in-flight plans stay in the parent directory.

Handoff notes that accompanied the work remain in `handoffs/` (they are session records, not plans).

## Maintenance

The `/done` skill is responsible for detecting completion and performing (or recommending) the archive move, while also updating the living `SOUL_DRIVER.md` and `DEV_NOTES.md` to reflect the new reality.

See parent `README.md` and `../ARCHIVE/` (top-level under GROK) for broader historical artifacts.