"""Robustness sweep for the video task: regenerate the case with other seeds, solve, score.

For each seed: simulate the grid and the sessions with that seed, nudge every
joint the way the official seed was nudged (move the next piece by up to two
frames, or for the 25 fps camera shift the next session's start by up to 9 ms)
so the flicker phase steps by >= 1.2 rad, render the exhibits, run the
unchanged reference solution, and score it with the verifier's rules.
"""
import copy
import dataclasses
import json
import sys
import time
from datetime import datetime, timedelta
from multiprocessing import get_context
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
import synthesize_evidence as se
import enf_forensics as ef

wrap = lambda x: (x + np.pi) % (2 * np.pi) - np.pi
OUT = Path(os.environ.get("SWEEP_OUT", "sweep-out")).resolve()

# the official plan before its joints were nudged
NOMINAL_PIECES = {
    "exhibit_01.mp4": [("S3", 0.0, 251.4), ("S4", 47.3, 236.9), ("S3", 251.4, 409.7), ("S3", 419.0, 560.0)],
    "exhibit_02.mp4": [("S6", 0.0, 480.0)],
    "exhibit_03.mp4": [("S1", 0.0, 540.0)],
    "exhibit_04.mp4": [("S8", 0.0, 265.2), ("S11", 21.6, 104.9), ("S9", 57.4, 330.0)],
    "exhibit_05.mp4": [("S2", 0.0, 288.3), ("S2", 320.0, 453.6), ("S2", 458.733, 600.0)],
    "exhibit_06.mp4": [("S10", 207.1, 401.6), ("S10", 0.0, 207.1), ("S10", 401.6, 600.0)],
    "exhibit_07.mp4": [("S5", 0.0, 401.2), ("S5", 406.8, 560.0)],
    "exhibit_08.mp4": [("S7", 0.0, 546.5), ("S7", 563.9, 720.0)],
}
NOMINAL_STARTS = {"S11": plan._t(9, 18, 40, 3.6), "S9": plan._t(6, 19, 57, 30.8)}


def theta(f, phi, sess, m):
    cam = plan.CAMERAS[sess.camera]
    e = cam.exposure_s
    for t_sw, e_new in sess.exposures:
        if m / cam.fps >= t_sw:
            e = e_new
    t0 = (sess.start - se.GRID_T0).total_seconds()
    t = t0 + (m / cam.fps - e / 2) / (1 + cam.clock_ppm * 1e-6)
    return 2 * se.phase_at(f, phi, np.array([t]))[0]  # lamp phase is the same on both sides


def nudge(f, phi):
    sessions = dict(plan.SESSIONS)
    for name, start in NOMINAL_STARTS.items():
        sessions[name] = dataclasses.replace(sessions[name], start=start)
    exhibits = {}
    for name, raw in NOMINAL_PIECES.items():
        pieces = [plan.Piece(*p) for p in raw]
        for i in range(len(pieces) - 1):
            A, B = pieces[i], pieces[i + 1]
            sa, sb = sessions[A.session], sessions[B.session]
            cam = plan.CAMERAS[sb.camera]
            a = plan.frame_index(plan.CAMERAS[sa.camera], A.src_end)
            b = plan.frame_index(cam, B.src_start)
            if cam.fps == 25.0:  # frame shifts do not move the step: shift the session start
                for ms in range(0, 10):
                    s2 = dataclasses.replace(sb, start=sb.start + timedelta(milliseconds=ms))
                    if abs(wrap(theta(f, phi, s2, b) - theta(f, phi, sa, a))) >= 1.2:
                        sessions[B.session] = sb = s2
                        break
            else:
                for d in (0, 1, -1, 2, -2):
                    if b + d < 0:
                        continue
                    if abs(wrap(theta(f, phi, sb, b + d) - theta(f, phi, sa, a))) >= 1.2:
                        pieces[i + 1] = plan.Piece(B.session, (b + d) / cam.fps, B.src_end)
                        break
        exhibits[name] = pieces
    return sessions, exhibits


def check(got, want):
    if len(got) != len(want):
        return f"{len(got)} vs {len(want)} stretches"
    errs = []
    for i, (g, w) in enumerate(zip(got, want)):
        if i and abs(g["start"] - w["start"]) > 1.0:
            errs.append(f"b{i} {g['start'] - w['start']:+.1f}s")
        if (g["utc"] is None) != (w["utc"] is None):
            errs.append(f"s{i} null mismatch")
        elif g["utc"] is not None:
            d = (datetime.fromisoformat(g["utc"].replace("Z", "+00:00")) - w["utc"]).total_seconds()
            if abs(d) > 2.0:
                errs.append(f"s{i} utc {d:+.1f}s")
    return "; ".join(errs)


def solve_one(args):
    path, log_path = args
    log = ef.GridLog(log_path)
    z, T, _ = ef.flicker_baseband(path)
    return path.name, ef.analyze(ef.Hum(z, T), log)


def run(seed, workers=8):
    t0 = time.time()
    out = OUT / f"seed_{seed}"
    se.SEED = seed
    f, phi, log_rng = se.grid()
    se.write_log(f, log_rng, out / "grid" / "frequency_log.csv")
    sessions, exhibits = nudge(f, phi)
    saved = (copy.copy(plan.SESSIONS), copy.copy(plan.EXHIBITS))
    plan.SESSIONS.clear(); plan.SESSIONS.update(sessions)
    plan.EXHIBITS.clear(); plan.EXHIBITS.update(exhibits)
    try:
        se._STATE["renderers"] = se.build_renderers(f, phi)
        ev = out / "evidence"
        ev.mkdir(parents=True, exist_ok=True)
        with get_context("fork").Pool(workers) as pool:
            list(pool.imap_unordered(se._render_exhibit, [(n, ev) for n in sorted(plan.EXHIBITS)]))
        key = plan.answer_key()
        (out / "plan.json").write_text(json.dumps({
            "sessions": {n: s.start.isoformat() for n, s in plan.SESSIONS.items()},
            "exhibits": {n: [[p.session, p.src_start, p.src_end] for p in ps] for n, ps in plan.EXHIBITS.items()}}))
        with get_context("fork").Pool(workers) as pool:
            reports = dict(pool.imap_unordered(solve_one, [(ev / n, out / "grid" / "frequency_log.csv") for n in sorted(key)]))
        (out / "report.json").write_text(json.dumps(reports, indent=1, default=float))
        results = {n: check(reports[n], key[n]) for n in sorted(key)}
    finally:
        plan.SESSIONS.clear(); plan.SESSIONS.update(saved[0])
        plan.EXHIBITS.clear(); plan.EXHIBITS.update(saved[1])
    ok = sum(1 for v in results.values() if not v)
    print(f"seed {seed}: {ok}/8 exhibits correct ({time.time() - t0:.0f}s)", flush=True)
    for name, v in results.items():
        if v:
            print(f"   {name}: {v}", flush=True)
    return ok


if __name__ == "__main__":
    seeds = [int(s) for s in sys.argv[1:]] or [1, 2, 3, 4, 5, 6]
    total = sum(run(s) for s in seeds)
    print(f"TOTAL {total}/{8 * len(seeds)}")
