# gre12062022 — The Internet Party

Production-grade repo for The Internet Party (parallel direct democracy platform).

> **LOCAL DEV ON macOS?**  
> **Always use `./start_local_with_node_relay.sh`** (see below).  
> **Do NOT run `./start.sh` locally** — it is only for production deploys (Render etc.).

## Quick Start

### Local Development (macOS — recommended)
Keeps the server persistently running and reachable on your LAN while the macOS firewall stays ON.

```bash
export DATA_FOLDER=/path/to/your/firebase-cert-dir
./start_local_with_node_relay.sh
```

Then visit:
- http://127.0.0.1:5000 (localhost)
- or the LAN IP printed by the script (e.g. http://192.168.x.x:5000)

This is the **only** command you should use for day-to-day work on this machine.

### Production (Render)

The repo includes a `render.yaml` **Blueprint** and `runtime.txt`.

**Critical: `render.yaml` is only used if you deploy via Blueprint.**

If you created the service as a normal "Web Service" (most common reason the file isn't picked up), Render ignores `render.yaml`. You have to set Build/Start/Env manually, and pushing changes to `render.yaml` does nothing for an existing manual service.

#### How to actually use render.yaml
1. In Render: **New → Blueprint**
2. Select this repo
3. It will read `render.yaml` and create the service with the correct settings.

For an existing service:
- You can try linking it to the blueprint, or
- Delete the service and recreate it via the Blueprint flow (re-attach the secret file after).

While using a manual Web Service (what many people end up with):
- Manually set these in the service **Settings**:
  - Build Command: `pip install --upgrade pip && pip install pipenv && pipenv install --deploy --ignore-pipfile`
  - Start Command: `./start.sh`
  - Add env vars as needed (see below)

`runtime.txt` is respected even on manual services and helps with Python version.

#### Recommended env vars / settings
- `DATA_FOLDER=/etc/secrets/`
- `PYTHON_VERSION=3.13` (or use the dashboard Python version selector)
- `OPERATOR_EMAILS=you@ex.com,friend@ex.com` (comma-separated; locks operator actions to these accounts. If unset, any logged-in user can use the /account operator panel.)
- Other values from `render.yaml` (WEB_CONCURRENCY, GUNICORN_THREADS, etc.)

#### Secret File (always manual)
- In the service dashboard, add a **Secret File** with the **exact** name:
  ```
  theinternetparty-5b902-firebase-adminsdk-qlzzx-3864b82b40.json
  ```
- This gets mounted at `/etc/secrets/`.
- Must set `DATA_FOLDER=/etc/secrets/`

#### Deploy & Verify
- Push to `main` triggers auto-deploy.
- `./start.sh` must run in the foreground (it does).
- Check logs for the `DATA_FOLDER=...` line we added.
- Health checks: `/healthz` and `/healthz?deep=1`

The start command (what `./start.sh` runs):
```bash
pipenv run gunicorn --bind 0.0.0.0:$PORT --workers 2 --threads 8 --worker-class gthread PlotterApp:app
```

After the service is live, validate with the NPC harness:
```bash
RUN_SCALE=1 TARGET_BASE_URL=https://<your-app>.onrender.com \
  pipenv run pytest tests/e2e/test_scale_voting.py -q -s --browser chromium
```

### Kill everything
```bash
./kill_all.sh
```

## Live Operator Surface (Primary)

After logging in, go to `/account` → scroll to **Operator & Dev Tools** panel for:
- Inspect windows, ballots, tallies
- Seed test data
- Clear, promote winners, reset users
- Target window override

See `notes/GROK/SOUL_DRIVER.md` and `notes/GROK/DEV_NOTES.md` for north star, architecture, and backlog.

Secondary tools: `python -m dev_tools.cli --help` and the prefab dashboard.

The legacy 2020 election monitors (PresidentMonitor, state data, /monitor routes) have been fully removed as part of production repo cleanup.