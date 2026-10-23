# Reference-solution robustness

The verifier only ever sees one data set (the committed evidence), and the
reference solution scores 1.0 on it with every edit within 0.23 s of the true
point and every recording time within 0.41 s. These checks ask a different
question: is that success principled, or tuned to one lucky draw? Scripts are
in `tools/robustness/`.

## 1. Every stretch of the official data is identifiable

[`identifiability-audit.md`](identifiability-audit.md) (`audit.py`): for every
true stretch, the correlation of its flicker-derived frequency trace with the
log at the true time versus the best other time anywhere in the four-day log
(same coverage) and within ±15 min. Every dated stretch beats every other time
in the log (margins +0.037 to +0.257); neither out-of-log stretch has a
distinctive match (best vs second best +0.002 and +0.039). Every splice steps
the flicker phase by at least 1.28 rad and leaves the band depth unchanged;
every exposure change steps it by a similar amount but changes the band depth
by 0.36x to 2.34x.

## 2. Thresholds moved up and down (official data)

`perturb.py`: each decision threshold of the reference solution changed on its
own; the analysis re-run on the official data and scored with the verifier's
rules.

| Threshold | Default | Lower | Higher |
|---|---|---|---|
| `STEP_T` (phase step marking an edit) | 25 | 18 ✅ | 35 ✅ |
| `FREE_STEP_T` (step without log) | 30 | 20 ✅ | 45 ✅ |
| `CUSUM_DROP` (when a model stops growing) | 12 | 8 ✅ | 18 ✅ |
| `ANCHOR_GAP` (global match margin) | 0.05 | 0.035 ✅ | 0.07 ❌ exhibit_04 |
| `LOCAL_GAP` (match margin near a neighbour) | 0.05 | 0.035 ❌ exhibit_01 | 0.07 ✅ |
| `GROUP_CORR` (harmonics moving together) | 0.35 | 0.25 ✅ | 0.5 ✅ |

| Exposure-change test | Result |
|---|---|
| band depth must change by more than 10 % (default 15 %) | ✅ |
| band depth must change by more than 25 % | ✅ |
| 0.6 x the depth change the phase step implies (default 0.8) | ✅ |
| 1.0 x the depth change the phase step implies | ✅ |

14 of 16 variants still solve all eight exhibits. The two failures sit on the
traps the exhibits were built around. A stricter global margin (0.07) leaves
exhibit_04's second recording undated: it was made on Nov 6 around 20:00 and
competes with the scheduled 20:00 swing that recurs every day (its margin over
the best other day is 0.054). A looser local margin (0.035) accepts a spurious
nearby match inside exhibit_01 and splits a stretch.

## 3. Other random draws of the same case

`seed_sweep.py`: the generator re-run with six other seeds (new grid history,
people, camera jitter, frame drops and sensor noise; same case plan, every
joint re-nudged the same way to a phase step of at least 1.2 rad), then the
unchanged reference solution scored with the verifier's rules.

| Seed | Exhibits correct | Misses |
|---|---|---|
| 1 | 6/8 | 01 (insert undated), 08 (nothing dated) |
| 2 | 8/8 | |
| 3 | 6/8 | 01 (insert undated), 04 (first boundary 2.8 s late) |
| 4 | 6/8 | 01 (insert undated), 05 (a stretch split in two) |
| 5 | 7/8 | 04 (an extra stretch) |
| 6 | 8/8 | |
| **Total** | **41/48** | |

`audit.py` run on the failing draws shows where the misses come from. The
three undated inserts in exhibit_01 have global trace margins of only +0.083,
+0.044 and +0.029 in those draws. The 3.2 min insert is still the best match
for its true time, but no 180 s window inside it clears the solution's 0.05
anchor margin, so the solution leaves it `null` rather than guess. In seed 1,
the best global match for exhibit_08's first stretch is a wrong time (margin
−0.031). Its last stretch would date correctly but is shorter than the
solution's 180 s anchor window, so nothing gets dated. The other three misses
are in draws where exhibit_04's and exhibit_05's margins are among the
smallest of the sweep (+0.027 to +0.057). The committed draw has no such weak
spot: every dated stretch is its own best match in the whole log, and the
weakest (+0.037) is next to a neighbour that pins it down (section 1).

For comparison, the audio version of the task scored 38/48 on the same kind
of sweep.
