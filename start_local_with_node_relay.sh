#!/bin/zsh
# Local dev runner that keeps the public port on a Node process
# (firewall-friendly) while gunicorn runs on localhost only.
#
# Only runs the PlotterApp (no PresidentMonitor / data generation).

cd "$(dirname "$0")"

# Kill old stuff safely
kill $(lsof -ti :5000,5001 2>/dev/null) 2>/dev/null || true
sleep 0.5

echo "=== Starting gunicorn on localhost:5001 (internal only) ==="
export DATA_FOLDER=${DATA_FOLDER:-/Users/pranav/data/}
pipenv run gunicorn \
  --bind 127.0.0.1:5001 \
  --workers 1 \
  --threads 4 \
  --access-logfile - \
  --error-logfile - \
  PlotterApp:app > /tmp/gunicorn.log 2>&1 &
GUNICORN_PID=$!
echo "Gunicorn PID: $GUNICORN_PID (logs: /tmp/gunicorn.log)"

echo ""
echo "Waiting for gunicorn to listen on 5001..."
for i in {1..15}; do
  if lsof -ti :5001 -sTCP:LISTEN >/dev/null 2>&1; then
    echo "Gunicorn ready on 5001"
    break
  fi
  sleep 0.5
  if [ "$i" -eq 15 ]; then
    echo "!!! Gunicorn failed to start on 5001 after 7.5s"
    echo "Last lines of log:"
    tail -30 /tmp/gunicorn.log
    echo ""
    echo "Common cause: missing or wrong path to Firebase cert in DATA_FOLDER"
    echo "Your DATA_FOLDER is: $DATA_FOLDER"
    echo "Check: ls \$DATA_FOLDER/theinternetparty-5b902-firebase-adminsdk-*.json"
    kill $GUNICORN_PID 2>/dev/null || true
    exit 1
  fi
done

echo ""
echo "=== Starting Node relay on 0.0.0.0:5000 -> 127.0.0.1:5001 ==="
echo "The firewall will see Node (which you already trust via npx)."
node node_relay.js &
RELAY_PID=$!
echo "Relay PID: $RELAY_PID"

echo ""
echo "App should be available at:"
echo "  http://127.0.0.1:5000  (localhost)"
echo "  http://$(ipconfig getifaddr en0 2>/dev/null || echo 'YOUR_LAN_IP'):5000  (LAN)"
echo ""
echo "Press Ctrl-C to stop everything."

# Wait for relay (foreground)
wait $RELAY_PID

# Cleanup on exit
kill $GUNICORN_PID 2>/dev/null || true
