# Trial analysis (hosted-style)

TB3 CI follows `/run` and `/cheat` with an automated review of every trial
(`scripts/ci/stage_hosted_analysis.py`, the six criteria of
`docs/prompts/trial-analysis.toml`, claude-code with
`anthropic/claude-sonnet-5`). `tools/analyze.sh` stages the same review
locally. It was run on the two most recent `/run` jobs, three of the six valid
trials:

| Trial | Agent | task_specification | reward_hacking | difficulty_crux | near_miss | refusals | low_timeout |
|---|---|---|---|---|---|---|---|
| H6sLQgM | codex · gpt-6.1-sol | ✅ pass | ✅ pass | ✅ pass | ❌ fail | ✅ pass | ✅ pass |
| 9Yo67mX | claude-code · opus-5.5 | ✅ pass | ✅ pass | ✅ pass | ❌ fail | ✅ pass | ✅ pass |
| bLEkjHD | claude-code · opus-5.5 | ✅ pass | ✅ pass | ✅ pass | ❌ fail | ✅ pass | ✅ pass |

Analysis jobs: `analysis-run-codex-gpt-6.1-sol-20261023-171221` and
`analysis-run-claude-code-claude-opus-5-5-20261023-171547`.

## What the reviewer found

- **task_specification (pass).** "instruction.md precisely specifies ... the
  semantics of utc ('when the frame at start was recorded', i.e. picture time,
  or null if outside logged days), tolerances (1s for boundaries, 2s for utc)."
- **reward_hacking (pass).** No trial touched the solution, the tests, the
  answer key or the reward files; all of them did genuine signal processing.
- **difficulty_crux (pass).** The failures are the difficulty the author
  described: "The task's difficulty explanation specifically calls out
  exhibit_10 (the LED-lit room) as a case where ... the DVR muxed the sound
  3.6 s behind the picture, ... while the instruction asks when the picture was
  taken."
- **refusals, low_timeout (pass).** All three engaged fully and finished in 40
  to 66 minutes of a 4 h budget.

## The near-miss flag, and why it does not mean the threshold is doing the work

TB3 asks this question because "if many trials are near misses, the task may
appear harder than it is: the threshold is doing the work, not the conceptual
challenge." The reviewer flagged all three trials because they passed 11 or 12
of 13 tests and missed exhibit_10's 2 s tolerance with errors of 3.29 to
3.56 s ("a structurally and substantively correct solution that missed one
numeric tolerance").

The numbers are close, but the error is not a measurement error that a
slightly looser threshold would forgive; it is the size of a conceptual
mistake. An analysis that dates exhibit_10's picture lands about 0.1 s from the
truth (the reference solution: 0.10 s); one that dates its sound instead lands
3.3 to 3.6 s off, whatever its precision, because that is how far the DVR
muxed the sound behind the picture. Every other time the six agents reported
was within 0.63 s. The 2 s tolerance, set for unrelated reasons (where a
one-second log reading sits within its second, plus the accuracy of a trace
match), falls in the wide gap between the two answers.

What the flag does point at, fairly, is how concentrated the agents'
difficulty is: they solved ten of eleven videos, including two that were built
to need a non-obvious insight (the line-locked camera's frame timing, and the
outage insert dated through another exhibit). Their failures all come from one
question they did not ask. A larger A/V lag would make the categorical nature
of the error plain in the numbers without changing anything else; the 3.6 s
used here is within the range of real DVR and body-worn-camera desync.
