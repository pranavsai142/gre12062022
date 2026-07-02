#!/bin/zsh
# Helper to clean and add specific rules for the project's Python 3.14
# Run this while your Flask server is listening on port 5000.
#
# Usage:
#   chmod +x fix_firewall.sh
#   ./fix_firewall.sh
#
# It will ask for sudo password.
#
# After running, test with:
#   curl -v http://192.168.1.71:5000/
# from this machine and from another device on the LAN.

set -e

echo "=== Current firewall state ==="
/usr/libexec/ApplicationFirewall/socketfilterfw --getglobalstate || true

echo ""
echo "=== Current list (may need sudo for full view) ==="
/usr/libexec/ApplicationFirewall/socketfilterfw --list || true

# Exact paths for Homebrew Python 3.14.6 (update if brew upgrades)
LAUNCHER="/usr/local/Cellar/python@3.14/3.14.6/Frameworks/Python.framework/Versions/3.14/Resources/Python.app/Contents/MacOS/Python"
REAL_BIN="/usr/local/Cellar/python@3.14/3.14.6/Frameworks/Python.framework/Versions/3.14/bin/python3.14"
REAL_PYTHON="/usr/local/Cellar/python@3.14/3.14.6/Frameworks/Python.framework/Versions/3.14/Python"
VENV_PY="/Volumes/ssd/projects/gre12062022/.venv/bin/python"
OPT_PY="/usr/local/opt/python@3.14/bin/python3.14"

echo ""
echo "=== Adding/unblocking the specific binaries that actually run your server ==="

for path in "$LAUNCHER" "$REAL_BIN" "$REAL_PYTHON" "$VENV_PY" "$OPT_PY"; do
  if [ -e "$path" ]; then
    echo "Processing: $path"
    sudo /usr/libexec/ApplicationFirewall/socketfilterfw --add "$path" || true
    sudo /usr/libexec/ApplicationFirewall/socketfilterfw --unblockapp "$path" || true
  else
    echo "Skipping (not found): $path"
  fi
done

echo ""
echo "=== Refreshing ALF (off then on) ==="
sudo /usr/libexec/ApplicationFirewall/socketfilterfw --setglobalstate off || true
sleep 1
sudo /usr/libexec/ApplicationFirewall/socketfilterfw --setglobalstate on || true

echo ""
echo "=== Updated list ==="
sudo /usr/libexec/ApplicationFirewall/socketfilterfw --list | grep -E 'python|Python|5000' || sudo /usr/libexec/ApplicationFirewall/socketfilterfw --list || true

echo ""
echo "Done. Now restart your server (use: pipenv run python run_lan.py)"
echo "Then test from this machine: curl -v http://192.168.1.71:5000/"
echo "And from another device on the same WiFi."
echo ""
echo "If still only localhost works, we will switch to the socat proxy workaround."
