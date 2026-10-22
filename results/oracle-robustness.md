# Reference-solution robustness

The verifier only ever sees one data set (the committed evidence), and the
reference solution scores 1.0 on it with every edit placed at the true point
(error < 0.01 s) and every recording time within 0.91 s. These checks ask a
different question: is that success principled, or tuned to one lucky draw?

## 1. Every stretch of the official data is identifiable

[`identifiability-audit.md`](identifiability-audit.md): for every true
stretch, the correlation of its hum trace with the log at the true time versus
the best other time anywhere in the four-day log (same coverage) and within
±15 min. Every dated stretch beats every other time in the log (margins
+0.045 to +0.285); both unmatched stretches have no distinctive match (best vs
second best +0.007 and +0.005). Every splice steps the hum phase by at least
1.2 rad at each usable harmonic (by construction; see `tests/case_plan.py`).

## 2. Thresholds moved up and down (official data)

Each decision threshold of the reference solution changed on its own; the
solution re-run on the official data and scored with the verifier's rules.

| Threshold | Default | Lower | Higher |
|---|---|---|---|
| `STEP_T` (phase step marking an edit) | 25 | 20 ✅ | 32 ✅ |
| `GROUP_CORR` (harmonics moving together) | 0.35 | 0.28 ✅ | 0.45 ✅ |
| `ANCHOR_GAP` (global match margin) | 0.05 | 0.04 ✅ | 0.065 ❌ exhibit_04 |
| `LOCAL_GAP` (match margin near a neighbour) | 0.05 | 0.04 ✅ | 0.07 ✅ |
| `CUSUM_DROP` (when a model stops growing) | 12 | 8 ✅ | 18 ❌ exhibit_04 |
| `FREE_STEP_T` (step without log, in gaps) | 30 | 20 ✅ | 45 ✅ |

10 of 12 variants still solve all eight exhibits. Both failures are the same
stretch: exhibit_04's second recording, made on Nov 6 around 20:00, competes
with the scheduled 20:00 frequency swing that recurs every day (its best
window beats the next-best day by 0.066). That is the trap the exhibit was
built around; a stricter acceptance margin, or letting the first model run on
through the unmatched insert, loses it.

## 3. Other random draws of the same case

`tests/synthesize_evidence.py` re-run with six other seeds (new grid history,
noise, speech, hum coupling phases; same case plan, splices re-nudged the same
way), then the unchanged reference solution scored with the verifier's rules:

| Seed | Exhibits correct | Misses |
|---|---|---|
| 1 | 6/8 | 01 (insert split in two), 06 (first piece undated) |
| 2 | 7/8 | 01 (no stretch dated) |
| 3 | 8/8 | |
| 4 | 7/8 | 06 (last piece undated) |
| 5 | 6/8 | 01 (insert undated), 04 (insert end 3 s off) |
| 6 | 4/8 | 01, 04, 06, 07 (one stretch undated each) |
| **Total** | **38/48** | |

The misses concentrate on the two lowest-SNR exhibits (01 and 06), whose
3.5-minute pieces are not always unique against four days of log on a given
draw. The committed draw was audited stretch by stretch (section 1).
