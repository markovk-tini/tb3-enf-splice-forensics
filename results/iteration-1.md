# Iteration 1: audio ENF (superseded)

The first version of the task used **audio** recordings: eight synthetic
exhibits with mains hum at 50 Hz and its harmonics, the same 4-day grid log,
and the same report format as the final task. It passed every automated check
(static 28/28, rubric review clean, oracle 1.0, nop 0.0).

## Trials (harbor `--env docker`, task as of commit `c37ca1a`)

| Job | Trial | Agent | Model | Effort | Reward | Tests | Agent time |
|---|---|---|---|---|---|---|---|
| run-codex-gpt-6.1-sol-20261023-001334 | 2ePRYAj | codex | openai/gpt-6.1-sol | xhigh | **1.0** | 10/10 | 11 min |
| run-codex-gpt-6.1-sol-20261023-001334 | GiKJKGN | codex | openai/gpt-6.1-sol | xhigh | **1.0** | 10/10 | 14 min |
| run-codex-gpt-6.1-sol-20261023-001334 | ovTz88L | codex | openai/gpt-6.1-sol | xhigh | **1.0** | 10/10 | 25 min |
| run-claude-code-claude-opus-5-5-20261023-001334 | 3 trials | claude-code | anthropic/claude-opus-5-5 | max | - | - | infra error: `EnvironmentStartTimeoutError` (two harbor processes built the same image at once; the claude side's builds hung; agent never started) |
| run-claude-code-claude-opus-5-5-20261023-003057 | 3 trials | claude-code | anthropic/claude-opus-5-5 | max | - | - | cancelled during setup once GPT-6.1-sol had passed twice |

## What happened

GPT-6.1-sol solved the audio version three times in 11 to 25 minutes, with
the textbook expert pipeline:

1. long-term spectra to find which hum harmonics are usable (it dropped the
   tone-contaminated 100 Hz band of exhibit 01 on its own);
2. per-harmonic frequency tracks, matched against the log (gap-aware);
3. time jumps between matches to find edits; recognition of the out-of-log
   recording and of the unmatched insert;
4. hum-phase analysis at each suspected edit to place it, plus the recorder
   clock error when converting to UTC.

It also took a shortcut the data allowed: every edit sat on a whole multiple of
10 seconds, so approximate boundaries could be snapped to round numbers.

## What changed

Audio ENF is a well-documented technique and squarely within the model's
expertise; the traps (interfering tones, clock error, log outage, unmatched
stretches) cost it minutes, not hours. The task was moved to **video**: the
grid frequency has to be recovered from the faint bands that mains-powered
lighting leaves in rolling-shutter video, which adds camera physics (row
readout timing, frame-rate aliasing, exposure integration, frame drops,
auto-exposure steps that shift the band phase without being edits) on top of
the forensic reasoning. Edit points were also moved off round numbers.
