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

`render.yaml` is the deploy blueprint: connect this repo as a Blueprint in the
Render dashboard, then upload the Firebase admin JSON as a **Secret File** named
`theinternetparty-5b902-firebase-adminsdk-qlzzx-3864b82b40.json` (mounted at
`/etc/secrets/`, which `DATA_FOLDER` points at). Every push to `main` deploys.

The start command is `./start.sh` (foreground gunicorn, logs to the Render stream):
```bash
./start.sh
# equivalent to:
pipenv run gunicorn --bind 0.0.0.0:$PORT --workers 2 --threads 8 --worker-class gthread PlotterApp:app
```

Environment variables (all optional, sensible defaults):
- `SECRET_KEY` — session signing key shared by all workers (render.yaml auto-generates one; without it a stable key is derived from the service-account file)
- `DATA_FOLDER` — directory containing the Firebase admin JSON (default `/data/`)
- `WEB_CONCURRENCY` / `GUNICORN_THREADS` / `GUNICORN_TIMEOUT` — gunicorn tuning (2 / 8 / 60)
- `OPERATOR_EMAILS` — comma-separated allowlist for operator actions (promote, seed, clear, set-window). Unset = any logged-in member (v1 behavior).

Health check: `GET /healthz` (shallow) or `/healthz?deep=1` (verifies RTDB).

After deploying, validate under load with the NPC harness (see `TESTING.md`):
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