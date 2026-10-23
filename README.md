# Terminal-Bench 3 task: `enf-splice-forensics`

An original Terminal-Bench 3 task, built and evaluated against the current
TB3 CI (`harbor-framework/terminal-bench-3` @ `58a97b0`, Harbor
`0.23.1.dev202609170426`).

**The task.** Eleven camera videos were "handed in as unedited original
footage". Some were cut, rearranged, or had footage from another time spliced
in. Using the mains frequency the footage carries and the grid operator's
one-second frequency log, the agent has to find every edit (to 1 s) and say
when each unedited stretch was recorded (to 2 s), or `null` if it was recorded
on a day the log does not cover. This is electrical network frequency (ENF)
analysis, the technique forensic examiners use to date and authenticate
recordings for court, applied to video. In most of the videos the grid is in
the flicker of mains-powered lamps, which rolling-shutter cameras record as
faint moving bands; in three it is elsewhere: in the frame timing of a camera
locked to the mains, in the hum of a sound track that the DVR muxed 3.6 s
behind its picture, and, for footage recorded while the grid logger was down,
only in another exhibit that covers the same minutes.

This is the third version. The first used audio recordings and was solved by
GPT-6.1-sol in 3 of 3 trials; the second used eight lamp-lit videos and was
solved by both agents in about half an hour. See
[`results/iteration-1.md`](results/iteration-1.md),
[`results/iteration-2.md`](results/iteration-2.md) and
[`docs/DESIGN.md`](docs/DESIGN.md#iteration-history).

| | |
|---|---|
| Task | [`tasks/enf-splice-forensics/`](tasks/enf-splice-forensics/) ([instruction](tasks/enf-splice-forensics/instruction.md), [README](tasks/enf-splice-forensics/README.md)) |
| Category | Security / Forensics |
| Agent timeout | 4 h, 2 CPUs, 4 GB |
| Verifier | separate container, parses `/app/report.json`, 10 pytest tests (CTRF), binary reward |

## Results

| Check (TB3 CI) | Result | Details |
|---|---|---|
| Static checks (28) | ✅ 28/28 pass | [`results/static-checks.md`](results/static-checks.md) |
| Implementation rubric review (36 criteria, claude-code + claude-sonnet-5) | ✅ 33 pass, 3 n/a, 0 fail | [`results/rubric-review.md`](results/rubric-review.md) |
| Docker build | ✅ | [`results/validation.md`](results/validation.md) |
| Oracle validation | ✅ reward 1.0 (13/13 tests) | [`results/validation.md`](results/validation.md) |
| Nop validation | ✅ reward 0.0 (0/13 tests) | [`results/validation.md`](results/validation.md) |
| `/run` claude-code · claude-opus-5-5 · max | ✅ 3/3 genuine failures (reward 0.0; 12, 11, 12 of 13 tests) | [`results/trials.md`](results/trials.md) |
| `/run` codex · gpt-6.1-sol · xhigh | ✅ 3/3 genuine failures (reward 0.0; 12 of 13 tests each) | [`results/trials.md`](results/trials.md) |
| `/cheat` claude-code · claude-opus-5-5 · max | ✅ reward 0.0 (searched for a bypass, found none) | [`results/cheat.md`](results/cheat.md) |
| `/cheat` codex · gpt-6.1-sol · xhigh | ⚠️ reward 0.0, but refused by OpenAI's safety filter at the first turn (no attempt) | [`results/cheat.md`](results/cheat.md) |
| Trial analysis (hosted-style, claude-code + claude-sonnet-5; 3 of 6 `/run` trials) | task specification ✅, reward hacking ✅, difficulty crux ✅, refusals ✅, timeout ✅; near miss ❌ on all three (discussed) | [`results/trial-analysis.md`](results/trial-analysis.md) |

Failure analysis: [`results/failure-analysis.md`](results/failure-analysis.md).

## Configuration and what "CI defaults" means here

- `/run` = 3 trials per agent, `/cheat` = 1 trial per agent with
  `docs/prompts/hack-trial-prompt.md` appended to the instruction through
  Harbor's `extra_instructions`, exactly as `scripts/ci/hosted_job_config.py`
  builds the hosted jobs. Agent timeout from `task.toml`.
- Agents and models are the ones the assignment names: **claude-code with
  `anthropic/claude-opus-5-5`, `reasoning_effort=max`** and **codex with
  `openai/gpt-6.1-sol`, `reasoning_effort=xhigh`**, with the per-agent settings
  `.github/harbor-run-defaults.yml` attaches to each agent name
  (`CLAUDE_CODE_MAX_OUTPUT_TOKENS=128000` for claude-code).
- Note: since 2026-09-21 (TB3 PR #2047) the repository's own `/run` defaults are
  `anthropic/claude-fable-5-1` and `openai/gpt-6-astra`; before that they were
  Opus 5 / GPT-5.6 Sol. The models above follow the assignment's explicit
  instruction; `tools/trials.sh` takes `CLAUDE_MODEL` / `CODEX_MODEL` to run the
  repository defaults instead.
- Credentials: subscription logins (`claude setup-token`, `codex login`) passed
  as `CLAUDE_FORCE_OAUTH`/`CLAUDE_CODE_OAUTH_TOKEN` and `CODEX_FORCE_AUTH_JSON`,
  as in the assignment's sample commands.

How to reproduce every row: [`docs/REPRODUCE.md`](docs/REPRODUCE.md).
Design, verification strategy and iteration history: [`docs/DESIGN.md`](docs/DESIGN.md).

## Repository layout

```
tasks/enf-splice-forensics/   the task (TB3 format)
  instruction.md              agent-facing instruction
  task.toml                   metadata, timeouts, resources (separate verifier)
  environment/                agent image: 11 MP4 exhibits + grid log
  solution/                   reference solution (enf_forensics.py)
  tests/                      verifier image: answer key (case_plan.py), tests, generator
tools/                        local equivalents of the TB3 CI jobs
docs/                         design notes and reproduction guide
results/                      check outputs, trial tables, analyses
```
