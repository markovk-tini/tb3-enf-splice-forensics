"""Render a rubric-review verdicts.json as a Markdown table (like the CI sticky comment)."""

import json
import sys
import tomllib


def main(verdicts_path: str, rubric_path: str) -> None:
    with open(verdicts_path) as fh:
        checks = json.JSONDecoder().raw_decode(fh.read().lstrip())[0]["checks"]
    with open(rubric_path, "rb") as fh:
        criteria = tomllib.load(fh)["criteria"]
    order = [c["name"] for c in criteria]
    severity = {c["name"]: c.get("severity", "error") for c in criteria}
    icon = {"pass": "✅", "fail": "❌", "warn": "⚠️", "not_applicable": "⚪"}
    counts = {}
    rows = []
    for name in order:
        v = checks.get(name, {"outcome": "missing", "explanation": "no verdict"})
        outcome = v.get("outcome", "missing")
        counts[outcome] = counts.get(outcome, 0) + 1
        note = " (nonblocking)" if severity[name] == "warning" else ""
        expl = v.get("explanation", "").replace("|", "\\|").replace("\n", " ")
        rows.append(f"| {icon.get(outcome, '❓')} | `{name}`{note} | {expl} |")
    extra = sorted(set(checks) - set(order))
    blocking_fail = sum(
        1 for n in order if checks.get(n, {}).get("outcome") in (None, "fail") and severity[n] != "warning"
    )
    print("# Implementation rubric review\n")
    print(f"- Criteria: {len(order)} (from `docs/prompts/task-implementation.toml`)")
    print("- Outcomes: " + ", ".join(f"{k}: {v}" for k, v in sorted(counts.items())))
    print(f"- Blocking failures: **{blocking_fail}**")
    if extra:
        print(f"- Verdicts for unknown criteria: {extra}")
    print("\n| | Criterion | Explanation |\n|---|---|---|")
    print("\n".join(rows))


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
