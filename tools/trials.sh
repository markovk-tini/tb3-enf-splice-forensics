#!/bin/bash
# Agent trials, mirroring the Terminal-Bench 3 hosted /run and /cheat jobs
# (scripts/ci/hosted_job_config.py in terminal-bench-3):
#   /run   -> n_attempts = 3 per agent
#   /cheat -> n_attempts = 1 per agent, with docs/prompts/hack-trial-prompt.md
#             appended to the task instruction through Harbor's
#             `extra_instructions` (exactly how CI builds the cheat job)
#
# Agents and models are the ones the assignment specifies. kwargs/env are the
# ones .github/harbor-run-defaults.yml attaches to each agent name (CI keeps
# them when a comment overrides the model):
#   claude-code  anthropic/claude-opus-5-5  reasoning_effort=max
#                CLAUDE_CODE_MAX_OUTPUT_TOKENS=128000
#   codex        openai/gpt-6.1-sol         reasoning_effort=xhigh
# CLAUDE_MODEL / CODEX_MODEL override the model (e.g. the current CI defaults
# anthropic/claude-fable-5-1 and openai/gpt-6-astra).
#
# Credentials come from the subscriptions, as in the assignment's sample
# commands, but are passed through the process environment rather than the
# job config so they never land in persisted job files:
#   claude-code: CLAUDE_FORCE_OAUTH=1 + CLAUDE_CODE_OAUTH_TOKEN, read from
#                $TB3_SECRETS (default ~/.tb3-secrets/env, from `claude setup-token`)
#   codex:       CODEX_FORCE_AUTH_JSON=1 -> ~/.codex/auth.json (from `codex login`)
#
# Usage: tools/trials.sh run|cheat claude|codex [n_concurrent] [n_attempts]
set -euo pipefail
export HARBOR_TELEMETRY=0  # no anonymous usage events to the Harbor developers
export PATH="$HOME/.local/bin:$PATH"

KIND=${1:?run or cheat}
WHO=${2:?claude or codex}
REPO_ROOT=$(cd "$(dirname "$0")/.." && pwd)
TASK="$REPO_ROOT/tasks/enf-splice-forensics"
JOBS=${JOBS_DIR:-$REPO_ROOT/jobs}
TB3_DIR=${TB3_DIR:-$REPO_ROOT/../tb3-ref/terminal-bench-3}
SECRETS=${TB3_SECRETS:-$HOME/.tb3-secrets/env}

case "$KIND" in
    run) ATTEMPTS=${4:-3}; NC=${3:-3} ;;
    cheat) ATTEMPTS=1; NC=1 ;;
    *) echo "kind must be run or cheat" >&2; exit 2 ;;
esac

case "$WHO" in
    claude)
        set -a; . "$SECRETS"; set +a
        : "${CLAUDE_CODE_OAUTH_TOKEN:?CLAUDE_CODE_OAUTH_TOKEN missing from $SECRETS}"
        export CLAUDE_FORCE_OAUTH=1
        AGENT=claude-code; MODEL=${CLAUDE_MODEL:-anthropic/claude-opus-5-5}
        KWARGS='{"reasoning_effort": "max"}'
        ENVS='{"CLAUDE_CODE_MAX_OUTPUT_TOKENS": "128000"}'
        ;;
    codex)
        [ -f "$HOME/.codex/auth.json" ] || { echo "run 'codex login' first" >&2; exit 2; }
        export CODEX_FORCE_AUTH_JSON=1
        AGENT=codex; MODEL=${CODEX_MODEL:-openai/gpt-6.1-sol}
        KWARGS='{"reasoning_effort": "xhigh"}'
        ENVS='{}'
        ;;
    *) echo "agent must be claude or codex" >&2; exit 2 ;;
esac

SLUG=$(echo "$MODEL" | sed 's|.*/||; s|[^A-Za-z0-9.-]|-|g')
NAME="$KIND-$AGENT-$SLUG-$(date -u +%Y%m%d-%H%M%S)"
CFG=$(mktemp --suffix=.json)

python3 - "$CFG" <<PY
import json, sys
from pathlib import Path
cfg = {
    "job_name": "$NAME",
    "n_attempts": $ATTEMPTS,
    "n_concurrent_trials": $NC,
    "tasks": [{"path": "$TASK"}],
    "agents": [{
        "name": "$AGENT",
        "model_name": "$MODEL",
        "kwargs": json.loads('''$KWARGS'''),
        "env": json.loads('''$ENVS'''),
    }],
}
if "$KIND" == "cheat":
    cfg["extra_instructions"] = [Path("$TB3_DIR/docs/prompts/hack-trial-prompt.md").read_text()]
Path(sys.argv[1]).write_text(json.dumps(cfg, indent=2) + "\n")
PY

if [ -n "${DRY_RUN:-}" ]; then
    harbor run -c "$CFG" -o "$JOBS" --env docker --print-config
    exit 0
fi

mkdir -p "$JOBS"
echo "job $NAME: $AGENT $MODEL x$ATTEMPTS (concurrency $NC)"
harbor run -c "$CFG" -o "$JOBS" --env docker --yes
echo "job dir: $JOBS/$NAME"
