"""Identifiability audit (video): for every true stretch, how clearly does its
flicker-derived trace single out the true log time? global: best other time
anywhere in the log (same coverage); local: best other time within +-900 s, at
least 30 s away. Also the flicker phase step at every joint and every exposure
change, and the band depth change that comes with it."""
import pickle
import sys
from pathlib import Path

import numpy as np

import os
import tempfile
TASK = Path(__file__).resolve().parents[2] / "tasks" / "enf-splice-forensics"
CACHE = Path(os.environ.get("ENF_CACHE", Path(tempfile.gettempdir()) / "enf-cache"))
CACHE.mkdir(parents=True, exist_ok=True)
sys.path.insert(0, str(TASK / "tests"))
sys.path.insert(0, str(TASK / "solution"))
import case_plan as plan
import enf_forensics as E
import synthesize_evidence as se

D = Path(sys.argv[1])
if (D / "plan.json").exists():  # a draw written by seed_sweep.py: its seed and nudged plan
    import dataclasses
    import json
    from datetime import datetime
    se.SEED = int(D.name.split("_")[-1])
    saved = json.loads((D / "plan.json").read_text())
    for name, start in saved["sessions"].items():
        plan.SESSIONS[name] = dataclasses.replace(plan.SESSIONS[name], start=datetime.fromisoformat(start))
    plan.EXHIBITS.clear()
    plan.EXHIBITS.update({n: [plan.Piece(*p) for p in ps] for n, ps in saved["exhibits"].items()})
key = plan.answer_key()
log = E.GridLog(D / "grid" / "frequency_log.csv")


examined = {}
outage = []


def hum_for(name):
    """The channel the reference solution dates this video with (flicker,
    frame timing or sound), and the A/V lag that moves sound times to the
    picture."""
    cache = CACHE / f"{name}.{D.name}.examined.pkl"
    if cache.exists():
        r = pickle.loads(cache.read_bytes())
    else:
        r = E.examine(D / "evidence" / name, log)
        cache.write_bytes(pickle.dumps(r))
    examined[name] = r
    return r["hum"]


print("| Exhibit | Channel | Stretch | True time | r at true time | best other (log) | margin | best other (±15 min) | local margin |")
print("|---|---|---|---|---|---|---|---|---|")
hums = {}
for name in sorted(key):
    hum = hums[name] = hum_for(name)
    ch, shift = examined[name]["channel"], examined[name]["shift"]
    for i, seg in enumerate(key[name]):
        i0, i1 = np.searchsorted(hum.t, [seg["start"] + 8, seg["end"] - 8])
        if seg["utc"] is None:
            c = E.masked_ncc(hum.f[i0:i1], log.L, min_frac=0.9)
            j, c1, c2 = E.best_two(c)
            print(f"| {name} | {ch} | {i} ({seg['start']:.0f}-{seg['end']:.0f} s) | not in log | - | {c1:.3f} (any time) | "
                  f"{c1 - c2:+.3f} (best vs 2nd) | - | - |")
            continue
        s_true = (seg["utc"] - log.start).total_seconds() - shift  # when the channel's signal was recorded
        if not log.valid(np.array([s_true, s_true + (seg["end"] - seg["start"]) / 2])).any():
            outage.append((name, i, seg, hum))
            print(f"| {name} | {ch} | {i} ({seg['start']:.0f}-{seg['end']:.0f} s) | {seg['utc']:%d %H:%M:%S} | "
                  f"no log readings (logger outage): see the table below | | | | |")
            continue
        lag = int(round(s_true - seg["start"] + E.WIN / 2))
        c_at, c2 = E.uniqueness(hum.f, log.L, i0, i1, lag)
        a = max(0, lag + i0 - 900)
        c = E.masked_ncc(hum.f[i0:i1], log.L[a:lag + i1 + 900], min_frac=0.9)
        at = lag + i0 - a
        cc = c.copy()
        cc[max(0, at - 30):at + 31] = -1
        c2l = float(cc.max())
        print(f"| {name} | {ch} | {i} ({seg['start']:.0f}-{seg['end']:.0f} s) | {seg['utc']:%d %H:%M:%S} | {c_at:.3f} | {c2:.3f} | "
              f"{c_at - c2:+.3f} | {c2l:.3f} | {c_at - c2l:+.3f} |")

# stretches recorded while the logger was down: matched against the other
# videos' footage of the same minutes instead
if outage:
    print()
    print("| Exhibit | Stretch | True time | Other video | r at the true offset | best other offset | margin |")
    print("|---|---|---|---|---|---|---|")
for name, i, seg, hum in outage:
    i0, i1 = np.searchsorted(hum.t, [seg["start"] + 8, seg["end"] - 8])
    for other in sorted(key):
        if other == name:
            continue
        for k, oseg in enumerate(key[other]):
            if oseg["utc"] is None:
                continue
            # the other stretch's file time at which the true moment of seg's start falls
            ratio = 1 + plan.CAMERAS[plan.SESSIONS[plan.EXHIBITS[other][k].session].camera].clock_ppm * 1e-6
            t_other = oseg["start"] + (seg["utc"] - oseg["utc"]).total_seconds() * ratio
            if not (oseg["start"] <= t_other and t_other + (seg["end"] - seg["start"]) <= oseg["end"]):
                continue
            ho = hums[other]
            c = E.masked_ncc(hum.f[i0:i1], ho.f, min_frac=0.9)
            at = int(np.argmin(np.abs(ho.t - (t_other + 8))))
            c_at = float(c[max(0, at - 1):at + 2].max())
            cc = c.copy()
            cc[max(0, at - 20):at + 21] = -1
            print(f"| {name} | {i} ({seg['start']:.0f}-{seg['end']:.0f} s) | {seg['utc']:%d %H:%M:%S} | {other} | "
                  f"{c_at:.3f} | {cc.max():.3f} | {c_at - cc.max():+.3f} |")

# measured flicker steps at joints and exposure changes, from the footage itself
print()
print("| Exhibit | Event | File time (s) | Phase step, truth (rad) | Phase step, measured (rad) | Band depth ratio, measured |")
print("|---|---|---|---|---|---|")
f, phi, _ = se.grid()
wrap = lambda x: (x + np.pi) % (2 * np.pi) - np.pi


def theta(sess, m):
    cam = plan.CAMERAS[sess.camera]
    e = cam.exposure_s
    for t_sw, e_new in sess.exposures:
        if m / cam.fps >= t_sw:
            e = e_new
    t0 = (sess.start - se.GRID_T0).total_seconds()
    return 2 * se.phase_at(f, phi, np.array([t0 + (m / cam.fps - e / 2) / (1 + cam.clock_ppm * 1e-6)]))[0]


def measured(hum, t):
    y = E.free_residual(hum, 2)
    L, R = y[int((t - 5) * E.BB):int((t - 1) * E.BB)], y[int((t + 1) * E.BB):int((t + 5) * E.BB)]
    AL, AR = y[int((t - 16) * E.BB):int((t - 1) * E.BB)], y[int((t + 1) * E.BB):int((t + 16) * E.BB)]
    return np.angle(R.mean() * np.conj(L.mean())), np.abs(AR).mean() / np.abs(AL).mean()


for name in sorted(key):
    pieces = plan.EXHIBITS[name]
    hum = hums[name]
    pos = 0
    for i, p in enumerate(pieces):
        s = plan.SESSIONS[p.session]
        cam = plan.CAMERAS[s.camera]
        n0, n1 = plan.frame_index(cam, p.src_start), plan.frame_index(cam, p.src_end)
        for t_sw, e_new in s.exposures:
            m = plan.frame_index(cam, t_sw)
            if n0 < m < n1:
                ft = (pos + m - n0) / cam.fps
                tr = wrap(theta(s, m) - theta(s, m - 1) - 2 * np.pi * 100 / (cam.fps * (1 + cam.clock_ppm * 1e-6)))
                dm, rho = measured(hum, ft)
                print(f"| {name} | exposure change (not an edit) | {ft:.2f} | {tr:+.2f} | {dm:+.2f} | {rho:.2f} |")
        if i + 1 < len(pieces):
            q = pieces[i + 1]
            sq = plan.SESSIONS[q.session]
            a = n1
            b = plan.frame_index(plan.CAMERAS[sq.camera], q.src_start)
            ft = (pos + n1 - n0) / cam.fps
            tr = wrap(theta(sq, b) - theta(s, a))
            dm, rho = measured(hum, ft)
            print(f"| {name} | edit | {ft:.2f} | {tr:+.2f} | {dm:+.2f} | {rho:.2f} |")
        pos += n1 - n0

# phase coherence: at the true time the flicker phase follows the phase
# integrated from the log; at any other time it wanders. For every dated
# stretch, the coherence of a fitted phase model (offset + clock ratio) at the
# true time against the best of the five strongest other trace matches.
print()
print("| Exhibit | Stretch | Coherence at true time | Best coherence at another time (top-5 trace matches) |")
print("|---|---|---|---|")


def coherence_at(hum, lag, i0, i1):
    e = hum.f
    j = np.clip(lag + np.arange(i0, i1), 0, log.L.size - 1)
    r0 = 1.0 + np.nanmedian(e[i0:i1] - log.L[j]) / E.NOM
    if not np.isfinite(r0):
        return 0.0
    m = E.Model(hum, log, E.fine_lag(e, log.L, i0, i1, lag) - E.WIN / 2 * r0, r0)
    return m.fit(hum.t[i0], hum.t[i1 - 1])


in_outage = {(n, i) for n, i, _, _ in outage}
for name in sorted(key):
    hum = hums[name]
    for i, seg in enumerate(key[name]):
        if seg["utc"] is None or (name, i) in in_outage:  # no log to be coherent with
            continue
        i0, i1 = np.searchsorted(hum.t, [seg["start"] + 8, seg["end"] - 8])
        s_true = (seg["utc"] - log.start).total_seconds() - examined[name]["shift"]  # the signal's own time
        lag = int(round(s_true - seg["start"] + E.WIN / 2))
        c = E.masked_ncc(hum.f[i0:i1], log.L, min_frac=0.9)
        cc = c.copy()
        cc[max(0, lag + i0 - 60):lag + i0 + 61] = -1
        others = []
        for _ in range(5):
            k = int(np.argmax(cc))
            others.append(coherence_at(hum, k - i0, i0, i1))
            cc[max(0, k - 60):k + 61] = -1
        print(f"| {name} | {i} ({seg['start']:.0f}-{seg['end']:.0f} s) | {coherence_at(hum, lag, i0, i1):.3f} | {max(others):.3f} |")
