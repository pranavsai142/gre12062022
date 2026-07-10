#!/usr/bin/env bash
# Verify that production is running the post-clock deploy stack.
# Usage: ./scripts/verify_live_deploy.sh [base_url]
set -euo pipefail
BASE="${1:-https://theinternetparty.us}"
fail=0

check() {
  local path="$1"
  local needle="$2"
  local body
  body=$(curl -fsS -m 20 "${BASE}${path}" || true)
  if echo "$body" | grep -q "$needle"; then
    echo "OK  ${path}  (contains ${needle})"
  else
    echo "FAIL ${path}  expected '${needle}' in body"
    echo "     got: $(echo "$body" | head -c 120 | tr '\n' ' ')"
    fail=1
  fi
}

echo "Checking ${BASE} …"
check "/healthz" '"status":"ok"'
check "/voting-clock" '"endsAt"'
check "/status" '"remainingLabel"'
check "/robots.txt" 'User-agent'
# robots must NOT still be the joke body
if curl -fsS -m 15 "${BASE}/robots.txt" | grep -qi 'fuck'; then
  echo "FAIL /robots.txt still has joke body"
  fail=1
else
  echo "OK  /robots.txt  (professional)"
fi
if curl -fsS -m 15 "${BASE}/vote" | grep -q 'data-voting-clock'; then
  echo "OK  /vote  (live clock markup)"
else
  echo "FAIL /vote missing data-voting-clock"
  fail=1
fi

echo "---"
if [[ "$fail" -eq 0 ]]; then
  echo "LIVE DEPLOY LOOKS GOOD"
  curl -fsS -m 15 "${BASE}/status" | head -c 400
  echo
  exit 0
else
  echo "LIVE DEPLOY NOT YET UPDATED — push main and wait for Render rebuild"
  echo "  git push origin main"
  exit 1
fi
