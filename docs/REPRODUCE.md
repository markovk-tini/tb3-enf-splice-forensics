# Reproducing every check and run

Everything was run locally on Windows 11 + WSL2 (Ubuntu 22.04, 20 CPUs,
16 GB RAM for WSL) with Docker Engine 29 inside WSL. Any Linux host with
Docker works the same way. Paths below are relative to this repository; the
scripts expect a checkout of `harbor-framework/terminal-bench-3` next to it at
`../tb3-ref/terminal-bench-3` (or set `TB3_DIR`).

## 1. Setup

```bash
# Terminal-Bench 3 at the commit these results were produced against
git clone https://github.com/harbor-framework/terminal-bench-3 ../tb3-ref/terminal-bench-3
git -C ../tb3-ref/terminal-bench-3 checkout 58a97b0831627394a04c32d0d7097786ef2ca067

# Harbor: the exact version TB3 CI pins in .github/harbor-version
curl -LsSf https://astral.sh/uv/install.sh | sh
uv tool install harbor==0.23.1.dev202609170426

# Subscription credentials (the assignment's sample commands use the same mechanism)
claude setup-token                       # Claude Code OAuth token
mkdir -p ~/.tb3-secrets && chmod 700 ~/.tb3-secrets
printf 'CLAUDE_CODE_OAUTH_TOKEN=%s\n' '<token>' > ~/.tb3-secrets/env && chmod 600 ~/.tb3-secrets/env
codex login                              # writes ~/.codex/auth.json
```

The scripts export `CLAUDE_FORCE_OAUTH=1` + `CLAUDE_CODE_OAUTH_TOKEN` and
`CODEX_FORCE_AUTH_JSON=1` into the harbor process environment, which is what
the assignment's `--ae` flags do. Passing them through the environment rather
than the job config keeps them out of the saved job files.

## 2. Static checks (CI: "Static checks")

```bash
tools/run_static_checks.sh tasks/enf-splice-forensics
```

Runs all 28 `scripts/checks/check-*.sh` from the TB3 checkout in workflow
order, with the same `dockerfile-pin` v1.5.0 binary (sha256-verified) and
PyYAML 6.0.2 the workflow installs. Output: `results/static-checks.md`.

## 3. Implementation rubric review (CI: "Review")

```bash
tools/review.sh tasks/enf-splice-forensics
```

`tools/stage_review.py` builds the review task exactly like
`scripts/review/stage_task.py` (same reviewer instruction template, the rubric
`docs/prompts/task-implementation.toml` appended, same word-count helper, same
verifier), copying the local task instead of fetching a PR commit. It runs with
`review_agent`/`review_model` from `.github/harbor-run-defaults.yml`
(`claude-code` + `anthropic/claude-sonnet-5`). Output:
`results/rubric-review.md` and the raw `results/rubric-review-verdicts.json`.

## 4. Docker build, oracle and nop (CI: "Validation")

```bash
tools/run_validation.sh tasks/enf-splice-forensics
```

One Harbor job with agents `oracle` and `nop`, one attempt each, as the hosted
`/validate` job does. Oracle must score 1.0 and nop 0.0.

## 5. Agent trials (`/run`) and adversarial trials (`/cheat`)

```bash
tools/trials.sh run   claude    # claude-code, anthropic/claude-opus-5-5, reasoning_effort=max, 3 trials
tools/trials.sh run   codex     # codex, openai/gpt-6.1-sol, reasoning_effort=xhigh, 3 trials
tools/trials.sh cheat claude    # 1 trial, TB3 hack prompt appended to the instruction
tools/trials.sh cheat codex
```

These mirror `scripts/ci/hosted_job_config.py`: `/run` uses `trials: 3` from
`.github/harbor-run-defaults.yml`; `/cheat` forces one attempt and appends
`docs/prompts/hack-trial-prompt.md` through Harbor's `extra_instructions`.
Each agent keeps the kwargs/env the CI config attaches to its name
(`reasoning_effort`, and `CLAUDE_CODE_MAX_OUTPUT_TOKENS=128000` for
claude-code). The agent timeout comes from `task.toml` (4 h).

## 6. Trial analysis (CI: hosted `harbor analyze`)

```bash
tools/analyze.sh jobs/<job-name>
```

Stages one review task per trial exactly like
`scripts/ci/stage_hosted_analysis.py` (same instruction, the six criteria from
`docs/prompts/trial-analysis.toml`, same `analysis.json` schema check) and runs
it with `analyze_agent`/`analyze_model` (`claude-code` +
`anthropic/claude-sonnet-5`).

## 7. Summaries

```bash
python3 tools/summarize.py jobs/<job> [jobs/<job> ...]
```

## Regenerating the evidence

```bash
pip install numpy==2.3.4 scipy==1.16.3 av==19.0.2
cd tasks/enf-splice-forensics/tests && python synthesize_evidence.py ../environment/data 11
python case_plan.py   # prints the answer key
```

The second argument is the number of worker processes (one exhibit each); the
output is byte-identical for any worker count. Rendering takes about 1.5 min
with 11 workers.

Earlier versions of the task are tagged `iteration-1-audio` and
`iteration-2-video`.

## Reference-solution robustness

```bash
pip install numpy==2.3.4 scipy==1.16.3 av==19.0.2
python tools/robustness/audit.py <data-dir>        # identifiability of every stretch and edit
python tools/robustness/perturb.py <data-dir>      # each threshold moved down and up, rescored
SWEEP_OUT=sweep python tools/robustness/seed_sweep.py 1 2 3 4 5 6   # other random draws, re-solved
```

`<data-dir>` holds `evidence/` and `grid/` (for the committed data,
`tasks/enf-splice-forensics/environment/data`). Decoded channels are cached in
`$ENF_CACHE` (default: the system temp directory). Results are in
`results/identifiability-audit.md` and `results/oracle-robustness.md`.
