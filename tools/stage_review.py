"""Stage the Terminal-Bench 3 implementation-rubric review as a Harbor task.

Mirrors terminal-bench-3/scripts/review/stage_task.py (what the hosted /review
job runs) with one difference: the task under review is copied from a local
directory instead of being fetched from a PR commit with git. The reviewer
instruction, the rubric, the word-count helper, the task.toml and the verifier
are produced exactly as the CI script produces them.

Usage: python stage_review.py <tb3-checkout> <task-dir> <output-dir>
"""

import shutil
import sys
from pathlib import Path


def stage(tb3: Path, task: Path, out: Path) -> None:
    templates = tb3 / "scripts/rubric-regression/templates"
    environment, tests = out / "environment", out / "tests"
    environment.mkdir(parents=True)
    tests.mkdir()

    (environment / "instruction_word_counts.py").write_text(
        (tb3 / "scripts/review/instruction_word_counts.py").read_text()
    )
    shutil.copytree(task, environment / "task-under-review" / task.name)
    (environment / "Dockerfile").write_text(
        "FROM ubuntu:24.04\n"
        "RUN apt-get update && apt-get install -y --no-install-recommends "
        "ca-certificates curl git nodejs npm procps python3 "
        "&& rm -rf /var/lib/apt/lists/*\n"
        "RUN npm install -g @anthropic-ai/claude-code\n"
        "COPY task-under-review/ /app/task-under-review/\n"
        "COPY instruction_word_counts.py /app/instruction_word_counts.py\n"
        "WORKDIR /app\n"
    )
    rubric = (tb3 / "docs/prompts/task-implementation.toml").read_text()
    instruction = (templates / "instruction.md").read_text().replace(
        "the quality rubric is at `/app/rubric.toml`.",
        "apply the rubric included below.",
    )
    (out / "instruction.md").write_text(
        instruction + "\n\nRubric:\n\n```toml\n" + rubric + "```\n"
    )
    (out / "task.toml").write_text(
        'schema_version = "1.0"\n'
        'artifacts = ["/app/verdicts.json"]\n\n'
        "[agent]\n"
        "timeout_sec = 1800.0\n"
    )
    (tests / "test.sh").write_text(
        "#!/bin/bash\n"
        "if [ -f /app/verdicts.json ] && [ -s /app/verdicts.json ]; then\n"
        "  echo 1 > /logs/verifier/reward.txt\n"
        "else\n"
        "  echo 0 > /logs/verifier/reward.txt\n"
        "fi\n"
    )


if __name__ == "__main__":
    stage(Path(sys.argv[1]), Path(sys.argv[2]).resolve(), Path(sys.argv[3]))
