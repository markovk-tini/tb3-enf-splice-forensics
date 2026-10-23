# Failure analysis (`/run`, final version)

All six valid trials failed, three per agent, and all of them failed on the
same video for the same reason. Each one dated exhibit_10 by its sound track
and reported that as the time of its picture, 3.3 to 3.6 s too early, outside
the 2 s tolerance. Five of the six got the other ten videos exactly right,
with edit points to the frame and recording times within 0.63 s; one Claude
trial also left the outage insert of exhibit_11 undated.

| Trial | Agent | Videos right | Worst edit error | exhibit_10 time error | Other misses |
|---|---|---|---|---|---|
| EcKNWHM | codex · gpt-6.1-sol · xhigh | 10/11 | 0.00 s | −3.55 s | |
| Bnav2jM | codex · gpt-6.1-sol · xhigh | 10/11 | 0.00 s | −3.53 s | |
| H6sLQgM | codex · gpt-6.1-sol · xhigh | 10/11 | 0.00 s | −3.53 s | |
| 3tTQRNF | claude-code · claude-opus-5-5 · max | 10/11 | 0.00 s | −3.55 s | |
| 9Yo67mX | claude-code · claude-opus-5-5 · max | 9/11 | 0.00 s | −3.56 s | exhibit_11's insert left `null` |
| bLEkjHD | claude-code · claude-opus-5-5 · max | 10/11 | 0.00 s | −3.29 s | |

Trial details, including the trials that did not count, are in
[`trials.md`](trials.md).

TB3's automated trial review, run on three of the six trials, agrees that the
task specification is clear, that there was no reward hacking and that the
failures are the difficulty the task describes; it also flags the trials as
near misses, which [`trial-analysis.md`](trial-analysis.md) discusses.

## What the agents got right

A lot. Both agents recognised within minutes that the grid has to be recovered
from the footage, extracted the rolling-shutter flicker bands with
scene-normalised per-row fits, handled the 25 fps camera whose bands stand
still, kept the webcam's dropped frames out of the edit list, corrected the
29.97 fps clock, told the exposure changes from the cuts, and placed every edit
on the right frame. Two parts of the task were built to need an insight that
is not in the ENF literature, and the agents found them on their own:

- **exhibit_09 (line-locked camera).** Its flicker bands are frozen, so the
  usual extraction finds nothing. All six trials worked out that the grid is in
  the DVR's millisecond frame timestamps instead ("One video's frame spacing
  tracks the mains frequency directly", codex; "the camera's frame timing
  follows the mains, so the frequency is recorded in its timestamps", Claude)
  and dated it within 0.13 s.
- **exhibit_11 (insert from the logger outage).** It matches nothing in the
  log, and `null` would be wrong. Five of the six trials matched it against
  exhibit_08, which covers the same minutes ("it matches exhibit_08's in-gap
  footage almost perfectly. I dated it that way, so it gets a real time rather
  than null", Claude), and dated it within 0.30 s; Claude's 9Yo67mX did not and
  reported `null`.

## What they got wrong

exhibit_10 is an LED-lit data room recorded by a DVR channel with a
microphone. The picture does not flicker; the sound carries mains hum from the
equipment in the room. The DVR muxed the sound 3.6 s behind the picture: a
ceiling light that goes off at 97.3 s in the picture is heard clicking at
100.9 s, and the light coming back on at 233.8 s clicks at 237.4 s. The
instruction defines `utc` as "when the frame at `start` was recorded".

Every trial found the hum, matched it to the log (a clean, unique match), and
reported the sound's time as the picture's. None of them measured the lag,
although they looked at the two light switches: they examined them as possible
edits and used the sound's continuous match across them to rule edits out.

- codex (Bnav2jM): "The audio also gives a continuous match for another video
  across two large brightness jumps."
- codex (H6sLQgM): "I'm checking those transitions against the images and, for
  exhibit 10, the audio."
- Claude (bLEkjHD): "The `exhibit_10` audio gives a clean ENF trace, best at
  the 100 Hz harmonic."
- Claude (3tTQRNF), in its final summary: "exhibit_10: the picture has no
  flicker, but the audio carries a 50/100 Hz hum" and "exhibit_10's brightness
  changes at 97.3 s and 233.8 s are also lighting changes, not cuts." Its list
  of "weakest calls" names the out-of-log insert of exhibit_04 and possible
  undetected edits in exhibit_02, but not the sound's clock.

## Why this is a genuine failure and not a flaw in the task

- **The question is unambiguous.** `utc` is when the *frame* at `start` was
  recorded; nothing in the instruction says the sound and the picture share a
  clock.
- **The answer is in the data.** Two events are both seen (the brightness
  changes in one frame, with the rolling-shutter transition across it) and
  heard (a switch click 3.6 s later), and they give the same lag. The reference
  solution measures +3.60 s from them and dates the picture within 0.10 s.
- **It is a real-world failure mode.** DVRs and body-worn cameras that record
  sound through a separate input routinely mux it out of sync; examiners check
  sync before using one track to date the other.
- **The tolerance is not the issue.** The agents' errors on exhibit_10 are 3.3
  to 3.6 s, the A/V lag itself plus the usual half-second of dating error, not
  a near miss: every other time they reported was within 0.63 s.

## What it says about the agents

Both agents are excellent at the signal processing and at checking their
results against the reference: wherever the grid log could tell them they were
wrong, they were right. They found evidence in places nobody told them to
look (frame timing, another exhibit). What they did not do is question a
result that the log confirmed. A sound track that matches the grid log
perfectly is a correct date, but of the sound; whether it is also the date of
the picture is a separate question that no amount of signal processing
answers, and in six trials neither model asked it. In the audio version of the
task (GPT-6.1-sol 3/3) and the lamp-lit video version (both agents solved it),
every answer could be checked against the log; this version contains one answer
that cannot, and that is where both models failed, consistently.
