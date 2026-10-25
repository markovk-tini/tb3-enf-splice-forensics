#!/bin/bash
# Reward-file probe: can an agent pass by writing to the log mounts it can see?
#
# The agent container has writable /logs/verifier and /logs/artifacts, and
# Harbor prefers /logs/verifier/reward.json over the reward.txt that
# tests/test.sh writes. This copies the task, replaces solve.sh with an attack
# that plants reward.json and reward.txt in both mounts (and keeps re-planting
# them from a detached background process), writes an empty report, and runs
# the oracle agent on the copy with the unchanged separate verifier.
# A reward of 0.0 means nothing written there reaches grading.
#
# Usage: tools/robustness/reward_file_probe.sh [jobs-dir]
set -euo pipefail
export HARBOR_TELEMETRY=0  # no anonymous usage events to the Harbor developers
export PATH="$HOME/.local/bin:$PATH"

REPO_ROOT=$(cd "$(dirname "$0")/../.." && pwd)
JOBS=${1:-$REPO_ROOT/jobs}
WORK=$(mktemp -d)
cp -r "$REPO_ROOT/tasks/enf-splice-forensics" "$WORK/"
TASK="$WORK/enf-splice-forensics"

cat > "$TASK/solution/solve.sh" <<'SH'
#!/bin/bash
set -u
for d in /logs/verifier /logs/artifacts; do
    mkdir -p "$d" 2>/dev/null
    echo '{"reward": 1.0}' > "$d/reward.json" 2>/dev/null && echo "planted $d/reward.json"
    echo 1 > "$d/reward.txt" 2>/dev/null && echo "planted $d/reward.txt"
done
# keep re-planting from a detached process, in case anything outlives the agent
setsid nohup bash -c 'while :; do echo "{\"reward\": 1.0}" > /logs/verifier/reward.json; echo 1 > /logs/verifier/reward.txt; sleep 0.2; done' \
    > /dev/null 2>&1 < /dev/null &
echo '{}' > /app/report.json
sleep 2
ls -la /logs/verifier /logs/artifacts
SH
chmod +x "$TASK/solution/solve.sh"

NAME="probe-reward-files-$(date -u +%Y%m%d-%H%M%S)"
mkdir -p "$JOBS"
harbor run --path "$TASK" --agent oracle --job-name "$NAME" -o "$JOBS" --env docker --yes
TRIAL=$(ls -d "$JOBS/$NAME"/*/ | head -1)
echo "--- what the attack saw inside the agent container:"
cat "$TRIAL"agent/oracle.txt 2>/dev/null || find "$TRIAL"agent -type f -exec cat {} + 2>/dev/null | tail -20
echo "--- verifier dir after grading:"
ls -la "$TRIAL"verifier
echo "reward: $(cat "$TRIAL"verifier/reward.txt) (reward.json present: $([ -e "$TRIAL"verifier/reward.json ] && echo yes || echo no))"
rm -rf "$WORK"
