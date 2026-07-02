#!/bin/zsh
# Local development runner that stays as close as possible to what runs on Render
# (i.e. the logic in start.sh), but:
# - Uses pipenv run for reliable venv python
# - Runs the app in foreground (so you see output)
# - Disables reloader (FLASK_USE_RELOADER=0) for more reliable mac firewall rules
# - Still starts the monitor in background like prod
#
# This lets you test LAN access exactly like the prod start.sh flow.
#
# Usage:
#   ./start_local.sh
#
# After it prints that the app is starting, in another terminal run:
#   ./whitelist_current.sh
#
# Then test from other devices on the LAN: http://192.168.1.71:5000

cd "$(dirname "$0")"

# For local Mac dev, default to your data folder (where cert and state data live)
# On Render, it will use /data when running start.sh
# Override with: DATA_FOLDER=/your/path ./start_local.sh
export DATA_FOLDER=${DATA_FOLDER:-/Users/pranav/data/}

echo "=== Killing old monitor (like start.sh) ==="
./kill_process.sh PresidentMonitor.py

echo "=== Starting monitor in background (like prod) ==="
pipenv run python PresidentMonitor.py -s al,ak,az,ar,ca,co,ct,de,fl,ga,hi,id,il,in,ia,ks,ky,la,me,md,ma,mi,mn,ms,mo,mt,ne,nv,nh,nj,nm,ny,nc,nd,oh,ok,or,pa,ri,sc,sd,tn,tx,ut,vt,va,wa,wv,wi,wy > monitor.log &
MONITOR_PID=$!
echo "Monitor PID: $MONITOR_PID (logs: monitor.log)"

echo ""
echo "=== Starting PlotterApp with gunicorn (foreground, prod-grade, visible) ==="
echo "Matches the gunicorn command now in start.sh (used on Render)"
echo ""
echo ">>> IMPORTANT SEQUENCE FOR FIREWALL <<<"
echo "1. Wait until you see: 'Listening at: http://0.0.0.0:5000'"
echo "2. In a SECOND terminal, immediately run: ./whitelist_current.sh"
echo "3. When it says 'Restart the gunicorn process now', Ctrl-C this and re-run ./start_local.sh"
echo ""
echo ">>> ALSO: System Settings > Privacy & Security > Local Network"
echo ">>> Make sure your Terminal is toggled ON <<<"
echo ""

PORT=5000 pipenv run gunicorn \
  --bind 0.0.0.0:5000 \
  --workers 1 \
  --threads 4 \
  --access-logfile - \
  --error-logfile - \
  PlotterApp:app

echo ""
echo "(server exited)"

