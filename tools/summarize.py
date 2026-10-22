"""Summarise Harbor job directories as Markdown: one row per trial.

Usage: python summarize.py <job-dir> [<job-dir> ...] > results/<name>.md
"""

import json
import sys
from datetime import datetime
from pathlib import Path


def ts(s):
    return datetime.fromisoformat(s.replace("Z", "+00:00")) if s else None


def minutes(span):
    if not span or not span.get("started_at") or not span.get("finished_at"):
        return None
    return (ts(span["finished_at"]) - ts(span["started_at"])).total_seconds() / 60


def ctrf(trial):
    p = trial / "verifier" / "ctrf.json"
    if not p.is_file():
        return None, []
    c = json.loads(p.read_text())["results"]
    failed = [t["name"].split("::")[-1] for t in c["tests"] if t["status"] != "passed"]
    return f"{c['summary']['passed']}/{c['summary']['tests']}", failed


def main(jobs):
    print("| Job | Trial | Agent | Model | Effort | Reward | Tests passed | Agent time (min) | Tokens in / out | Exception |")
    print("|---|---|---|---|---|---|---|---|---|---|")
    for job in map(Path, jobs):
        for res in sorted(job.glob("*/result.json")):
            r = json.loads(res.read_text())
            trial = res.parent
            cfg = r.get("config", {}).get("agent", {})
            effort = (cfg.get("kwargs") or {}).get("reasoning_effort", "")
            reward = (r.get("verifier_result") or {}).get("rewards", {}).get("reward")
            passed, failed = ctrf(trial)
            ar = r.get("agent_result") or {}
            tok = ""
            if ar.get("n_input_tokens") is not None:
                tok = f"{ar['n_input_tokens']:,} / {ar.get('n_output_tokens') or 0:,}"
            exc = (r.get("exception_info") or {}).get("exception_type", "") if r.get("exception_info") else ""
            m = minutes(r.get("agent_execution"))
            print(f"| {job.name} | {trial.name.split('__')[-1]} | {cfg.get('name')} | {cfg.get('model_name') or ''} | "
                  f"{effort} | {reward} | {passed or '-'} | {'' if m is None else f'{m:.0f}'} | {tok} | {exc} |")


if __name__ == "__main__":
    main(sys.argv[1:])
