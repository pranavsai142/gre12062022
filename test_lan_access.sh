#!/bin/zsh
# test_lan_access.sh
# Tests PlotterApp reachability on localhost vs your LAN IP.
# Run this after whitelist + server restart to verify.

PORT=5000
VERBOSE=0
LOOP=1

while [[ $# -gt 0 ]]; do
  case $1 in
    -v|--verbose) VERBOSE=1; shift ;;
    --loop) LOOP=$2; shift 2 ;;
    --port) PORT=$2; shift 2 ;;
    -h|--help) echo "Usage: $0 [-v] [--loop N] [--port N]"; exit 0 ;;
    *) echo "Unknown: $1"; exit 1 ;;
  esac
done

LAN_IP=$(ipconfig getifaddr en0 2>/dev/null || ipconfig getifaddr en1 2>/dev/null || echo "192.168.1.71")
LOCAL_URL="http://127.0.0.1:$PORT"
LAN_URL="http://$LAN_IP:$PORT"

echo "=== PlotterApp LAN Test ==="
echo "Local: $LOCAL_URL"
echo "LAN:   $LAN_URL"
echo ""

test_url() {
  local url=$1 label=$2
  echo ">>> $label ($url)"

  if [[ $VERBOSE -eq 1 ]]; then
    curl -v -I --max-time 5 --connect-timeout 3 "$url" 2>&1 | head -20
    local status=$?
  else
    local out
    out=$(curl -s -I --max-time 5 --connect-timeout 3 -w "HTTPSTATUS:%{http_code}" "$url" 2>&1)
    local status=$?
    if [[ $status -eq 0 ]]; then
      if echo "$out" | grep -q "HTTPSTATUS:200"; then
        echo "    ✅ 200 OK"
      elif echo "$out" | grep -q "HTTPSTATUS:"; then
        echo "    ⚠️  Got response but status not 2xx"
        echo "$out" | grep -E 'HTTPSTATUS|HTTP/'
      else
        echo "    ✅ Connected (no status?)"
      fi
    else
      echo "    ❌ curl failed (exit $status)"
    fi
  fi
  echo ""
}

if ! lsof -ti :$PORT -sTCP:LISTEN >/dev/null 2>&1; then
  echo "No listener on :$PORT. Start with ./start_local.sh first."
  exit 1
fi

for i in $(seq 1 $LOOP); do
  [[ $LOOP -gt 1 ]] && echo "=== Run $i/$LOOP ==="
  test_url "$LOCAL_URL" "Localhost"
  test_url "$LAN_URL" "LAN IP"
done

echo "If LAN fails but localhost works → firewall still blocking the connection for this Python binary."
echo "Run ./whitelist_current.sh (while listening), then kill/restart gunicorn."
