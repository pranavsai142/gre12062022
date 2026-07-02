# gre12062022 — The Internet Party

Production-grade repo for The Internet Party (parallel direct democracy platform).

## Quick Start

**Local dev (recommended — persistent + LAN accessible with macOS firewall ON):**
```bash
export DATA_FOLDER=/path/to/your/firebase-cert-dir
./start_local_with_node_relay.sh
```
Then visit http://127.0.0.1:5000 or your LAN IP:5000

**Production (Render or similar):**
```bash
./start.sh
# or directly:
pipenv run gunicorn --bind 0.0.0.0:$PORT --workers 2 --threads 4 PlotterApp:app
```

**Kill everything:**
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