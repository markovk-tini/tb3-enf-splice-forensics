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
too, and in more than one way. Lamps on the mains flicker at twice the grid
frequency, and a CMOS camera with a rolling shutter reads its sensor one row
after another, so each frame samples the flicker at a few hundred instants:
faint horizontal bands whose phase in each frame is the lamp phase at that
frame's readout time. A camera locked to the mains ("line lock") starts every
frame at the same point of the mains cycle; its bands never move, and the grid
is in the frame timing instead. A recorder with a microphone picks up hum. Each
of these is a clock and a tamper seal: where someone cut the footage or spliced
in other footage, the phase jumps and its time line breaks.

The task hands the agent eleven "exhibits" (H.264 videos from security,
body-worn and web cameras, one with a sound track) and four days of grid log,
and asks for every edit point (to 1 s) and the original recording time of every
unedited stretch (to 2 s), or `null` for stretches recorded on days the log
does not cover. One report, binary reward.

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
| 03 | USB webcam, unedited, which dropped 202 frames in short bursts | The frame timestamps, not the frame count, are its time line. |
| 04 | PAL (25 fps) shop camera: two recordings made two days apart, both around 20:00, joined by 83 s from a recording made after the log period | At 25 fps the bands stand almost still and a naive scene estimate absorbs them. The 20:00 schedule swing repeats every day, so the frequency trace alone leaves the two days nearly tied. Around the unexplained insert the neighbours' residual phases drift and periodically line up again. |
| 05 | Corridor body-worn camera with a 31.7 s cut, a 5.1 s cut, and two exposure changes | The exposure changes (1.18 rad each; band depth halves, then doubles) are not edits; telling them from the cuts takes the log (an exposure change keeps the timing) or the physics of the change. |
| 06 | Warehouse CCTV cut into three pieces of about 3.3 min and reassembled out of order | Every piece has to be dated on its own to 2 s; the joints have no visual seam. |
| 07 | Budget camera that stamps 30 fps but really runs at 29.97 fps, 5.6 s cut just after the 08:00 schedule change | A clock error of −999 ppm: the flicker appears 0.1 Hz off and time stretches by 0.1 %. |
| 08 | Office CCTV that starts inside a 45 min logger outage, 17.4 s cut | The first 4.4 min cannot be matched at all; the stretch has to be dated by extrapolating across the outage. |
| 09 | Line-locked reception camera on a DVR, unedited | The flicker bands are frozen and pass for part of the scene; there is no flicker signal at all. The grid is in the DVR's millisecond frame timestamps: frames come every second mains cycle, so a "25 fps" stream drifts with the grid frequency (40/41 ms intervals; over 10 s the drift tracks the log at r = 0.97). |
| 10 | LED-lit data room on a DVR channel with a microphone, unedited | The LED panels do not flicker. The mains hum in the sound track dates the sound, but the DVR muxed the sound 3.6 s behind the picture; the instruction asks when the picture was taken. A ceiling light switched off and on is seen in one frame and heard as a click 3.6 s later. |
| 11 | Stockroom CCTV with 105 s of its own footage spliced in from 40 minutes earlier, recorded while the logger was down | The insert matches nothing in the log, but it comes from a logged day, so `null` is wrong. Only exhibit_08, which covers the same minutes, can date it: the two recordings of the same moments see the same wander of the mains phase. |

None of these is a trick: each is a situation that comes up in real case work
(weak flicker under modern lighting, cameras with unknown sensor timing, PAL
frame rates, line-locked analogue-era cameras, webcams that drop frames,
auto-exposure, 29.97 fps clocks, DVRs whose sound is out of sync, database
gaps, rearranged evidence). The instruction states the output contract and the
tolerances; it says nothing about how to get there, nor where the grid is in
the footage.

What separates expert from non-expert approaches:

- **Getting the signal at all.** The global brightness of a frame barely
  flickers (the bands largely average out over the frame), and at 25 fps what
  is left aliases to a slow drift that cannot be told from scene changes. The
  information is in the band phase, which needs the band spacing, a scene
  estimate, and a robust per-row measurement.
- **The grid is not always in the light.** A video with frozen bands or no
  flicker is not a video without ENF: check the frame timing and the sound.
- **Which clock does a signal belong to?** A sound track dates the sound; the
  question is about the picture. A stretch that matches nothing in the log may
  still be from a logged day, if it fell in a logger gap.
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
  of them where a schedule swing dominates it, and even phase coherence can
  reach 0.98 at a wrong time for a short stretch.

## Verification

- The agent writes one JSON file. The verifier (separate container) parses it;
  no agent code ever runs there, so there is no execution sandbox to escape and
  no reward channel to tamper with.
- Expected values come from `tests/case_plan.py`, the plan the evidence was
  built from (cameras, clock errors, session start times, exposure changes,
  light switches, which piece of which session went where). Nothing is
  hand-typed: `answer_key()` computes the expected stretches, and
  `tests/synthesize_evidence.py` rendered the videos from the same plan. The
  videos, the log and the plan are byte-for-byte reproducible.
- Tolerances: edit points ±1 s, times ±2 s. The reference solution places every
  edit within 0.23 s and dates every stretch within 0.53 s. Wrong matches are
  off by minutes to days; the sound of exhibit_10 is 3.6 s from its picture.
  Both bounds sit in wide empty bands between correct and incorrect answers.
- Every splice was placed (to the frame, or for the 25 fps camera by shifting a
  session start by 4 ms) so that the flicker phase steps by at least 1.28 rad.
  Without this, a join between two moments whose grid phases happen to
  coincide would be physically invisible and the 1 s requirement would be
  unfair. Exposure changes step it by 1.18 to 1.31 rad, so step size alone
  does not separate them from edits.
- Thirteen pytest tests (coverage of all videos, tiling, one per video) with a
  CTRF report; reward 1 only if all pass.

### Anti-cheat

The answer key exists only in the verifier image. The agent image holds the
eleven MP4 files and the CSV log. The files carry no metadata beyond the
muxer's encoder string; every file was encoded with identical x264 settings and
fixed keyframe spacing (scene-cut detection off), so neither the container nor
the codec structure marks an edit. The DVR exhibits' millisecond timestamps and
the sound track are evidence, not leaks: they are what the camera and DVR
would record. The grid history is simulated, so there is nothing to find
online. Guessing is hopeless: 24 stretches, each needing the right count,
boundaries to ±1 s and a time to ±2 s within a four-day span.

## Reference solution (summary)

`solution/enf_forensics.py`, about 1,200 lines, numpy/scipy/av only:

1. **Channels.** Every video is analysed through each channel that can carry
   the grid, and the channel that dates most of it is kept:
   - *flicker*: per-pixel median of a frame sample as the static scene; per
     frame, the column median of frame / scene for every sensor row (gamma
     undone); the band spacing as the spatial frequency whose amplitude varies
     most between frames; a robust per-frame least-squares fit of the bands at
     that frequency and its double; removal of the constant bias left by bands
     that stood still while the scene was sampled (circle centre of the
     per-frame amplitudes); demodulation at 100 and 200 Hz with the frame
     timestamps, resampled to a 20 Hz complex baseband;
   - *frame timing*: for a nominal rate that divides 50 Hz, frame n is taken as
     50/fps × n mains cycles after frame 0 (a line-locked camera);
   - *sound*: each mains harmonic brought down to a complex baseband.
   All three give the baseband of a mains harmonic; from here the analysis is
   the same.
2. Maximum-likelihood ENF trace (SNR-weighted sum of periodograms).
3. Dating: gap-aware normalised cross-correlation against the whole log,
   accepted only with a clear margin over the second-best lag; where the trace
   leaves several days nearly tied, a phase-model fit at each candidate decides.
   Stretches next to dated ones are first tested near the neighbours' implied
   times with their clock ratio fixed, and accepted only if their phase follows
   the log about as coherently as the neighbour's (piecewise across exposure
   changes).
4. Phase model per dated stretch: log offset plus clock ratio, fitted by
   maximising the coherence of the phase against the phase integrated from the
   log readings. Each model grows until its residual phase steps (and the step
   is not an exposure change) or decoheres, crossing log gaps only if a
   reference-free phase-step test sees no discontinuity.
5. Neighbouring stretches are merged when their implied times agree within
   2 s; boundaries are refined by a two-model change point on the phase
   agreement, or next to unexplained footage at the first lasting phase step;
   unexplained footage is split only at reference-free phase steps that are not
   exposure changes.
6. **Beyond one video.** Times from a sound track are moved to the picture by
   the lag between events that are both seen and heard (a frame-to-frame
   brightness step and a click). Footage the log cannot explain is tested
   against the other videos' dated footage by phase locking, with the two
   cameras' relative clock rate fitted, and dated through them.

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
3. **Iteration 2: video** (tag `iteration-2-video`; `results/iteration-2.md`).
   Exhibits 01 to 08 above, with the instruction noting that the scenes were
   lit by mains-powered lamps. Lamp depths were cut to the range where H.264
   still keeps the bands, and several oracle problems were found and fixed in
   principled ways (a band-spacing estimator biased towards the lowest
   frequency; exposure steps that were too small to be confusable with splices;
   a lamp fingerprint averaged across exposure changes; one-sided boundaries
   pulled 20 s off by a drifting residual phase). It passed every automated
   check, and both agents solved it in about half an hour with frame-exact edit
   points: GPT-6.1-sol 2/2, Claude Opus 5.5 1/1. Every trap in it announced
   itself, and every answer could be checked against the log.
4. **Iteration 3 (this version).** Exhibits 09 to 11 put the grid where an
   expert does not look first (frame timing, a late sound track, another
   exhibit), and the instruction no longer says the scenes were lamp-lit.
   Building the oracle for them surfaced three more problems, fixed in the
   oracle:
   - local continuations were accepted at 60 % of the neighbour's coherence;
     with the new renders, chance matches near the 3.2 min insert of exhibit_01
     reached 0.83 to 0.87 and were accepted; the bar is now 90 %, measured
     piecewise across exposure changes (which otherwise pull a true
     continuation down to 0.87);
   - exhibit_04's second 20:00 recording lost its trace margin to the same
     swing on other days; a phase fit at the tied candidates (0.995 at the
     true time, 0.79 at the look-alike) now decides;
   - cross-video phase locking ignored the two cameras' 14 ppm clock
     difference, which over 105 s turns the 100 Hz demodulation into a 0.9 rad
     ramp and pulled the outage insert 1.8 s off; the relative rate is now
     fitted, and the insert is dated within 0.18 s.
