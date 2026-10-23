# Design notes: enf-splice-forensics

Background for discussing the task: what it asks, why it is hard, how it is
verified, and how it got to its current form.

## The idea

The frequency of the mains is never exactly 50 Hz: it wanders by tens of
millihertz from second to second as supply and demand shift, every synchronous
grid shares one wander, and transmission operators log it once a second.
Anything that picks up the mains therefore carries an unforgeable timestamp.
This is **electrical network frequency (ENF) analysis**, a real forensic
discipline: police laboratories and independent examiners use it to date and
authenticate recordings for court.

Most ENF work is on audio, where the mains leaks in as hum. Video carries it
too, through the light. Lamps on the mains flicker at twice the grid
frequency, and a CMOS camera with a rolling shutter reads its sensor one row
after another, so each frame samples the flicker at a few hundred instants
spread over its readout time. The result is faint horizontal bands whose
phase in each frame is the lamp phase at that frame's readout time. Extract
that phase frame by frame and you have the grid frequency, and with it a clock
and a tamper seal: where someone cut the footage or spliced in other footage,
the band phase jumps and its time line breaks.

The task hands the agent eight "exhibits" (silent H.264 videos from security,
body-worn and web cameras) and four days of grid log, and asks for every edit
point (to 1 s) and the original recording time of every unedited stretch (to
2 s), or `null` for stretches recorded on days the log does not cover. One
report, binary reward.

## Why it is hard (and why that is fair)

The front end is real signal processing: the bands are one to three per cent
of the light (a grey level or two after gamma) and compression erases part of
them; the row readout time that sets their spacing is not in the files and
differs between cameras; the scene has to be cancelled without cancelling the
bands; people walk through; body-worn cameras jitter; at 30 fps the bands roll
a third of a cycle per frame, at 25 fps they stand almost still. Each exhibit
then isolates one thing a forensic examiner has to get right:

| Exhibit | What it is | What makes it hard |
|---|---|---|
| 01 | Office CCTV (30 fps) with a 3.2 min insert of the same camera's footage from two days earlier, and a 9.3 s cut | Same room, same lamps, nobody in view at the joints: the picture shows no seam. Only the flicker phase and the log give it away; it has the smallest splice step of the set (1.28 rad). |
| 02 | Lobby body-worn camera, unedited, recorded three days after the log ends; the camera re-exposes once | No log to check against. The exposure change steps the flicker phase by 1.31 rad, as much as a splice, and must not be reported as an edit: the band depth falls to under half, the brightness settles, and a person walks through the moment without a break. |
| 03 | USB webcam, unedited, which dropped 202 frames in short bursts | The frame timestamps, not the frame count, are its time line. Treating frames as evenly spaced breaks the phase continuity about a hundred times. |
| 04 | PAL (25 fps) shop camera: two recordings made two days apart, both around 20:00, joined by 83 s from a recording made after the log period | At 25 fps a 100 Hz flicker advances exactly four cycles per frame, so the bands stand almost still and a naive scene estimate absorbs them. The 20:00 schedule swing repeats every day. Around the unexplained insert the neighbours' residual phases drift and periodically line up again, which pulled the reference solution's first boundary estimates 12 to 17 s off. |
| 05 | Corridor body-worn camera with a 31.7 s cut, a 5.1 s cut, and two exposure changes | The exposure changes (1.18 rad each; band depth halves, then doubles) are not edits; telling them from the cuts takes the log (an exposure change keeps the timing) or the physics of the change. |
| 06 | Warehouse CCTV cut into three pieces of about 3.3 min and reassembled out of order | Every piece has to be dated on its own to 2 s; the joints have no visual seam. |
| 07 | Budget camera that stamps 30 fps but really runs at 29.97 fps, 5.6 s cut just after the 08:00 schedule change | A clock error of −999 ppm: the flicker appears 0.1 Hz off and time stretches by 0.1 %; a phase model has to include the clock ratio or it decoheres within seconds. |
| 08 | Office CCTV that starts inside a 45 min logger outage, 17.4 s cut | The first 4.4 min cannot be matched at all. The examiner must establish from the footage itself that they belong to the same unedited stretch, and date its start by extrapolating across the outage. |

None of these is a trick: each is a situation that comes up in real case work
(weak flicker under modern lighting, cameras with unknown sensor timing, PAL
frame rates, webcams that drop frames, auto-exposure, NTSC-style 29.97 fps
clocks, database gaps, rearranged evidence). The instruction states the output
contract and the tolerances and that the scenes were lit by mains-powered
lamps; it says nothing about how to get there.

What separates expert from non-expert approaches:

- **Getting the signal at all.** The global brightness of a frame barely
  flickers (the bands largely average out over the frame), and at 25 fps what
  is left aliases to a slow drift that cannot be told from scene changes. The
  information is in the band phase, which needs the band spacing, a scene
  estimate, and a robust per-row measurement.
- **Phase, not just frequency.** A frequency trace can only locate a cut to
  several seconds. Integrating the log predicts the flicker phase to a
  fraction of a radian; under the right model the residual phase is flat and
  every edit is a step.
- **Not every step is an edit.** Exposure changes step the phase too. A
  longer exposure integrates the flicker over a longer window, which makes the
  bands fainter by sinc(100 Hz × E) and moves their phase back by
  π × 100 Hz × ΔE. A cut does neither, and it changes the timing.
- **Significance, not just maximum correlation.** Four days of log contain
  345,600 candidate lags; a two-minute trace correlates at r > 0.95 with many
  of them where a schedule swing dominates it.
- **Camera clocks and timestamps.** Coherent phase models must include the
  clock ratio, and dropped frames must be handled through the timestamps.
- **Log gaps.** Where the log is missing, continuity has to be established
  from the footage itself.

## Verification

- The agent writes one JSON file. The verifier (separate container) parses it;
  no agent code ever runs there, so there is no execution sandbox to escape and
  no reward channel to tamper with.
- Expected values come from `tests/case_plan.py`, the plan the evidence was
  built from (cameras, clock errors, session start times, exposure changes,
  which piece of which session went where). Nothing is hand-typed:
  `answer_key()` computes the expected stretches, and
  `tests/synthesize_evidence.py` rendered the videos from the same plan. The
  videos, the log and the plan are byte-for-byte reproducible.
- Tolerances: edit points ±1 s, times ±2 s. The reference solution places every
  edit within 0.23 s and dates every stretch within 0.41 s. Wrong matches are
  off by minutes to days. Both bounds sit in wide empty bands between correct
  and incorrect answers.
- Every splice was placed (to the frame, or for the 25 fps camera by shifting a
  session start by 4 ms) so that the flicker phase steps by at least 1.28 rad.
  Without this, a join between two moments whose grid phases happen to
  coincide would be physically invisible and the 1 s requirement would be
  unfair. Exposure changes step it by 1.18 to 1.31 rad, so step size alone
  does not separate them from edits.
- Ten pytest tests (coverage of all videos, tiling, one per video) with a CTRF
  report; reward 1 only if all pass.

### Anti-cheat

The answer key exists only in the verifier image. The agent image holds the
eight MP4 files and the CSV log. The files carry no metadata beyond the muxer's
encoder string; every file was encoded with identical x264 settings and fixed
keyframe spacing (scene-cut detection off), so neither the container nor the
codec structure marks an edit. The grid history is simulated, so there is
nothing to find online. Guessing is hopeless: 18 stretches, each needing the
right count, boundaries to ±1 s and a time to ±2 s within a four-day span.

## Reference solution (summary)

`solution/enf_forensics.py`, about 900 lines, numpy/scipy/av only, about
2.5 min for all eight exhibits:

1. **Flicker front end.** Per-pixel median of a frame sample as the static
   scene; per frame, the column median of frame / scene for every sensor row
   (gamma undone); the band spacing as the spatial frequency whose amplitude
   varies most between frames; a robust per-frame least-squares fit of the
   bands at that frequency and its double; removal of the constant bias left by
   bands that stood still while the scene was sampled (circle centre of the
   per-frame amplitudes); demodulation at 100 and 200 Hz with the frame
   timestamps, resampled to a 20 Hz complex baseband. From here the flicker is
   treated as harmonics 2 and 4 of a mains hum.
2. Maximum-likelihood ENF trace (SNR-weighted sum of periodograms).
3. Dating: gap-aware normalised cross-correlation against the whole log
   (accepted only with a clear margin over the second-best lag), and, for
   stretches next to dated ones, a local search near the neighbours' implied
   times with their clock ratio fixed.
4. Phase model per dated stretch: log offset plus clock ratio, fitted by
   maximising the coherence of the flicker phase against the phase integrated
   from the log readings. Each model grows until its residual phase steps (and
   the step is not an exposure change) or decoheres, crossing log gaps only if
   a reference-free phase-step test sees no discontinuity.
5. Neighbouring stretches are merged when their implied times agree within
   2 s; boundaries are refined by a two-model change point on the phase
   agreement, or next to unexplained footage at the first lasting phase step;
   unexplained footage is `null`, split only at reference-free phase steps that
   are not exposure changes.

## Iteration history

1. **Domain choice.** A task that uses real expertise, verifies a hidden
   ground truth exactly, and has nothing to find online. ENF forensics fits, and
   synthetic data with a known generating plan gives an exact answer key.
2. **Iteration 1: audio** (tag `iteration-1-audio`; `results/iteration-1.md`).
   Eight recordings with mains hum, appliance and inverter tones, phone
   band-limiting, AGC, an 870 ppm recorder clock, the same log and the same
   report format. It passed every automated check, and GPT-6.1-sol solved it
   three times out of three in 11 to 25 minutes with the textbook pipeline; it
   also exploited the fact that every edit sat on a round ten seconds. Audio
   ENF is too well trodden to be hard, so the task moved to video, and edit
   points moved off round numbers.
3. **Iteration 2: video.** First render: flicker deep enough (5 to 15 %) that
   the per-frame phase was exact to 0.03 rad. Lamp depths were cut by about
   three times, to the range where H.264 still keeps the bands; below about a
   quarter of the original depth x264 drops them from the P-frames entirely.
4. **Oracle development surfaced design problems**, fixed in the generator or
   in a principled oracle change, never by weakening the verifier:
   - the band-spacing estimator chose the lowest frequency it was allowed to,
     where the sinusoid is nearly collinear with the brightness trend; it now
     measures the energy the bands explain, not the size of their coefficient;
   - the exposure changes, as first planned, stepped the phase by only 0.6 to
     0.76 rad, clearly less than any splice, so a threshold on step size would
     have separated them; they were made 1.18 to 1.31 rad and the smallest
     splice 1.28 rad, and the oracle tells them apart by the band-depth change
     the physics requires;
   - the lamp fingerprint used to test "same footage" (a combination of the
     100 and 200 Hz band phases that is invariant to timing and exposure) was
     averaged over windows that straddled an exposure change; it is now formed
     per block;
   - next to an unexplained insert, a neighbour's residual phase drifts, lines
     up again 20 s later, and pulled the boundary there; one-sided boundaries
     now snap to the first lasting phase step, where the stretch stopped
     growing.
