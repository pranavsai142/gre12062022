#!/bin/zsh
# kill_all.sh
# Kills all processes related to the PlotterApp local dev setup:
# - gunicorn (PlotterApp)
# - node relay
# - Anything listening on 5000/5001

echo "=== Killing all PlotterApp / dev processes ==="

# 1. Kill anything listening on the dev ports
for port in 5000 5001; do
  PIDS=$(lsof -ti :$port 2>/dev/null)
  if [[ -n "$PIDS" ]]; then
    echo "Killing processes on port $port: $PIDS"
    kill -9 $PIDS 2>/dev/null || true
  fi
done

# 2. Kill by name patterns (more aggressive)
echo "Killing by process name patterns..."
pkill -9 -f "gunicorn.*PlotterApp" 2>/dev/null || true
pkill -9 -f "node node_relay.js" 2>/dev/null || true
pkill -9 -f "PlotterApp.py" 2>/dev/null || true

# 3. Use existing kill helper if present
if [[ -x "./kill_process.sh" ]]; then
  echo "Using kill_process.sh helper..."
  ./kill_process.sh gunicorn 2>/dev/null || true
fi

sleep 1

# Verify
REMAINING=$(lsof -ti :5000,5001 2>/dev/null)
if [[ -n "$REMAINING" ]]; then
  echo "WARNING: Still some processes on ports:"
  lsof -i :5000,5001
else
  echo "✅ Ports 5000 and 5001 are clear."
fi

echo ""
echo "Done."
