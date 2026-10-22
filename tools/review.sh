#!/bin/bash
# Implementation-rubric review, mirroring hosted /review
# (scripts/ci/hosted_task_launcher.py: review_agent / review_model from
# .github/harbor-run-defaults.yml, i.e. claude-code + anthropic/claude-sonnet-5,
# no extra kwargs), then render the verdicts as a table.
#
# The CI review task restricts the reviewer's network to api.anthropic.com
# (network_mode allowlist); the local docker backend runs it with open network,
# which does not change what the reviewer reads or how it judges.
#
# Usage: tools/review.sh [task-dir]
set -euo pipefail
# python3 >= 3.11 (tomllib) from the static-check venv, then harbor
export PATH="$HOME/tb3-ci-venv/bin:$HOME/.local/bin:$PATH"

REPO_ROOT=$(cd "$(dirname "$0")/.." && pwd)
TASK=${1:-$REPO_ROOT/tasks/enf-splice-forensics}
TB3_DIR=${TB3_DIR:-$REPO_ROOT/../tb3-ref/terminal-bench-3}
JOBS=${JOBS_DIR:-$REPO_ROOT/jobs}
SECRETS=${TB3_SECRETS:-$HOME/.tb3-secrets/env}
MODEL=${REVIEW_MODEL:-anthropic/claude-sonnet-5}

set -a; . "$SECRETS"; set +a
export CLAUDE_FORCE_OAUTH=1

STAGE=$(mktemp -d)/enf-splice-forensics-review
python3 "$REPO_ROOT/tools/stage_review.py" "$TB3_DIR" "$TASK" "$STAGE"
NAME="review-$(date -u +%Y%m%d-%H%M%S)"
harbor run --path "$STAGE" --agent claude-code --model "$MODEL" \
    --job-name "$NAME" -o "$JOBS" --env docker --yes

VERDICTS=$(find "$JOBS/$NAME" -path '*artifacts*' -name verdicts.json | head -1)
python3 "$REPO_ROOT/tools/render_review.py" "$VERDICTS" "$TB3_DIR/docs/prompts/task-implementation.toml" \
    > "$REPO_ROOT/results/rubric-review.md"
cp "$VERDICTS" "$REPO_ROOT/results/rubric-review-verdicts.json"
echo "job dir: $JOBS/$NAME"
cat "$REPO_ROOT/results/rubric-review.md"
