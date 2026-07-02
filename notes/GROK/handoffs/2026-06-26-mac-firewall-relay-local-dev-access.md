# Session Handoff — 2026-06-26 - macOS Firewall + Persistent Local Dev Network Access

**Project:** The Internet Party (Party No. 3)  
**Focus:** Solved local dev server (PlotterApp/gunicorn) LAN access on macOS without disabling firewall. Shift to production + real development.

## Solution (The Technical Challenge)

macOS Application Firewall was blocking non-localhost traffic to the Python/gunicorn process on port 5000 (even after CLI whitelists and GUI entries). Localhost worked; LAN IP from other devices gave "Empty reply from server".

**The fix (relay approach):**
- Run gunicorn bound only to `127.0.0.1:5001` (localhost/internal).
- Use a tiny Node TCP relay (`node_relay.js`) listening on `0.0.0.0:5000` forwarding to the internal gunicorn.
- Firewall sees Node (already trusted via npx/serve) as the public listener → allows full network access.
- Firewall GUI entries can be deleted; no whitelist script needed.

This keeps the server always running and accessible on the local network with firewall ON.

## Ease of Use (What You Need)

- **Start local dev (PlotterApp only, network accessible):**  
  `export DATA_FOLDER=/your/path/with/cert` (if not default)  
  `./start_local_with_node_relay.sh`

  Starts: gunicorn internal + Node relay on 5000.  
  Access: http://127.0.0.1:5000 (localhost) or http://YOUR_LAN_IP:5000 (network).

- **Kill everything (rogue monitor, gunicorn, relay, ports 5000/5001):**  
  `./kill_all.sh`

- **Prod on Render (direct, no relay):**  
  `./start.sh` (or SSH and run it).  
  Uses gunicorn directly on $PORT. Monitor still backgrounded.

- **Node relay script (if running pieces manually):**  
  `node node_relay.js` (defaults: 5000 → 127.0.0.1:5001).  
  Override: `RELAY_PORT=5000 TARGET_PORT=5001 node node_relay.js`

**Workflow:** Use the relay script for local dev. It keeps a persistent server on the network. Firewall stays on.

## Prod vs Local + Changes

- **Will this be "live" (auto-reload like npx serve)?**  
  No. npx serve works for static files with built-in watchers.  
  This is a dynamic Python/Flask app.

- **Local (with relay script):** Persistent server always accessible on network. Code changes require restarting the script (no magic auto-reload). For hot-reload during pure dev, you can temporarily run `pipenv run flask run --host=127.0.0.1 --port=5001 --reload` + the relay if needed.

- **Production (Render):** Changes require redeploy (git push / Render build). Standard for web services. The app is not "live editing".

## Current State & Next

- Firewall challenge solved for local network dev.
- Prod uses proper gunicorn (no dev server).
- Ready for real development: enforce constraints, categories, public experience, etc. (see DEV_NOTES backlog).
- Keep using relay script locally for always-on network access during dev.

*Handoff created as part of /done on 2026-06-26.*
