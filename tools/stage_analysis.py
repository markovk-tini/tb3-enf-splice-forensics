"""Stage per-trial trajectory reviews, mirroring the hosted analysis that
Terminal-Bench 3 runs after /run and /cheat (scripts/ci/stage_hosted_analysis.py).

Same reviewer instruction (docs/prompts/trial-analysis.txt + every criterion
from docs/prompts/trial-analysis.toml), same /app/trial and /app/task layout,
same analysis.json schema check. The only difference: the trial and task are
copied from local directories instead of being downloaded from Harbor Hub.

Usage: python stage_analysis.py <tb3-checkout> <task-dir> <job-dir> <output-dir>
"""

import json
import shutil
import sys
import tomllib
from pathlib import Path

VERIFIER = r"""#!/bin/sh
mkdir -p /logs/verifier
if test -f /app/analysis.json && jq -e -s --slurpfile criteria /tests/criteria.json -f /tests/validate.jq /app/analysis.json >/dev/null 2>&1; then
    echo 1
else
    echo 0
fi > /logs/verifier/reward.txt
"""

VALIDATE_JQ = r"""
length == 1 and (.[0] | type == "object" and
(.summary | type == "string" and test("\\S")) and
(.checks | type == "object" and (keys == ($criteria[0] | sort)) and
  all(.[]; type == "object" and
    (.outcome == "pass" or .outcome == "fail" or .outcome == "not_applicable") and
    (.explanation | type == "string" and test("\\S")))))
"""

DOCKERFILE = """FROM python:3.12-slim
RUN apt-get update && apt-get install -y --no-install-recommends ca-certificates jq && rm -rf /var/lib/apt/lists/*
COPY trial/ /app/trial/
COPY task/ /app/task/
WORKDIR /app
"""


def stage(tb3: Path, task: Path, job: Path, out: Path) -> int:
    criteria = tomllib.loads((tb3 / "docs/prompts/trial-analysis.toml").read_text())["criteria"]
    names = [c["name"] for c in criteria]
    guidance = "\n\n".join(f"{c['name']}: {c['description']}\n{c['guidance']}" for c in criteria)
    instruction = (tb3 / "docs/prompts/trial-analysis.txt").read_text() + "\n\n" + guidance
    count = 0
    for result in sorted(job.glob("*/result.json")):
        trial = result.parent
        staged = out / f"{task.name}__{trial.name.split('__')[-1]}"
        env, tests = staged / "environment", staged / "tests"
        tests.mkdir(parents=True)
        env.mkdir()
        shutil.copytree(trial, env / "trial")
        # the task as the agent and verifier saw it (data files are not needed to judge)
        shutil.copytree(task, env / "task", ignore=shutil.ignore_patterns("data"))
        (env / "Dockerfile").write_text(DOCKERFILE)
        (tests / "criteria.json").write_text(json.dumps(names))
        (tests / "validate.jq").write_text(VALIDATE_JQ)
        (tests / "test.sh").write_text(VERIFIER)
        (staged / "instruction.md").write_text(instruction)
        (staged / "task.toml").write_text(
            'schema_version = "1.3"\n'
            'artifacts = [{ source = "/app/analysis.json", destination = "analysis.json" }]\n\n'
            "[agent]\ntimeout_sec = 600.0\n\n[verifier]\ntimeout_sec = 30.0\n"
        )
        count += 1
    return count


if __name__ == "__main__":
    n = stage(*(Path(a).resolve() for a in sys.argv[1:5]))
    print(f"staged {n} trial reviews")
