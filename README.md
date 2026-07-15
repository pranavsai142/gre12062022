# gre12062022 — The Internet Party

> **STATUS: DEMO OF AN ABANDONED MISSION (2026-07-14)**  
> Party No. 3 as a real national parallel government is **given up**.  
> The software stays online so people can **see the idea and use the mechanics** — only after a **forced fair-warning disclaimer**.

## What visitors experience

1. **First hit** → `/disclaimer` (cannot skip).  
   Long page with the sociological revelations from the give-up conversation, concrete failure examples, and **required checkboxes** (process without power is a simulation; software is optional polish; two-party lock-in; power is not crowdsourced; no single online demos; demo-only).
2. **After accept** → full site (vote, drafts, library, login, operator tools) works as a **sandbox demo**.  
   A sticky banner remains: *Demo of an abandoned mission…*
3. Optional hard tombstone: set `PRODUCT_DISCONTINUED=1` (410 writes + shut-down HTML only).

## Public-facing give-up (the point of the disclaimer)

The owner concluded:

- **Parallel process without parallel power is a simulation.**
- **Software is optional polish** on associations people can already form.
- **Industrial two-party lock-in** is structural; an app does not repeal it.
- **Power is not crowdsourced** from a website.
- The **open internet is not one demos** — universal “one party” fragments.

Full write-up: [`notes/GROK/SOCIETAL_GIVE_UP_INVESTIGATION.md`](notes/GROK/SOCIETAL_GIVE_UP_INVESTIGATION.md)  
What-we-learned handoff: [`notes/GROK/handoffs/2026-07-14-what-we-learned-give-up.md`](notes/GROK/handoffs/2026-07-14-what-we-learned-give-up.md)

Sibling **TheInternet** dojo is still documented as abandoned (no agent-training mission for Party No. 3 at scale).

## Local run

```bash
export DATA_FOLDER=/path/to/your/firebase-cert-dir
./start_local_with_node_relay.sh
```

Open http://127.0.0.1:5000 → forced disclaimer → then explore.

Env knobs:

| Variable | Default | Meaning |
|---|---|---|
| `FORCED_DISCLAIMER` | `1` | Session gate on `/disclaimer` |
| `PRODUCT_DISCONTINUED` | `0` | `1` = hard tombstone (no demo) |

## Production (Render)

Same as before: Blueprint / `start.sh` / Secret File for Firebase.  
After deploy, humans hit the disclaimer first; `/healthz` stays probe-friendly (`forced_disclaimer: true`).

## Historical architecture

See `notes/GROK/SOUL_DRIVER.md` and `notes/GROK/DEV_NOTES.md` (mission closed; demo retained). Secondary tools: `python -m dev_tools.cli --help`.
