# `/run` trials (final version)

Configuration: [`tools/trials.sh`](../tools/trials.sh), as described in the
top-level README (claude-code with `anthropic/claude-opus-5-5`,
`reasoning_effort=max`; codex with `openai/gpt-6.1-sol`,
`reasoning_effort=xhigh`; 4 h agent timeout, 2 CPUs, 4 GB; Harbor
`--env docker`). Every trial ran against the same agent-facing task: the
instruction, `environment/` and `tests/` are unchanged since commit
`b7b82f4`; later commits changed only the reference solution, metadata and
documentation.

## Trials that count

| Job | Trial | Agent | Model | Effort | Reward | Tests passed | Agent time (min) | Tokens in / out | What it got wrong |
|---|---|---|---|---|---|---|---|---|---|
| run-codex-gpt-6.1-sol-20261023-031834 | EcKNWHM | codex | openai/gpt-6.1-sol | xhigh | **0.0** | 12/13 | 28 | 4,228,787 / 44,157 | exhibit_10 dated by its sound: −3.55 s |
| run-codex-gpt-6.1-sol-20261023-031834 | Bnav2jM | codex | openai/gpt-6.1-sol | xhigh | **0.0** | 12/13 | 33 | 5,119,094 / 55,558 | exhibit_10 dated by its sound: −3.53 s |
| run-codex-gpt-6.1-sol-20261023-171221 | H6sLQgM | codex | openai/gpt-6.1-sol | xhigh | **0.0** | 12/13 | 40 | 7,840,572 / 75,189 | exhibit_10 dated by its sound: −3.53 s |
| run-claude-code-claude-opus-5-5-20261023-032134 | 3tTQRNF | claude-code | anthropic/claude-opus-5-5 | max | **0.0** | 12/13 | 66 | 23,109,550 / 194,369 | exhibit_10 dated by its sound: −3.55 s |
| run-claude-code-claude-opus-5-5-20261023-171547 | 9Yo67mX | claude-code | anthropic/claude-opus-5-5 | max | **0.0** | 11/13 | 63 | 27,691,329 / 195,352 | exhibit_10 dated by its sound: −3.56 s; exhibit_11's outage insert left `null` |
| run-claude-code-claude-opus-5-5-20261023-171547 | bLEkjHD | claude-code | anthropic/claude-opus-5-5 | max | **0.0** | 12/13 | 66 | 18,591,408 / 191,033 | exhibit_10 dated by its sound: −3.29 s |

**3 of 3 genuine failures for each agent.** All six finished on their own well
inside the 4 h timeout (28 to 66 min) and wrote a complete report; five failed
a single test, the one for exhibit_10, and one failed two. Why, and what they
got right: [`failure-analysis.md`](failure-analysis.md).

## Trials that do not count

| Job | Trial | Agent | What happened |
|---|---|---|---|
| run-codex-gpt-6.1-sol-20261023-031834 | Q5uTfm3 | codex | ChatGPT usage limit reached 3 min in ("You've hit your usage limit ... try again at 4:58 AM"); `NonZeroAgentExitCodeError`, no report. Replaced by H6sLQgM. |
| run-claude-code-claude-opus-5-5-20261023-032134 | ozBm8ce | claude-code | Stopped after 97 min when the run was paused overnight; `CancelledError`. Replaced. |
| run-claude-code-claude-opus-5-5-20261023-032134 | k59RMMg | claude-code | Stopped after 26 min when the run was paused overnight; `CancelledError`. Replaced. |
| run-codex-gpt-6.1-sol-20261023-050018 | QTRAUkT | codex | Stopped a minute after launch when the run was paused overnight; `CancelledError`. Replaced by H6sLQgM. |

## Earlier versions

- Iteration 1 (audio): [`iteration-1.md`](iteration-1.md), GPT-6.1-sol 3/3 solved.
- Iteration 2 (lamp-lit video): [`iteration-2.md`](iteration-2.md), GPT-6.1-sol 2/2 and Claude 1/1 solved.
