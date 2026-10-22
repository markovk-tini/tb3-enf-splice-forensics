#!/bin/bash
# Run the Terminal-Bench 3 static checks against a task, exactly as the
# "CI / Static checks" workflow (.github/workflows/static-checks.yml) does:
# same scripts (from a pinned TB3 checkout), same dockerfile-pin release,
# same PyYAML, same pass/fail/warn semantics.
#
# Usage: tools/run_static_checks.sh [task-dir] [tb3-checkout]
#   task-dir      default: tasks/enf-splice-forensics (relative to repo root)
#   tb3-checkout  default: $TB3_DIR or ../tb3-ref/terminal-bench-3
set -uo pipefail

REPO_ROOT=$(cd "$(dirname "$0")/.." && pwd)
TASK_DIR=${1:-tasks/enf-splice-forensics}
TB3_DIR=${2:-${TB3_DIR:-$REPO_ROOT/../tb3-ref/terminal-bench-3}}
CHECKS_DIR="$TB3_DIR/scripts/checks"
OUT=${OUT:-$REPO_ROOT/results/static-checks.md}

# --- tooling (mirrors the workflow's install steps) ---------------------------
export PATH="$HOME/.local/bin:$PATH"
if ! command -v dockerfile-pin >/dev/null 2>&1; then
    tmp=$(mktemp -d)
    curl --fail --silent --show-error --location \
        https://github.com/azu/dockerfile-pin/releases/download/v1.5.0/dockerfile-pin_linux_amd64.tar.gz \
        --output "$tmp/dockerfile-pin.tar.gz"
    echo "88845bfbe4918596f00eb77ebeec8a0826026c9b24bcc83053cae48402e95ea6  $tmp/dockerfile-pin.tar.gz" | sha256sum --check --quiet
    tar --extract --gzip --file "$tmp/dockerfile-pin.tar.gz" --directory "$tmp" dockerfile-pin
    install -m 0755 "$tmp/dockerfile-pin" "$HOME/.local/bin/dockerfile-pin"
fi
VENV="$HOME/tb3-ci-venv"
if [ ! -x "$VENV/bin/python3" ]; then
    uv venv --quiet --python 3.12 "$VENV"
    uv pip install --quiet --python "$VENV/bin/python3" PyYAML==6.0.2
fi
export PATH="$VENV/bin:$PATH"   # checks call python3 and need tomllib + PyYAML

# --- the check list, in workflow order ---------------------------------------
CHECKS=(
    "Canary strings|check-canary.sh"
    "No cheat directory|check-no-cheat-dir.sh"
    "Dockerfile refs|check-dockerfile-references.sh"
    "Image digest pins|check-image-digests.sh"
    "Dockerfile sanity|check-dockerfile-sanity.sh"
    "Dockerfile platform|check-dockerfile-platform.sh"
    "Absolute paths|check-task-absolute-path.sh"
    "Test refs|check-test-file-references.sh"
    "test.sh sanity|check-test-sh-sanity.sh"
    "Task fields|check-task-fields.sh"
    "Task fix changelog|check-task-changelog.sh"
    "Task timeout cap|check-task-timeout.sh"
    "Instruction suffix|check-instruction-suffix.sh"
    "Instruction headings|check-instruction-headings.sh"
    "GPU types|check-gpu-types.sh"
    "Resource sizes|check-resource-sizes.sh"
    "Allow internet|check-allow-internet.sh"
    "No internet opt-in|check-no-allow-internet-true.sh"
    "Task slug length|check-task-slug.sh"
    "Task package name|check-task-package-name.sh"
    "Separate verifier|check-separate-verifier.sh"
    "Verifier tooling baked|check-verifier-tooling-baked.sh"
    "Trial network fetch|check-trial-network-fetch.sh"
    "Pip pinning|check-pip-pinning.sh"
    "Pytest version pin|check-pytest-version.sh"
    "Nproc usage|check-nproc.sh"
    "CPU parallelism advisory (nonblocking)|check-cpu-threads.sh"
    "Compose volumes|check-compose-volumes.sh"
)

cd "$REPO_ROOT"
# A new task: it is in FIX_DIRS but absent from the base checkout, like in CI.
export FIX_DIRS="$TASK_DIR" BASE_DIR="$TB3_DIR"

passed=0; failed=0; warned=0
rows=""
for entry in "${CHECKS[@]}"; do
    name="${entry%%|*}"; script="${entry##*|}"
    out=$(bash "$CHECKS_DIR/$script" "$TASK_DIR" 2>&1); rc=$?
    clean=$(printf '%s\n' "$out" | sed -E $'s/\x1b\\[[0-9;]*[A-Za-z]//g')
    fails=$(printf '%s\n' "$clean" | grep '^FAIL ' || true)
    warns=$(printf '%s\n' "$clean" | grep '^WARN ' || true)
    if [ $rc -ne 0 ]; then
        failed=$((failed + 1)); status="FAIL"
        detail=$(printf '%s' "${fails:-$clean}" | tr '\n' ' ' | cut -c1-300)
    elif [ -n "$warns" ]; then
        warned=$((warned + 1)); status="WARN"
        detail=$(printf '%s' "$warns" | tr '\n' ' ' | cut -c1-300)
    else
        passed=$((passed + 1)); status="PASS"; detail=""
    fi
    printf '%-4s  %s %s\n' "$status" "$name" "$detail"
    rows+="| $name | $status | ${detail//|/\\|} |"$'\n'
done

mkdir -p "$(dirname "$OUT")"
{
    echo "# Static checks"
    echo
    echo "- Task: \`$TASK_DIR\`"
    echo "- Checks: \`scripts/checks/*\` from terminal-bench-3 @ \`$(git -C "$TB3_DIR" rev-parse --short HEAD)\`"
    echo "- Run: $(date -u +%Y-%m-%dT%H:%M:%SZ)"
    echo "- Result: **$passed passed, $failed failed, $warned with warnings** (of ${#CHECKS[@]})"
    echo
    echo "| Check | Result | Details |"
    echo "|---|---|---|"
    printf '%s' "$rows"
} > "$OUT"
echo
echo "$passed passed, $failed failed, $warned with warnings -> $OUT"
[ $failed -eq 0 ]
