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

The service uses **Pipenv** (Pipfile + Pipfile.lock). A `runtime.txt` is included for Python version.

#### Connect in Render
- New → **Blueprint** (recommended) or New → Web Service + connect repo.
- Runtime: Python.
- Name e.g. `internet-party`.

**Build Command** (use this):
```
pip install --upgrade pip && pip install pipenv && pipenv install --deploy --ignore-pipfile
```

**Start Command**:
```
./start.sh
```

(Defined in `render.yaml` — Blueprint will apply them automatically.)

Python version: You can set `PYTHON_VERSION=3.13` directly as an environment variable in the Render dashboard (this is what worked for the current deploy). `runtime.txt` + the value in render.yaml also declare 3.13.

#### Secret File + Firebase
- Upload the admin JSON as a **Secret File** with the *exact* name:
  ```
  theinternetparty-5b902-firebase-adminsdk-qlzzx-3864b82b40.json
  ```
- Mounted by Render at `/etc/secrets/`.
- Set (or confirm) env var: `DATA_FOLDER=/etc/secrets/`

#### Other env vars (from render.yaml or manual)
- `SECRET_KEY` (auto-generated if using blueprint)
- `WEB_CONCURRENCY=2`, `GUNICORN_THREADS=8`
- (Optional) `OPERATOR_EMAILS=you@example.com,...`

#### Deploy & Verify
- Deploy on push to `main` or manual.
- Watch logs. `./start.sh` must run in foreground.
- Health: `GET /healthz` and `/healthz?deep=1`

The start command:
```bash
./start.sh
# runs: pipenv run gunicorn --bind 0.0.0.0:$PORT --workers 2 --threads 8 --worker-class gthread PlotterApp:app
```

After live, run the scale/E2E validation (see TESTING.md):
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