# Design notes: enf-splice-forensics

Background for discussing the task: what it asks, why it is hard, how it is
verified, and how it got to its current form.

## The idea

Mains-powered equipment leaks a faint hum at the grid frequency (50 Hz in
Europe) and its harmonics into almost every recording made near it. The grid
frequency is never exactly 50 Hz: it wanders by tens of millihertz from second
to second as supply and demand shift, and every synchronous grid (Continental
Europe, Great Britain, ...) shares one wander. Transmission operators log it
once a second. A recording therefore carries an unforgeable timestamp: extract
the hum frequency over time, slide it along the operator's log, and the one
place it lines up is when it was recorded. Where someone cut the recording or
spliced in other audio, the hum's time line jumps and its phase breaks.

This is **electrical network frequency (ENF) analysis**, a real forensic
discipline. Police labs (the UK Metropolitan Police kept an ENF database for
years) and independent examiners use it to authenticate recordings for court.

The task hands the agent eight "exhibits" and four days of grid log and asks
for every edit point (to 1 s) and the original recording time of every
unedited stretch (to 2 s), or `null` for stretches recorded on days the log
does not cover. One report, binary reward.

## Why it is hard (and why that is fair)

Each exhibit isolates one thing a forensic examiner has to get right:

| Exhibit | What it is | What makes it hard |
|---|---|---|
| 01 | Living-room recording with a 3.5 min insert from two days earlier and a 12 s cut | The strongest hum harmonic (100 Hz) is dominated by an appliance tone 0.17 Hz below it; a trace taken from it, or from all harmonics naively, does not match the log. The right move is to notice the band does not move with the others and drop it. |
| 02 | Hall recording, unedited, made four days after the log ends | Nothing in the log matches. The best-looking time still correlates at r = 0.74; the examiner has to recognise a chance match and report `null`. |
| 03 | Office recording, unedited | Control: any spurious edit is wrong. |
| 04 | Two phone recordings made two days apart, both around 20:00, joined by 90 s from a recording made after the log period | Phone high-pass filter removes 50 Hz; the hum is only in harmonics. The hourly grid pattern repeats at 20:00 every day; a 90 s insert matches random times at r = 0.94 and must be left `null` with both boundaries placed to 1 s. |
| 05 | Phone kitchen recording with a 47 s cut and a 6 s cut | AGC and female speech crossing the hum bands; the 6 s cut changes the alignment by only 6 s, which frequency-trace matching cannot place to 1 s. |
| 06 | Plant-room camera recording cut into three pieces and reassembled out of order | An inverter tone at exactly 50.000 Hz contaminates the fundamental; the weakest hum of the set; each piece is only 3.5 to 4 minutes, so none of them is unique across four days of log on its own. The pieces have to be dated as parts of the same session. |
| 07 | Cheap recorder whose sample clock runs 870 ppm fast, 5.5 s cut just after the 08:00 schedule change | The clock error shifts the hum by 43.5 mHz and stretches time by 0.087 %; a phase model has to include the clock ratio or it decoheres within seconds. |
| 08 | Office recording that starts inside a 45 min logger outage, 18 s cut | The first 4.4 min cannot be matched at all. The examiner must decide, from hum phase continuity alone, that they belong to the same unedited stretch, and date its start by extrapolating the model across the outage. |

None of these is a trick: each is a situation that comes up in real ENF case
work (appliance interference, inverter/UPS hum, unmatched recordings, phone
band-limiting, cheap recorder clocks, database gaps, rearranged evidence). The
instruction states the output contract and the tolerances; it says nothing
about how to get there.

What separates expert from non-expert approaches:

- **Harmonic selection.** Real ENF is present at several harmonics that move
  together; a band taken over by another source does not. Picking the
  strongest band, or summing all of them, fails on 01 and 06.
- **Significance, not just maximum correlation.** Four days of log contain
  345,600 candidate lags. A 90 s trace correlates at r > 0.9 with many of them.
  Deciding *whether* a stretch matches at all needs a margin over the
  second-best match (or a prior from neighbouring stretches), not a fixed r
  threshold.
- **Phase, not just frequency.** The frequency trace is smeared over an 8 s
  analysis window and noisy, so it can only locate a cut to several seconds.
  The hum phase predicted by integrating the log is exact to a fraction of a
  radian; under the right model the residual phase is flat and every edit is a
  step. That is the standard ENF tamper-detection technique and the only way to
  hit 1 s on short cuts.
- **Recorder clock.** Coherent phase models must include the clock ratio
  (fitted to sub-ppm) or they lose coherence within seconds on exhibit 07.
- **Log gaps.** Where the log is missing, continuity has to be established from
  the recording itself (reference-free phase-step test).

## Verification

- The agent writes one JSON file. The verifier (separate container) parses it;
  no agent code ever runs there, so there is no execution sandbox to escape and
  no reward channel to tamper with.
- Expected values come from `tests/case_plan.py`, the plan the evidence was
  built from (devices, clock errors, session start times, which piece of which
  session went where). Nothing is hand-typed: `answer_key()` computes the
  expected stretches, and `tests/synthesize_evidence.py` rendered the audio from
  the same plan. The audio, the log and the plan are byte-for-byte reproducible.
- Tolerances: edit points ±1 s, times ±2 s. The reference solution places every
  edit at the true sample block (error < 0.01 s) and dates every stretch within
  0.91 s. Frequency-trace methods misplace short cuts by 2.5 to 7 s. Wrong
  matches are off by minutes to days. Both bounds sit in wide empty bands
  between correct and incorrect answers.
- Every splice was placed (to the sample, nudged by at most 3.25 ms) so the
  hum phase steps by at least 1.2 rad at every usable harmonic. Without this a
  join between two moments whose grid phases happen to coincide would be
  physically invisible and the 1 s requirement would be unfair. One joint in
  the first draft had a 0.19 rad step and was ambiguous within about ±5 s;
  that is how this constraint was found.
- Ten pytest tests (coverage of all recordings, tiling, one per recording) with
  a CTRF report; reward 1 only if all pass.

### Anti-cheat

The answer key exists only in the verifier image. The agent image holds the
eight FLAC files (no tags beyond the libFLAC vendor string) and the CSV log.
The grid history is simulated, so there is nothing to find online. Guessing is
hopeless: 18 stretches, each needing the right count, boundaries to ±1 s and a
time to ±2 s within a four-day span.

## Reference solution (summary)

`solution/enf_forensics.py`, about 580 lines, numpy/scipy/soundfile only,
about 75 s for all eight exhibits:

1. Complex baseband (20 Hz) around every harmonic of 50 Hz that the sample rate
   allows; keep the bands whose 8 s-STFT frequency tracks are mutually
   correlated (prefer a group of at least two), discarding crystal-steady bands.
2. Maximum-likelihood ENF trace (SNR-weighted harmonic sum of periodograms).
3. Dating: gap-aware normalised cross-correlation against the whole log
   (accepted only with a clear margin over the second-best lag), and, for
   stretches next to dated ones, a local search near the neighbours' implied
   times with their clock ratio fixed.
4. Phase model per dated stretch: log offset plus clock ratio, fitted by
   maximising the coherence of the hum phase against the phase integrated from
   the log readings. Each model grows until its residual phase steps (likelihood
   ratio > 25) or decoheres (CUSUM), crossing log gaps only if a reference-free
   phase-step test sees no discontinuity.
5. Neighbouring stretches are merged when their implied times agree within
   2 s; boundaries are refined by a two-model change point on the phase
   agreement; unexplained stretches are `null`.

## Iteration history

1. **Domain choice.** A task that uses real expertise, verifies a hidden
   ground truth exactly, and has nothing to find online. ENF forensics fits, and
   synthetic data with a known generating plan gives an exact answer key.
2. **First data set: hum far too strong** (25–38 dB SNR, r = 0.92–0.999 at the
   true lag from a single harmonic). Simple matching would solve it. Hum levels
   were cut by about 11 dB and device self-noise was added *after* the
   recorder's high-pass filter (before that, the filter did not reduce in-band
   SNR at all, which is physically wrong).
3. **Interferers** (appliance tone near 100 Hz, inverter at exactly 50 Hz),
   **a null insert** and **an outage** added. Each one forced a principled
   change in the oracle (band grouping, significance margins, reference-free
   continuity), which is the point: each trap is something an examiner must
   handle.
4. **Oracle development surfaced data problems**, fixed in the generator, not
   by weakening the verifier:
   - a splice with a 0.19 rad phase step that no method could place to 1 s →
     all splices nudged to ≥ 1.2 rad;
   - the inverter's 150 Hz harmonic made the 150 Hz residual phase wobble
     whenever the grid sat near 50.0006 Hz → inverter reduced to its 50 Hz
     fundamental (the trap on the fundamental remains).
5. **Robustness check**: the generator was re-run with four other seeds (new
   grid history, noise, speech and hum phases; same case plan) and the
   unchanged reference solution scored on each, to make sure it is not tuned to
   one draw (results in `results/oracle-robustness.md`).
