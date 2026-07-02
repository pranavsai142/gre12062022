#!/bin/zsh
# Improved dynamic whitelist for macOS ALF + gunicorn/python
# Run this while the server is LISTENING on the port.

PORT=5000

echo "=== 1. Finding listener on :$PORT ==="
LISTEN_PIDS=$(lsof -ti :$PORT -sTCP:LISTEN 2>/dev/null || true)

if [[ -z "$LISTEN_PIDS" ]]; then
  echo "ERROR: No process listening on :$PORT yet."
  echo "Start the server (./start_local.sh) and wait for 'Listening at' then run this again."
  exit 1
fi

echo "Listening PIDs: $LISTEN_PIDS"

# Pre-add the things we know are reliable
KNOWN_PATHS=(
  "/Volumes/ssd/projects/gre12062022/.venv/bin/gunicorn"
  "/Volumes/ssd/projects/gre12062022/.venv/bin/python"
  "/usr/local/opt/python@3.14/bin/python3.14"
  "/usr/local/Cellar/python@3.14/3.14.6/Frameworks/Python.framework/Versions/3.14/bin/python3.14"
  "/usr/local/Cellar/python@3.14/3.14.6/Frameworks/Python.framework/Versions/3.14/Resources/Python.app/Contents/MacOS/Python"
)

echo ""
echo "=== 2. Pre-adding known paths (this often helps) ==="
for p in "${KNOWN_PATHS[@]}"; do
  if [[ -e "$p" ]]; then
    RP=$(realpath "$p" 2>/dev/null || echo "$p")
    echo "  Adding: $RP"
    sudo /usr/libexec/ApplicationFirewall/socketfilterfw --add "$RP" 2>/dev/null || true
    sudo /usr/libexec/ApplicationFirewall/socketfilterfw --unblockapp "$RP" 2>/dev/null || true
  fi
done

ADDED=()

for pid in $LISTEN_PIDS; do
  echo ""
  echo "=== 3. Inspecting live PID $pid ==="

  CMDLINE=$(ps -p $pid -o command= 2>/dev/null || echo "")
  echo "  Command: $CMDLINE"

  # Get the actual binary that owns the socket (most important)
  RAW_BIN=$(lsof -p $pid -Fn 2>/dev/null | grep '^n/' | head -1 | cut -c2- || echo "")
  if [[ -n "$RAW_BIN" && -e "$RAW_BIN" ]]; then
    REAL_BIN=$(realpath "$RAW_BIN" 2>/dev/null || echo "$RAW_BIN")
    echo "  Live binary image: $REAL_BIN"
    sudo /usr/libexec/ApplicationFirewall/socketfilterfw --add "$REAL_BIN" 2>/dev/null || true
    sudo /usr/libexec/ApplicationFirewall/socketfilterfw --unblockapp "$REAL_BIN" 2>/dev/null || true
    ADDED+=("$REAL_BIN")
  fi

  # Always force the gunicorn script + its python interpreter
  GUNICORN_BIN="/Volumes/ssd/projects/gre12062022/.venv/bin/gunicorn"
  if [[ -e "$GUNICORN_BIN" ]]; then
    GP=$(realpath "$GUNICORN_BIN" 2>/dev/null || echo "$GUNICORN_BIN")
    echo "  Forcing gunicorn script: $GP"
    sudo /usr/libexec/ApplicationFirewall/socketfilterfw --add "$GP" 2>/dev/null || true
    sudo /usr/libexec/ApplicationFirewall/socketfilterfw --unblockapp "$GP" 2>/dev/null || true
    ADDED+=("$GP")
  fi

  # Force the python that gunicorn is using (from the venv shebang)
  VENV_PYTHON="/Volumes/ssd/projects/gre12062022/.venv/bin/python"
  if [[ -e "$VENV_PYTHON" ]]; then
    VP=$(realpath "$VENV_PYTHON" 2>/dev/null || echo "$VENV_PYTHON")
    echo "  Forcing venv python: $VP"
    sudo /usr/libexec/ApplicationFirewall/socketfilterfw --add "$VP" 2>/dev/null || true
    sudo /usr/libexec/ApplicationFirewall/socketfilterfw --unblockapp "$VP" 2>/dev/null || true
    ADDED+=("$VP")
  fi

  # Also add the framework launcher (what lsof often shows for Homebrew python)
  LAUNCHER="/usr/local/Cellar/python@3.14/3.14.6/Frameworks/Python.framework/Versions/3.14/Resources/Python.app/Contents/MacOS/Python"
  if [[ -e "$LAUNCHER" ]]; then
    LP=$(realpath "$LAUNCHER" 2>/dev/null || echo "$LAUNCHER")
    echo "  Forcing framework launcher: $LP"
    sudo /usr/libexec/ApplicationFirewall/socketfilterfw --add "$LP" 2>/dev/null || true
    sudo /usr/libexec/ApplicationFirewall/socketfilterfw --unblockapp "$LP" 2>/dev/null || true
    ADDED+=("$LP")
  fi
done

echo ""
echo "=== 4. Hard refresh of ALF ==="
sudo /usr/libexec/ApplicationFirewall/socketfilterfw --setglobalstate off 2>/dev/null || true
sleep 0.8
sudo /usr/libexec/ApplicationFirewall/socketfilterfw --setglobalstate on 2>/dev/null || true

echo ""
echo "=== 5. IMPORTANT: Restart the gunicorn process now ==="
echo "Stop the current start_local.sh (Ctrl-C), then immediately re-run ./start_local.sh"
echo ""
echo "Added/forced paths (realpaths where possible):"
printf '  %s\n' "${ADDED[@]}" | sort -u
echo ""
echo "After restart, test from another machine on the LAN:"
echo "  curl -v --max-time 8 http://192.168.1.71:5000/"
echo ""
echo "If it still fails, paste the output of these three commands:"
echo "  lsof -i :5000 -nP"
echo "  sudo /usr/libexec/ApplicationFirewall/socketfilterfw --list"
echo "  ps -eo pid,comm,command | grep -E 'gunicorn|python' | grep -v grep"
echo ""
echo "=== Also check this (very common cause) ==="
echo "System Settings → Privacy & Security → Local Network"
echo "→ Make sure your Terminal (or iTerm) is toggled ON."
echo "If it's off or not listed, turn it on and restart the server."
