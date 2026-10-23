# Iteration 2: video ENF from rolling-shutter flicker (superseded)

The second version (tag `iteration-2-video`) moved the evidence to eight
silent H.264 videos. The grid frequency had to be recovered from the faint
bands that mains-lit lamps leave in rolling-shutter footage, with 30 and
25 fps cameras, a webcam that dropped frames, a camera running at 29.97 fps
while stamping 30, exposure changes that step the flicker phase as much as a
splice, an out-of-log insert between two 20:00 recordings, and edit points
off round numbers. It passed every automated check: static 28/28, rubric
review 34 pass / 2 n/a / 0 fail, oracle 1.0, nop 0.0.

## Trials (harbor `--env docker`, task as of commit `d9d328f`)

| Job | Trial | Agent | Model | Effort | Reward | Tests | Agent time | Worst errors (edit / time) |
|---|---|---|---|---|---|---|---|---|
| run-codex-gpt-6.1-sol-20261023-021504 | gAbA799 | codex | openai/gpt-6.1-sol | xhigh | **1.0** | 10/10 | 27 min | 0.00 s / 0.56 s |
| run-codex-gpt-6.1-sol-20261023-021504 | ND66knJ | codex | openai/gpt-6.1-sol | xhigh | **1.0** | 10/10 | 29 min | 0.00 s / 0.60 s |
| run-codex-gpt-6.1-sol-20261023-021504 | DraQCay | codex | openai/gpt-6.1-sol | xhigh | - | - | - | cancelled after 9 min |
| run-claude-code-claude-opus-5-5-20261023-021804 | rLjGVRv | claude-code | anthropic/claude-opus-5-5 | max | **1.0** | 10/10 | 34 min | 0.00 s / 0.43 s |
| run-claude-code-claude-opus-5-5-20261023-021804 | 868k4p6 | claude-code | anthropic/claude-opus-5-5 | max | - | - | - | cancelled after 36 min |
| run-claude-code-claude-opus-5-5-20261023-021804 | ZKDoSSt | claude-code | anthropic/claude-opus-5-5 | max | - | - | - | cancelled before start |

The remaining trials were cancelled once both agents had solved the task,
since they could no longer change the verdict.

## What happened

Both agents named the method in their first minute ("extract the lighting
flicker from each video and match it to the grid log") and executed it the
way the reference solution does:

1. decode with timestamps preserved, noticing the webcam's dropped frames;
2. per-row band measurements (Claude: column medians and a per-30 s fit of
   the band spacing; GPT: row-wise demodulation of the 10 Hz alias), with the
   25 fps exhibit handled by fitting the circle/ellipse the band phasors run
   around, the same bias fix the reference solution uses;
3. sliding-window matching against the log, then phase-level refinement;
4. every phase step checked against brightness, band depth and frame content:
   both classified the three exposure changes as lighting events, and Claude
   measured that real edits are "visually seamless" while the exposure events
   "coincide with visible scene changes";
5. both `null` stretches confirmed to have no reliable match.

Edit points came out frame-exact (0.00 s error) and times within 0.43 to
0.60 s, better than the reference solution's 0.23 s / 0.41 s on edits.

## What it means

ENF analysis of rolling-shutter video is as familiar to these agents as ENF
analysis of audio. Every trap in this version announced itself: dropped frames
show in the timestamps, exposure changes show in brightness and band depth,
the 25 fps bands are visibly static, and each stretch, once extracted, either
matches the log unmistakably or not at all. Making the task harder by turning
up noise or adding more traps of the same kind would not change that. The next
iteration needs evidence where the flicker is not where an expert first looks,
and where some answers cannot be checked against the log at all.
