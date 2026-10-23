# Reference-solution robustness

The verifier only ever sees one data set (the committed evidence), and the
reference solution scores 1.0 on it with every edit within 0.23 s of the true
point and every recording time within 0.53 s. These checks ask a different
question: is that success principled, or tuned to one lucky draw? Scripts are
in `tools/robustness/`; all numbers are for the final reference solution.

## 1. Every stretch of the official data is identifiable

[`identifiability-audit.md`](identifiability-audit.md) (`audit.py`): every
dated stretch is its own best match in the whole four-day log, through the
channel that carries its grid signal (flicker, frame timing or sound; margins
+0.031 to +0.249 over the best other time, +0.099 to +0.561 locally); neither
out-of-log stretch has a distinctive match; the stretch recorded during the
logger outage matches exhibit_08 at its true offset (0.980 against 0.896) and
phase-locks to it at 0.997; every splice steps the flicker phase by at least
1.28 rad and leaves the band depth unchanged; every exposure change steps it by
a similar amount but changes the band depth by 0.36x to 2.39x; and exhibit_10's
sound lags its picture by 3.60 s at both seen-and-heard events.

## 2. Thresholds moved up and down (official data)

`perturb.py`: each decision threshold of the reference solution changed on its
own; the full solution (channels, A/V offset, cross-video dating) re-run on
the official data and scored with the verifier's rules.

| Threshold | Default | Lower | Higher |
|---|---|---|---|
| `STEP_T` (phase step marking an edit) | 25 | 18 ✅ | 35 ✅ |
| `FREE_STEP_T` (step without log) | 30 | 20 ✅ | 45 ✅ |
| `CUSUM_DROP` (when a model stops growing) | 12 | 8 ✅ | 18 ✅ |
| `ANCHOR_GAP` (global match margin) | 0.05 | 0.035 ✅ | 0.07 ✅ |
| `LOCAL_GAP` (match margin near a neighbour) | 0.05 | 0.035 ✅ | 0.07 ✅ |
| `GROUP_CORR` (harmonics moving together) | 0.35 | 0.25 ✅ | 0.5 ✅ |
| `LOCAL_COH` (continuation coherence, relative to the neighbour) | 0.9 | 0.85 ✅ | 0.95 ✅ |
| `TIE_COH` (phase fit that settles a tie between days) | 0.98 | 0.97 ✅ | 0.99 ✅ |
| `TIE_LEAD` (its lead over the runner-up) | 0.15 | 0.1 ✅ | 0.2 ❌ exhibit_04 |
| `LOCK_COH` (phase lock against another video) | 0.97 | 0.95 ✅ | 0.99 ✅ |

| Exposure-change test | Result |
|---|---|
| band depth must change by more than 10 % (default 15 %) | ✅ |
| band depth must change by more than 25 % | ✅ |
| 0.6 x the depth change the phase step implies (default 0.8) | ✅ |
| 1.0 x the depth change the phase step implies | ✅ |

23 of 24 threshold variants and all four exposure-test variants still solve
all eleven videos. The one failure is the trap exhibit_04 was built around: its
second recording was made on Nov 6 around 20:00 and competes with the
scheduled 20:00 swing that recurs every day; the phase fit at the true time
leads the look-alike day by about 0.2, so demanding a lead of 0.2 leaves it
undated.

## 3. Other random draws of the same case

`seed_sweep.py`: the generator re-run with six other seeds (new grid history,
people, camera jitter, frame drops, sensor noise and sound; same case plan,
every joint re-nudged the same way to a phase step of at least 1.2 rad), then
the unchanged reference solution scored with the verifier's rules.

| Seed | Videos correct | Misses |
|---|---|---|
| 1 | 9/11 | 08 (nothing dated), 11 (outage insert undated, because 08 is) |
| 2 | 11/11 | |
| 3 | 10/11 | 04 (first recording undated) |
| 4 | 9/11 | 01 (insert undated), 05 (a stretch split in two) |
| 5 | 11/11 | |
| 6 | 11/11 | |
| **Total** | **61/66** | |

The misses are draws where a stretch's trace match is unusually weak, not
errors of the new mechanisms: the line-locked camera and the late sound are
right in all six draws, and the outage insert is dated in every draw where
exhibit_08 is. In seed 1 the best global match for exhibit_08's first stretch
is a wrong time (margin −0.031) and its last stretch is shorter than the
solution's 180 s anchor window, so nothing in it is dated, and the insert
that can only be dated through it stays `null`. In seeds 3 and 4 a 3 to
4.5 minute stretch clears none of its 180 s windows' anchor margins (+0.029 to
+0.044 over the whole stretch), and the solution leaves it undated rather than
guess; seed 4's exhibit_05 has the smallest margins of the sweep (+0.027 to
+0.057). The committed draw has no such weak spot: every dated stretch is its
own best match in the whole log, and the weakest (+0.031) sits next to a
neighbour that pins it down.

An earlier run of the same sweep scored 60/66: in seed 5 an out-of-log insert
locked by chance (0.977) to footage from four days earlier while the two
videos' relative clock rate was fitted freely. Taking the rate from the videos'
own dated stretches removed it (0.765) without touching the true lock (0.997).
For comparison, the audio version of the task scored 38/48 and the lamp-lit
video version 41/48 on the same kind of sweep.
