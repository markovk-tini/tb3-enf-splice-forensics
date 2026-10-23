# Identifiability audit (official evidence)

Produced by `tools/robustness/audit.py` from the committed evidence, with the
reference solution's own front ends and matching primitives. Each video is
measured through the channel the reference solution dates it with: the lamp
flicker, the frame timing of the line-locked camera (exhibit_09), or the sound
track (exhibit_10, whose sound is compared with the log at the sound's own
time, 3.6 s before the picture's).

## 1. Every dated stretch points to one time in the log

For every true stretch: the correlation of its frequency trace with the log at
the true time, against the best other time anywhere in the four-day log with
the same log coverage, and against the best other time within ±15 min (at
least 30 s away). Out-of-log stretches: the best time anywhere against the
second best.

| Exhibit | Channel | Stretch | True time | r at true time | best other (log) | margin | best other (±15 min) | local margin |
|---|---|---|---|---|---|---|---|---|
| exhibit_01.mp4 | flicker | 0 (0-251 s) | 05 16:38:44 | 0.978 | 0.917 | +0.061 | 0.706 | +0.272 |
| exhibit_01.mp4 | flicker | 1 (251-441 s) | 03 15:07:52 | 0.984 | 0.885 | +0.099 | 0.713 | +0.271 |
| exhibit_01.mp4 | flicker | 2 (441-599 s) | 05 16:42:56 | 0.967 | 0.890 | +0.077 | 0.801 | +0.166 |
| exhibit_01.mp4 | flicker | 3 (599-740 s) | 05 16:45:43 | 0.885 | 0.767 | +0.119 | 0.606 | +0.279 |
| exhibit_02.mp4 | flicker | 0 (0-480 s) | not in log | - | 0.741 (any time) | +0.005 (best vs 2nd) | - | - |
| exhibit_03.mp4 | flicker | 0 (0-540 s) | 03 14:21:37 | 0.956 | 0.707 | +0.249 | 0.535 | +0.422 |
| exhibit_04.mp4 | flicker | 0 (0-265 s) | 04 19:56:10 | 0.984 | 0.810 | +0.174 | 0.528 | +0.456 |
| exhibit_04.mp4 | flicker | 1 (265-348 s) | not in log | - | 0.884 (any time) | +0.006 (best vs 2nd) | - | - |
| exhibit_04.mp4 | flicker | 2 (348-621 s) | 06 19:58:28 | 0.997 | 0.944 | +0.054 | 0.724 | +0.273 |
| exhibit_05.mp4 | flicker | 0 (0-288 s) | 04 09:03:12 | 0.968 | 0.793 | +0.175 | 0.630 | +0.338 |
| exhibit_05.mp4 | flicker | 1 (288-422 s) | 04 09:08:32 | 0.965 | 0.904 | +0.061 | 0.855 | +0.110 |
| exhibit_05.mp4 | flicker | 2 (422-563 s) | 04 09:10:51 | 0.973 | 0.868 | +0.105 | 0.772 | +0.201 |
| exhibit_06.mp4 | flicker | 0 (0-194 s) | 03 11:05:47 | 0.949 | 0.795 | +0.155 | 0.633 | +0.317 |
| exhibit_06.mp4 | flicker | 1 (194-402 s) | 03 11:02:20 | 0.929 | 0.759 | +0.170 | 0.535 | +0.394 |
| exhibit_06.mp4 | flicker | 2 (402-600 s) | 03 11:09:01 | 0.949 | 0.880 | +0.069 | 0.690 | +0.259 |
| exhibit_07.mp4 | flicker | 0 (0-401 s) | 06 07:53:30 | 0.992 | 0.871 | +0.122 | 0.822 | +0.170 |
| exhibit_07.mp4 | flicker | 1 (401-554 s) | 06 08:00:17 | 0.973 | 0.899 | +0.075 | 0.771 | +0.202 |
| exhibit_08.mp4 | flicker | 0 (0-546 s) | 05 09:53:40 | 0.979 | 0.789 | +0.190 | 0.419 | +0.561 |
| exhibit_08.mp4 | flicker | 1 (546-703 s) | 05 10:03:04 | 0.975 | 0.944 | +0.031 | 0.869 | +0.106 |
| exhibit_09.mp4 | frame timing | 0 (0-420 s) | 06 13:22:07 | 0.969 | 0.813 | +0.156 | 0.752 | +0.217 |
| exhibit_10.mp4 | sound | 0 (0-360 s) | 04 15:46:51 | 0.986 | 0.814 | +0.172 | 0.606 | +0.380 |
| exhibit_11.mp4 | flicker | 0 (0-213 s) | 05 10:31:12 | 0.995 | 0.948 | +0.046 | 0.896 | +0.099 |
| exhibit_11.mp4 | flicker | 1 (213-318 s) | 05 09:54:44 | no log readings (logger outage): see the table below | | | | |
| exhibit_11.mp4 | flicker | 2 (318-705 s) | 05 10:34:44 | 0.997 | 0.910 | +0.087 | 0.689 | +0.308 |

Every dated stretch beats every other time in the log (global margins +0.031
to +0.249; local margins +0.099 to +0.561). Neither out-of-log stretch has a
distinctive match (best vs second best +0.005 and +0.006). The smallest global
margin, exhibit_08's last stretch (+0.031), sits next to a stretch whose time
pins it down (+0.106 within ±15 min of it).

## 2. The stretch recorded during the logger outage is datable, against another video

exhibit_11's insert falls entirely inside the 45-minute logger outage: the log
has no readings for any of its 105 s. exhibit_08's first stretch covers the same
minutes (it is dated by extrapolating its model across the outage), and the two
recordings of the same grid match:

| Exhibit | Stretch | True time | Other video | r at the true offset | best other offset | margin |
|---|---|---|---|---|---|---|
| exhibit_11.mp4 | 1 (213-318 s) | 05 09:54:44 | exhibit_08.mp4 | 0.980 | 0.896 | +0.084 |

Phase locking is stronger still: with the two cameras' relative clock rate
taken from their dated stretches, the insert and exhibit_08 lock at coherence
0.997; the best chance lock of any out-of-log footage against any other video
is 0.938. (In one of the random draws of the seed sweep, a chance lock reached
0.977 when the relative clock rate was fitted freely; with the rate taken from
the host video's own dated stretches it fell to 0.765, which is why the
reference solution uses the host's clock.)

## 3. Every edit is visible in the flicker, and every exposure change is distinguishable from an edit

Flicker phase step (100 Hz component) at every joint and every exposure
change: the true step from the generator, the step measured in the footage
(free residual phase, 4 s windows on either side of the event; next to a joint
into a different time the residual drifts, so this measurement is rougher than
the truth), and the band depth after the event relative to before.

| Exhibit | Event | File time (s) | Phase step, truth (rad) | Phase step, measured (rad) | Band depth ratio, measured |
|---|---|---|---|---|---|
| exhibit_01.mp4 | edit | 251.40 | +1.28 | +0.77 | 0.99 |
| exhibit_01.mp4 | edit | 440.97 | -1.81 | -1.10 | 1.04 |
| exhibit_01.mp4 | edit | 599.27 | +1.74 | +1.44 | 1.09 |
| exhibit_02.mp4 | exposure change (not an edit) | 188.40 | -1.31 | -1.26 | 0.36 |
| exhibit_04.mp4 | edit | 265.20 | +1.94 | +2.22 | 1.01 |
| exhibit_04.mp4 | edit | 348.48 | +2.24 | +2.45 | 0.99 |
| exhibit_05.mp4 | exposure change (not an edit) | 233.70 | -1.17 | -1.22 | 0.42 |
| exhibit_05.mp4 | edit | 288.30 | +2.39 | +2.14 | 1.02 |
| exhibit_05.mp4 | exposure change (not an edit) | 370.47 | +1.18 | +1.07 | 2.39 |
| exhibit_05.mp4 | edit | 421.87 | +2.05 | +1.99 | 1.01 |
| exhibit_06.mp4 | edit | 194.47 | +1.92 | +1.63 | 0.92 |
| exhibit_06.mp4 | edit | 401.57 | +2.29 | +2.07 | 0.99 |
| exhibit_07.mp4 | edit | 401.20 | -2.12 | -2.04 | 1.00 |
| exhibit_08.mp4 | edit | 546.50 | +2.32 | +2.17 | 1.00 |
| exhibit_11.mp4 | edit | 212.60 | +1.65 | +0.79 | 1.00 |
| exhibit_11.mp4 | edit | 318.00 | +2.73 | +2.12 | 1.00 |

Every splice steps the phase by at least 1.28 rad and leaves the band depth
unchanged (0.92 to 1.09). The three exposure changes step it by 1.17 to 1.31
rad, the same range, but change the band depth by a factor of 0.36 to 2.39, in
the direction and by at least the amount a change of exposure time implies
(longer exposure: fainter bands, phase moved back). In exhibit_05 the log also
shows that the timing is unchanged across them; in exhibit_02, which the log
does not cover, the band depth, the brightness transient and the person
walking through the moment are the evidence.

## 4. The two non-flicker exhibits

- **exhibit_09 (line-locked camera).** The flicker bands carry nothing (they
  stand still in every frame); the DVR's millisecond frame timestamps do. Read
  as one frame every second mains cycle, they give a frequency trace that
  matches the log at the true time with r = 0.969 against 0.813 anywhere else
  (table above), and a phase model dates the recording within 0.05 s.
- **exhibit_10 (sound muxed late).** The picture has no flicker; the sound's
  hum matches the log at the sound's time (r = 0.986 against 0.814). The lag
  between picture and sound is fixed by two events that are both seen and
  heard: the light goes off in the frame at 97.300 s and its switch clicks at
  100.902 s; it comes back on at 233.800 s and clicks at 237.402 s. Both give
  3.60 s.

## 5. Phase coherence alone does not date a short stretch

At the true time the measured phase follows the phase integrated from the log
almost perfectly. One might expect any other time to be ruled out the same
way, because the grid's fast fluctuations differ from day to day. The table
fits a phase model (offset plus clock ratio) at the true time and at each of
the five strongest other trace matches anywhere in the log (the outage insert
is left out: there is no log to be coherent with).

| Exhibit | Stretch | Coherence at true time | Best coherence at another time (top-5 trace matches) |
|---|---|---|---|
| exhibit_01.mp4 | 0 (0-251 s) | 0.998 | 0.845 |
| exhibit_01.mp4 | 1 (251-441 s) | 0.998 | 0.948 |
| exhibit_01.mp4 | 2 (441-599 s) | 0.998 | 0.963 |
| exhibit_01.mp4 | 3 (599-740 s) | 0.998 | 0.920 |
| exhibit_03.mp4 | 0 (0-540 s) | 0.995 | 0.590 |
| exhibit_04.mp4 | 0 (0-265 s) | 0.992 | 0.766 |
| exhibit_04.mp4 | 2 (348-621 s) | 0.995 | 0.788 |
| exhibit_05.mp4 | 0 (0-288 s) | 0.964 | 0.704 |
| exhibit_05.mp4 | 1 (288-422 s) | 0.948 | 0.942 |
| exhibit_05.mp4 | 2 (422-563 s) | 0.999 | 0.982 |
| exhibit_06.mp4 | 0 (0-194 s) | 0.998 | 0.939 |
| exhibit_06.mp4 | 1 (194-402 s) | 0.997 | 0.952 |
| exhibit_06.mp4 | 2 (402-600 s) | 0.998 | 0.873 |
| exhibit_07.mp4 | 0 (0-401 s) | 0.999 | 0.797 |
| exhibit_07.mp4 | 1 (401-554 s) | 0.999 | 0.882 |
| exhibit_08.mp4 | 0 (0-546 s) | 0.998 | 0.567 |
| exhibit_08.mp4 | 1 (546-703 s) | 0.998 | 0.987 |
| exhibit_09.mp4 | 0 (0-420 s) | 0.997 | 0.816 |
| exhibit_10.mp4 | 0 (0-360 s) | 0.998 | 0.823 |
| exhibit_11.mp4 | 0 (0-213 s) | 0.999 | 0.798 |
| exhibit_11.mp4 | 2 (318-705 s) | 0.998 | 0.609 |

The true time is coherent throughout (0.948 to 0.999; the two lowest values
are the exhibit_05 stretches that contain an exposure change, whose phase step
the plain model does not allow for). But for two- to three-minute stretches,
times on other days that the trace match already ranks highly can also be very
coherent: exhibit_08's last stretch reaches 0.987 at a time 18 hours earlier.
Measured on the simulated grid itself, two random 140 s windows on different
days have a median coherence of 0.33, but one pair in ten exceeds 0.70, and
among 345,600 candidate times the best ones come close to 1. So a date for a
short stretch is only safe with the trace match, the phase and the
neighbouring stretches taken together, which is how the reference solution
dates the stretches with the smallest margins.
