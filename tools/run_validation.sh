#!/bin/bash
# Docker build + oracle + nop, mirroring hosted /validate
# (scripts/ci/hosted_task_launcher.py: one job, agents oracle and nop, 1 attempt).
#
# Usage: tools/run_validation.sh [task-dir] [jobs-dir]
set -euo pipefail
export PATH="$HOME/.local/bin:$PATH"

REPO_ROOT=$(cd "$(dirname "$0")/.." && pwd)
TASK=$(cd "$REPO_ROOT/${1:-tasks/enf-splice-forensics}" && pwd)
JOBS=${2:-$REPO_ROOT/jobs}
NAME="validate-$(date -u +%Y%m%d-%H%M%S)"
CFG=$(mktemp --suffix=.json)

cat > "$CFG" <<JSON
{
  "job_name": "$NAME",
  "n_attempts": 1,
  "n_concurrent_trials": 2,
  "tasks": [{"path": "$TASK"}],
  "agents": [{"name": "oracle"}, {"name": "nop"}]
}
JSON

mkdir -p "$JOBS"
harbor run -c "$CFG" -o "$JOBS" --env docker --yes
echo "job: $JOBS/$NAME"
