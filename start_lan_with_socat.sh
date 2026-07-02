#!/bin/zsh
# Starts the app internally (127.0.0.1) + socat relay on 0.0.0.0:5000.
# This way the macOS firewall only has to allow "socat" (a simple clean binary)
# instead of fighting all the Python framework binaries.

set -e

cd "$(dirname "$0")"

echo "=== Killing anything currently on port 5000 ==="
lsof -ti :5000 | xargs kill -9 2>/dev/null || true
sleep 0.5

echo "=== Starting Flask internally on 127.0.0.1:5000 (background) ==="
# Using run_internal.py (no reloader, threaded, localhost only)
pipenv run python run_internal.py &
FLASK_PID=$!
echo "Flask PID: $FLASK_PID"
sleep 1.5   # give it time to bind

echo "=== Starting socat on 0.0.0.0:5000 forwarding to 127.0.0.1:5000 ==="
echo "If macOS prompts about socat incoming connections, click Allow."
socat TCP-LISTEN:5000,reuseaddr,fork TCP:127.0.0.1:5000

# When you Ctrl-C socat, also kill the background flask
echo ""
echo "Shutting down internal Flask..."
kill $FLASK_PID 2>/dev/null || true
