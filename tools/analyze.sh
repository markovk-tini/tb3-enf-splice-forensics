#!/bin/bash
# Trajectory review of every trial in a job, mirroring the hosted analysis that
# TB3 runs after /run and /cheat (analyze_agent / analyze_model from
# .github/harbor-run-defaults.yml: claude-code + anthropic/claude-sonnet-5).
#
# Usage: tools/analyze.sh <job-dir>
set -euo pipefail
export PATH="$HOME/tb3-ci-venv/bin:$HOME/.local/bin:$PATH"

JOB=$(cd "${1:?job dir}" && pwd)
REPO_ROOT=$(cd "$(dirname "$0")/.." && pwd)
TB3_DIR=${TB3_DIR:-$REPO_ROOT/../tb3-ref/terminal-bench-3}
TASK="$REPO_ROOT/tasks/enf-splice-forensics"
JOBS=${JOBS_DIR:-$REPO_ROOT/jobs}
SECRETS=${TB3_SECRETS:-$HOME/.tb3-secrets/env}
MODEL=${ANALYZE_MODEL:-anthropic/claude-sonnet-5}

set -a; . "$SECRETS"; set +a
export CLAUDE_FORCE_OAUTH=1

STAGE=$(mktemp -d)
python3 "$REPO_ROOT/tools/stage_analysis.py" "$TB3_DIR" "$TASK" "$JOB" "$STAGE"
NAME="analysis-$(basename "$JOB")"
harbor run --path "$STAGE" --agent claude-code --model "$MODEL" \
    --job-name "$NAME" -o "$JOBS" --env docker --yes -n 4
echo "analysis job: $JOBS/$NAME"
