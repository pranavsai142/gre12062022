# DEV_NOTES — The Internet Party (Living Project Reality)

**Last major update:** 2026-07-14 — **FULL GIVE-UP / PRODUCT DISCONTINUED.**  
Public site is a shut-down surface. Mutators return 410. Sociological archive: `SOCIETAL_GIVE_UP_INVESTIGATION.md`. Sibling **TheInternet** abandoned in parallel.

## Current Big Picture

**The Internet Party is abandoned.** Do not plan features, NPC scale runs, MetaPolicy deepenings, or categories/tags as if the party were operating.

What remains:

- **Shut-down UX:** `ShutdownPage.py` + `product_status.PRODUCT_DISCONTINUED` (default on) + `PlotterApp` `before_request` gate.
- **Archival code:** Domain modules (`Database.py`, `*Page.py`, voting engine) still in tree for history; not an invitation to run a live polity.
- **Investigation archive:** `notes/GROK/SOCIETAL_GIVE_UP_INVESTIGATION.md` — societal realizations, key conflicts, exploration pathway.
- **Handoffs:** Pre-2026-07-14 handoffs describe how the engine was built; they are historical, not a backlog.

### Key realizations that closed the project

1. Parallel process without parallel power is a simulation.  
2. Software is optional polish on real-world associations.  
3. Industrial two-party lock-in is structural; tech is not the unlock.  
4. Power is not crowdsourced from a blank website.  
5. There is no single online demos (fragmentation into many “internet parties”).  
6. Respect for real constitutional pathways conflicts with cosplay legislature claims.

## Hard-Won Lessons (Still true; mission closed)

- **"canidate" spelling** remains in historical code — do not mass-rename if inspecting archives.
- **Never random Flask secret_key with multi-worker gunicorn** — still true for any future Flask app.
- **Testing layer was the delivery gate** while the product was live; under give-up, tests assert discontinued behavior.
- **Context discipline** (`/init` + `/done` + handoffs) remains good practice; this give-up is recorded so agents do not “revive” the party by default.

## Information Architecture (Archival)

- `PlotterApp.py` — app entry; discontinued gate is first-class.
- `product_status.py` / `ShutdownPage.py` — give-up surface.
- `notes/GROK/SOCIETAL_GIVE_UP_INVESTIGATION.md` — why we stopped.
- Historical: `Database.py`, domain classes, `*Page.py`, `static/js/`, `npc/`, `tests/`.

### How to “run” (shut-down only)

```bash
./start_local_with_node_relay.sh
# Serves discontinued HTML. Writes return 410.
```

`PRODUCT_DISCONTINUED=0` is forensic-only.

## Next / Forward Backlog

**None for Party No. 3.** Closed items and old backlog are not active.

Optional owner-only ops (not product work): tear down Render/Firebase/domain when ready — see external assets checklist from the give-up session scratch if present; document in handoffs if done.

## Historical Note

Prior DEV_NOTES tracked a live governance engine and production readiness (2026-07-02–10). That chapter is over. Read `handoffs/` for how it was built; read `SOCIETAL_GIVE_UP_INVESTIGATION.md` for why it was given up.

---

*If you are an agent after `/init`: the project is discontinued. Do not implement voting features. Point humans at the investigation archive.*
