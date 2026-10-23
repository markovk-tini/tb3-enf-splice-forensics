# Identifiability audit (official evidence)

Produced by `tools/robustness/audit.py` from the committed evidence, with the
reference solution's own front end (flicker baseband) and matching primitives.

## 1. Every dated stretch points to one time in the log

For every true stretch: the correlation of its frequency trace (recovered from
the lamp flicker) with the log at the true time, against the best other time
anywhere in the four-day log with the same log coverage, and against the best
other time within ±15 min (at least 30 s away). Out-of-log stretches: the best
time anywhere against the second best.

| Exhibit | Stretch | True time | r at true time | best other (log) | margin | best other (±15 min) | local margin |
|---|---|---|---|---|---|---|---|
| exhibit_01.mp4 | 0 (0-251 s) | 05 16:38:44 | 0.980 | 0.915 | +0.066 | 0.702 | +0.278 |
| exhibit_01.mp4 | 1 (251-441 s) | 03 15:07:52 | 0.982 | 0.885 | +0.097 | 0.711 | +0.271 |
| exhibit_01.mp4 | 2 (441-599 s) | 05 16:42:56 | 0.968 | 0.882 | +0.086 | 0.813 | +0.155 |
| exhibit_01.mp4 | 3 (599-740 s) | 05 16:45:43 | 0.863 | 0.766 | +0.097 | 0.598 | +0.265 |
| exhibit_02.mp4 | 0 (0-480 s) | not in log | - | 0.743 (any time) | +0.002 (best vs 2nd) | - | - |
| exhibit_03.mp4 | 0 (0-540 s) | 03 14:21:37 | 0.961 | 0.704 | +0.257 | 0.534 | +0.427 |
| exhibit_04.mp4 | 0 (0-265 s) | 04 19:56:10 | 0.987 | 0.806 | +0.181 | 0.534 | +0.453 |
| exhibit_04.mp4 | 1 (265-348 s) | not in log | - | 0.897 (any time) | +0.039 (best vs 2nd) | - | - |
| exhibit_04.mp4 | 2 (348-621 s) | 06 19:58:28 | 0.997 | 0.943 | +0.054 | 0.725 | +0.272 |
| exhibit_05.mp4 | 0 (0-288 s) | 04 09:03:12 | 0.974 | 0.797 | +0.176 | 0.613 | +0.361 |
| exhibit_05.mp4 | 1 (288-422 s) | 04 09:08:32 | 0.967 | 0.903 | +0.064 | 0.853 | +0.115 |
| exhibit_05.mp4 | 2 (422-563 s) | 04 09:10:51 | 0.973 | 0.862 | +0.111 | 0.771 | +0.202 |
| exhibit_06.mp4 | 0 (0-194 s) | 03 11:05:47 | 0.946 | 0.793 | +0.153 | 0.636 | +0.310 |
| exhibit_06.mp4 | 1 (194-402 s) | 03 11:02:20 | 0.923 | 0.761 | +0.162 | 0.533 | +0.390 |
| exhibit_06.mp4 | 2 (402-600 s) | 03 11:09:01 | 0.950 | 0.879 | +0.071 | 0.687 | +0.263 |
| exhibit_07.mp4 | 0 (0-401 s) | 06 07:53:30 | 0.992 | 0.869 | +0.123 | 0.822 | +0.170 |
| exhibit_07.mp4 | 1 (401-554 s) | 06 08:00:17 | 0.972 | 0.897 | +0.075 | 0.769 | +0.203 |
| exhibit_08.mp4 | 0 (0-546 s) | 05 09:53:40 | 0.981 | 0.788 | +0.194 | 0.429 | +0.552 |
| exhibit_08.mp4 | 1 (546-703 s) | 05 10:03:04 | 0.976 | 0.940 | +0.037 | 0.865 | +0.112 |

Every dated stretch beats every other time in the log (global margins +0.037
to +0.257; local margins +0.112 to +0.552). Neither out-of-log stretch has a
distinctive match (best vs second best +0.002 and +0.039). The last two numbers
overlap: the 83 s insert in exhibit_04 matches a wrong time with as large a
margin as exhibit_08's last stretch has at its true time. A fixed margin over
the whole log cannot date one and reject the other; dating exhibit_08's last
stretch next to its neighbour's time (local margin +0.112) can.

## 2. Every edit is visible in the flicker, and every exposure change is distinguishable from an edit

Flicker phase step (100 Hz component) at every joint and every exposure
change: the true step from the generator, the step measured in the footage
(free residual phase, 4 s windows on either side of the event; next to a joint
into a different time the residual drifts, so this measurement is rougher than
the truth), and the band depth after the event relative to before.

| Exhibit | Event | File time (s) | Phase step, truth (rad) | Phase step, measured (rad) | Band depth ratio, measured |
|---|---|---|---|---|---|
| exhibit_01.mp4 | edit | 251.40 | +1.28 | +0.76 | 0.96 |
| exhibit_01.mp4 | edit | 440.97 | -1.81 | -1.13 | 1.05 |
| exhibit_01.mp4 | edit | 599.27 | +1.74 | +1.40 | 1.05 |
| exhibit_02.mp4 | exposure change (not an edit) | 188.40 | -1.31 | -1.29 | 0.36 |
| exhibit_04.mp4 | edit | 265.20 | +1.94 | +1.76 | 0.99 |
| exhibit_04.mp4 | edit | 348.48 | +2.24 | +2.51 | 1.00 |
| exhibit_05.mp4 | exposure change (not an edit) | 233.70 | -1.17 | -1.25 | 0.42 |
| exhibit_05.mp4 | edit | 288.30 | +2.39 | +2.21 | 1.01 |
| exhibit_05.mp4 | exposure change (not an edit) | 370.47 | +1.18 | +1.25 | 2.34 |
| exhibit_05.mp4 | edit | 421.87 | +2.05 | +1.97 | 1.01 |
| exhibit_06.mp4 | edit | 194.47 | +1.92 | +1.67 | 0.96 |
| exhibit_06.mp4 | edit | 401.57 | +2.29 | +2.15 | 1.04 |
| exhibit_07.mp4 | edit | 401.20 | -2.12 | -2.13 | 1.00 |
| exhibit_08.mp4 | edit | 546.50 | +2.32 | +2.05 | 0.99 |

Every splice steps the phase by at least 1.28 rad and leaves the band depth
unchanged (0.96 to 1.05). The three exposure changes step it by 1.17 to 1.31
rad, the same range, but change the band depth by a factor of 0.36 to 2.34, in
the direction and by at least the amount a change of exposure time implies
(longer exposure: fainter bands, phase moved back). In exhibit_05 the log also
shows that the timing is unchanged across them; in exhibit_02, which the log
does not cover, the band depth, the brightness transient and the person
walking through the moment are the evidence.
