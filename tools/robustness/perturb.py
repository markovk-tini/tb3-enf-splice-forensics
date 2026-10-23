"""Move each decision threshold of the reference solution down and up on its own,
re-run the analysis on the official data (cached flicker basebands), score."""
import json
import sys
from datetime import datetime
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

D = Path(sys.argv[1])
key = plan.answer_key()
log = E.GridLog(D / "grid" / "frequency_log.csv")
Z = {}
for name in sorted(key):
    cache = CACHE / f"{name}.{D.name}.npz"
    if not cache.exists():
        z, T, _ = E.flicker_baseband(D / "evidence" / name)
        np.savez(cache, z2=z[2], z4=z[4], T=T)
    d = np.load(cache)
    Z[name] = ({2: d["z2"], 4: d["z4"]}, float(d["T"]))


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
            dd = (datetime.fromisoformat(g["utc"].replace("Z", "+00:00")) - w["utc"]).total_seconds()
            if abs(dd) > 2.0:
                errs.append(f"s{i} utc {dd:+.1f}s")
    return "; ".join(errs)


def run():
    E._LOG_FFT.clear()
    bad = {}
    for name in sorted(key):
        z, T = Z[name]
        rep = E.analyze(E.Hum(dict(z), T), log)
        r = check(rep, key[name])
        if r:
            bad[name] = r
    return bad


VARIANTS = [("STEP_T", 25.0, 18.0, 35.0), ("FREE_STEP_T", 30.0, 20.0, 45.0), ("CUSUM_DROP", 12.0, 8.0, 18.0),
            ("ANCHOR_GAP", 0.05, 0.035, 0.07), ("LOCAL_GAP", 0.05, 0.035, 0.07), ("GROUP_CORR", 0.35, 0.25, 0.5)]
print("baseline:", run() or "all correct", flush=True)
for name, default, lo, hi in VARIANTS:
    row = []
    for v in (lo, hi):
        setattr(E, name, v)
        bad = run()
        row.append(f"{v:g} " + ("✅" if not bad else "❌ " + "; ".join(f"{k[8:10]}: {x}" for k, x in bad.items())))
    setattr(E, name, default)
    print(f"| `{name}` | {default:g} | {row[0]} | {row[1]} |", flush=True)

# exposure test: minimum depth change and how much of the sinc bound is required
orig = E.looks_like_exposure
for label, mn, frac in (("depth change > 0.10", 0.10, 0.8), ("depth change > 0.25", 0.25, 0.8),
                        ("sinc bound x0.6", 0.15, 0.6), ("sinc bound x1.0", 0.15, 1.0)):
    def lle(dth, rho, mn=mn, frac=frac):
        dE = -dth / (np.pi * 100.0)
        needed = abs(np.log(np.sinc(100.0 * abs(dE))))
        return abs(rho) > mn and np.sign(rho) == -np.sign(dE) and abs(rho) >= frac * needed
    E.looks_like_exposure = lle
    bad = run()
    print(f"| exposure test, {label} | | {'✅' if not bad else '❌ ' + str(bad)} |", flush=True)
E.looks_like_exposure = orig
