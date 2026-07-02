#!/bin/zsh
# Gunicorn + socat LAN helper for The Internet Party
# - Uses gunicorn (better than raw dev server)
# - Binds gunicorn to localhost only
# - socat takes the public port 5000 (easy for ALF to allow)
#
# Run: ./start_gunicorn_socat.sh
# Stop with Ctrl-C

set -e

cd "$(dirname "$0")"

echo "=== 1. Killing anything on port 5000 ==="
lsof -ti :5000 | xargs kill -9 2>/dev/null || true
sleep 0.5

echo "=== 2. Adding firewall rules for gunicorn + python (will ask sudo) ==="
GUNICORN_BIN="/Volumes/ssd/projects/gre12062022/.venv/bin/gunicorn"
LAUNCHER="/usr/local/Cellar/python@3.14/3.14.6/Frameworks/Python.framework/Versions/3.14/Resources/Python.app/Contents/MacOS/Python"
REAL_BIN="/usr/local/Cellar/python@3.14/3.14.6/Frameworks/Python.framework/Versions/3.14/bin/python3.14"
VENV_PY="/Volumes/ssd/projects/gre12062022/.venv/bin/python"

for p in "$GUNICORN_BIN" "$LAUNCHER" "$REAL_BIN" "$VENV_PY"; do
  if [ -e "$p" ]; then
    echo "  -> Adding $p"
    sudo /usr/libexec/ApplicationFirewall/socketfilterfw --add "$p" 2>/dev/null || true
    sudo /usr/libexec/ApplicationFirewall/socketfilterfw --unblockapp "$p" 2>/dev/null || true
  fi
done

echo "  -> Refreshing ALF"
sudo /usr/libexec/ApplicationFirewall/socketfilterfw --setglobalstate off 2>/dev/null || true
sleep 0.5
sudo /usr/libexec/ApplicationFirewall/socketfilterfw --setglobalstate on 2>/dev/null || true

echo ""
echo "=== 3. Starting gunicorn internally on 127.0.0.1:5000 (background) ==="
pipenv run gunicorn \
  --bind 127.0.0.1:5000 \
  --workers 1 \
  --threads 4 \
  --access-logfile - \
  --error-logfile - \
  PlotterApp:app &
GUNICORN_PID=$!
echo "Gunicorn PID: $GUNICORN_PID"
sleep 2

if ! kill -0 $GUNICORN_PID 2>/dev/null; then
  echo "ERROR: gunicorn failed to start. Check output above."
  exit 1
fi

echo ""
echo "=== 4. Starting socat on 0.0.0.0:5000 -> 127.0.0.1:5000 ==="
echo "If you get a macOS prompt for 'socat', ALLOW it."
echo "Access the site from LAN at http://192.168.1.71:5000"
echo ""
socat TCP-LISTEN:5000,reuseaddr,fork TCP:127.0.0.1:5000

echo ""
echo "Stopping gunicorn..."
kill $GUNICORN_PID 2>/dev/null || true
