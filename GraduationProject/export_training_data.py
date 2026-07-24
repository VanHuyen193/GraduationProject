#!/usr/bin/env python3
"""
export_training_data.py
=======================
Doc tfevents cua cac lan train (PPO / SAC / MA-POCA x 3 moi truong), rut gon
duong cong reward + thong ke, roi xuat ra 1 file JSON goi nhe cho menu Unity doc.

Chay trong conda env 'mlagents':
  C:\\Users\\Admin\\miniconda3\\envs\\mlagents\\python.exe export_training_data.py

Ket qua: Assets/GameHub/Resources/TrainingData/training_data.json
"""

import json
import warnings
from pathlib import Path
from datetime import datetime

warnings.filterwarnings("ignore")

import numpy as np
from tensorboard.backend.event_processing.event_accumulator import EventAccumulator

SCRIPT_DIR = Path(__file__).resolve().parent
RESULTS_DIR = SCRIPT_DIR / "results"
OUT_DIR = SCRIPT_DIR / "Assets" / "GameHub" / "Resources" / "TrainingData"
OUT_FILE = OUT_DIR / "training_data.json"

REWARD_KEY = "Environment/Cumulative Reward"
EPLEN_KEY = "Environment/Episode Length"

MAX_POINTS = 120  # so diem duong cong sau khi rut gon

# Thu tu moi truong khop enum GameEnvironment trong Unity.
# Moi thuat toan tro toi DUNG mot run hoan thien & tot nhat (chon sau khi khao sat
# results/ bang survey_results.py). MA-POCA = trainer_type 'poca' (khong phai 'mappo').
ENVIRONMENTS = [
    {
        "key": "CrossTheRoad",
        "name": "Cross The Road",
        "behavior": "CrossTheRoad",
        "algos": [
            {"algo": "PPO", "dirs": ["ctr01"]},                 # 2.0M steps
            {"algo": "SAC", "dirs": ["CrossTheRoad_SAC_01"]},   # hoi tu som (200K)
            {"algo": "MA-POCA", "dirs": ["ctr_poca_v1"]},       # 2.0M steps
        ],
    },
    {
        "key": "CaptureTheFlag",
        "name": "Capture The Flag",
        "behavior": "PuzzleBehavior",
        "algos": [
            {"algo": "PPO", "dirs": ["ctf_ppo_v3"]},            # run ngan nhat co du lieu
            {"algo": "SAC", "dirs": []},                        # chua train -> N/A
            {"algo": "MA-POCA", "dirs": ["ctf_poca_v2"]},       # 1.68M, max 0.88
        ],
    },
    {
        "key": "Football",
        "name": "Football Table",
        "behavior": "Football",
        "algos": [
            {"algo": "PPO", "dirs": ["FB01"]},                  # 1.59M self-play
            {"algo": "SAC", "dirs": ["Football_SAC_01"]},       # 0.92M, mean 1.94
            {"algo": "MA-POCA", "dirs": ["Football_POCA_01"]},  # 0.91M, mean 1.87
        ],
    },
]


def all_tfevents(run_dir: Path, behavior: str):
    """Tat ca file tfevents lien quan trong 1 thu muc run (ke ca behavior con)."""
    if not run_dir.exists():
        return []
    found = []
    for base in [run_dir / behavior, run_dir]:
        if base.exists():
            found += list(base.glob("*.tfevents.*"))
    if not found:  # quet sau
        found = list(run_dir.glob("**/*.tfevents.*"))
    # loc trung
    uniq = {p.resolve(): p for p in found}
    return list(uniq.values())


def read_series(tf_paths, key):
    """Doc + gop chuoi (step, value) cua 1 metric tu nhieu tfevents, sap xep theo step."""
    merged = {}
    for tf in tf_paths:
        try:
            ea = EventAccumulator(str(tf))
            ea.Reload()
            if key not in ea.Tags().get("scalars", []):
                continue
            for e in ea.Scalars(key):
                merged[int(e.step)] = float(e.value)
        except Exception as ex:
            print(f"    ! loi doc {tf.name}: {ex}")
    return sorted(merged.items())  # [(step, value), ...]


def smooth(values, window):
    if window <= 1 or len(values) < window:
        return values
    arr = np.array(values, dtype=float)
    kernel = np.ones(window) / window
    sm = np.convolve(arr, kernel, mode="valid")
    pad = np.full(len(values) - len(sm), sm[0])
    return list(np.concatenate([pad, sm]))


def downsample(steps, values, n):
    """Lay n diem cach deu (giu diem dau + cuoi)."""
    m = len(steps)
    if m <= n:
        return steps, values
    idx = np.linspace(0, m - 1, n).round().astype(int)
    idx = sorted(set(idx.tolist()))
    return [steps[i] for i in idx], [values[i] for i in idx]


def stats_of(series):
    if not series:
        return None
    vals = np.array([v for _, v in series], dtype=float)
    steps = [s for s, _ in series]
    n_last = max(1, len(vals) // 10)
    max_val = float(np.max(vals))
    thr = max_val * 0.9 if max_val > 0 else max_val * 1.1
    converge = next((s for s, v in series if v >= thr), steps[-1])
    return {
        "steps": int(steps[-1]),
        "final": float(vals[-1]),
        "max": max_val,
        "min": float(np.min(vals)),
        "meanLast10": float(np.mean(vals[-n_last:])),
        "convergeStep": int(converge),
    }


def build_algo(env, algo_cfg):
    behavior = env["behavior"]
    tf_paths = []
    used_dir = None
    for d in algo_cfg["dirs"]:
        paths = all_tfevents(RESULTS_DIR / d, behavior)
        if paths:
            tf_paths = paths
            used_dir = d
            break

    out = {
        "algo": algo_cfg["algo"],
        "found": False,
        "runId": used_dir or "",
        "steps": 0, "final": 0.0, "max": 0.0, "meanLast10": 0.0,
        "convergeStep": 0, "epLenFinal": 0.0,
        "cs": [], "cv": [],
    }

    if not tf_paths:
        print(f"    [{algo_cfg['algo']}] KHONG CO DU LIEU")
        return out

    reward = read_series(tf_paths, REWARD_KEY)
    if not reward:
        print(f"    [{algo_cfg['algo']}] co tfevents nhung thieu reward ({used_dir})")
        return out

    st = stats_of(reward)
    steps = [s for s, _ in reward]
    vals = [v for _, v in reward]
    vals_sm = smooth(vals, max(1, len(vals) // 60))
    cs, cv = downsample(steps, vals_sm, MAX_POINTS)

    eplen = read_series(tf_paths, EPLEN_KEY)
    ep_final = float(eplen[-1][1]) if eplen else 0.0

    out.update({
        "found": True,
        "steps": st["steps"], "final": round(st["final"], 4),
        "max": round(st["max"], 4), "meanLast10": round(st["meanLast10"], 4),
        "convergeStep": st["convergeStep"], "epLenFinal": round(ep_final, 2),
        "cs": [int(s) for s in cs],
        "cv": [round(float(v), 4) for v in cv],
    })
    print(f"    [{algo_cfg['algo']}] {used_dir}: {len(cs)} diem, "
          f"final={out['final']} max={out['max']} steps={out['steps']:,}")
    return out


def main():
    print("=" * 56)
    print("  XUAT DU LIEU TRAINING -> JSON cho menu Unity")
    print("=" * 56)

    environments = []
    for env in ENVIRONMENTS:
        print(f"\n[{env['name']}]")
        algos = [build_algo(env, a) for a in env["algos"]]
        environments.append({
            "key": env["key"],
            "name": env["name"],
            "algorithms": algos,
        })

    root = {
        "generated": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "environments": environments,
    }

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    with open(OUT_FILE, "w", encoding="utf-8") as f:
        json.dump(root, f, ensure_ascii=False, separators=(",", ":"))

    size_kb = OUT_FILE.stat().st_size / 1024
    print(f"\nDa ghi: {OUT_FILE}  ({size_kb:.1f} KB)")
    print("=" * 56)


if __name__ == "__main__":
    main()
