#!/bin/bash
set -euo pipefail

# Orchestration for prod verification per TESTING_STRATEGY and plan.
# Usage: DATA_FOLDER=~/data TARGET_BASE_URL=https://theinternetparty.us SCRATCH=... bash scripts/run_prod_verification.sh

DATA_FOLDER=${DATA_FOLDER:-~/data}
TARGET_BASE_URL=${TARGET_BASE_URL:-https://theinternetparty.us}
SCRATCH=${SCRATCH:-/var/folders/h9/sn160jkx6hb87vp9683ptqr00000gn/T/grok-goal-72c7fc886c6c/implementer}
RUN_SCALE=1

mkdir -p "$SCRATCH"
export DATA_FOLDER TARGET_BASE_URL RUN_SCALE

echo "=== RUN_PROD_VERIFICATION start $(date) ===" | tee "$SCRATCH/verification-run.log"

# Verif step 1: baseline E2E (non-scale) -> e2e-baseline.log
echo "Step 1: baseline E2E" | tee -a "$SCRATCH/verification-run.log"
pipenv run pytest tests/e2e/ -q --browser chromium --base-url "${TARGET_BASE_URL}" 2>&1 | tee "$SCRATCH/e2e-baseline.log"

# Verif step 2: scale-100 (pytest + direct) -> scale-100.log (full)
echo "Step 2: S-100" | tee -a "$SCRATCH/verification-run.log"
pipenv run pytest tests/e2e/test_scale_voting.py -q -s --browser chromium --base-url "${TARGET_BASE_URL}" 2>&1 | tee "$SCRATCH/scale-100.log"
pipenv run python -c '
import json, os
from npc.scenarios import run_full_cycle
m = run_full_cycle(base_url=os.environ["TARGET_BASE_URL"], n_drafters=3, n_voters=100, concurrency=25, yes_fraction=0.6, no_fraction=0.25, promote=True, cleanup=True)
print(json.dumps(m, indent=2, default=str))
' 2>&1 | tee -a "$SCRATCH/scale-100.log"

# Verif step 3: S-200 + mixed (use new wrapper for readers) -> scale-200-mixed.log full
echo "Step 3: S-200 mixed + readers" | tee -a "$SCRATCH/verification-run.log"
pipenv run python -c '
import json, os
from npc.scenarios import run_phase2_mixed
m = run_phase2_mixed(base_url=os.environ["TARGET_BASE_URL"], n_voters=200, n_readers=20, reader_rounds=2, promote=True, cleanup=True)
print(json.dumps(m, indent=2, default=str))
' 2>&1 | pipenv run python -m json.tool | tee "$SCRATCH/scale-200-mixed.log"

# S-Gov-Full-50 for AC2 completeness
echo "S-Gov-Full-50" | tee -a "$SCRATCH/verification-run.log"
pipenv run python -c '
import json, os
from npc.scenarios import run_s_gov_full
m = run_s_gov_full(base_url=os.environ["TARGET_BASE_URL"], n_voters=50, promote=True, cleanup=True)
print(json.dumps(m, indent=2, default=str))
' 2>&1 | pipenv run python -m json.tool | tee "$SCRATCH/s-gov-full-50.log"

# Health (step 4 pre)
curl -s "$TARGET_BASE_URL/healthz" | tee "$SCRATCH/verif-4-health.log"
curl -s "$TARGET_BASE_URL/healthz?deep=1" >> "$SCRATCH/verif-4-health.log"
curl -s "$TARGET_BASE_URL/ballot-items" >> "$SCRATCH/verif-4-health.log"

echo "=== RUN_PROD_VERIFICATION done $(date) ===" | tee -a "$SCRATCH/verification-run.log"
ls -l "$SCRATCH"/*.log | tee -a "$SCRATCH/verification-run.log"
