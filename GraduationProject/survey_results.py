#!/usr/bin/env python3
"""Khao sat moi run trong results/: doc trainer_type tu configuration.yaml + tfevents."""
import glob
import os
import warnings
from pathlib import Path

warnings.filterwarnings("ignore")
import numpy as np
from tensorboard.backend.event_processing.event_accumulator import EventAccumulator

ROOT = Path(__file__).resolve().parent / "results"
REWARD = "Environment/Cumulative Reward"

BEHAVIOR_ENV = {
    "CrossTheRoad": "CrossTheRoad",
    "PuzzleBehavior": "CaptureTheFlag",
    "Football": "Football",
}


def trainer_type(run_dir: Path):
    cfg = run_dir / "configuration.yaml"
    if not cfg.exists():
        return "?", "?"
    tt, ms = "?", "?"
    for line in cfg.read_text(encoding="utf-8", errors="ignore").splitlines():
        s = line.strip()
        if s.startswith("trainer_type:"):
            tt = s.split(":", 1)[1].strip()
        if s.startswith("max_steps:"):
            ms = s.split(":", 1)[1].strip()
    return tt, ms


def read_reward(run_dir: Path):
    events = glob.glob(str(run_dir / "**" / "*.tfevents.*"), recursive=True)
    merged = {}
    behaviors = set()
    for ev in events:
        behaviors.add(Path(ev).parent.name)
        try:
            ea = EventAccumulator(ev)
            ea.Reload()
            if REWARD in ea.Tags().get("scalars", []):
                for e in ea.Scalars(REWARD):
                    merged[int(e.step)] = float(e.value)
        except Exception:
            pass
    if not merged:
        return None, behaviors
    items = sorted(merged.items())
    vals = np.array([v for _, v in items])
    n = max(1, len(vals) // 10)
    return {
        "steps": items[-1][0],
        "npts": len(items),
        "final": round(float(vals[-1]), 3),
        "max": round(float(vals.max()), 3),
        "mean10": round(float(vals[-n:].mean()), 3),
    }, behaviors


rows = []
for run_dir in sorted(ROOT.iterdir()):
    if not run_dir.is_dir():
        continue
    tt, ms = trainer_type(run_dir)
    info, behaviors = read_reward(run_dir)
    beh = ",".join(sorted(b for b in behaviors if b in BEHAVIOR_ENV)) or ",".join(sorted(behaviors))
    env = next((BEHAVIOR_ENV[b] for b in behaviors if b in BEHAVIOR_ENV), "?")
    rows.append((env, tt, run_dir.name, ms, beh, info))

print(f"{'ENV':<16}{'TRAINER':<9}{'RUN':<26}{'MAXCFG':<12}{'STEPS':>10}{'PTS':>6}{'FINAL':>8}{'MAX':>8}{'MEAN10':>8}  BEH")
print("-" * 130)
for env, tt, run, ms, beh, info in sorted(rows, key=lambda r: (r[0], r[1], r[2])):
    if info:
        print(f"{env:<16}{tt:<9}{run:<26}{str(ms):<12}{info['steps']:>10}{info['npts']:>6}"
              f"{info['final']:>8}{info['max']:>8}{info['mean10']:>8}  {beh}")
    else:
        print(f"{env:<16}{tt:<9}{run:<26}{str(ms):<12}{'—':>10}{'—':>6}{'—':>8}{'—':>8}{'—':>8}  {beh} (no reward)")
