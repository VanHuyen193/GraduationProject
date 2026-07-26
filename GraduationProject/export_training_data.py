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
        "key": "Football",
        "name": "Football Table",
        "behavior": "Football",
        "algos": [
            {"algo": "PPO", "dirs": ["FB01"]},                  # 1.59M self-play
            {"algo": "SAC", "dirs": ["Football_SAC_01"]},       # 0.92M
            {"algo": "MA-POCA", "dirs": ["Football_POCA_01"]},  # 0.91M
        ],
    },
    {
        "key": "CrossTheRoad",
        "name": "Cross The Road",
        "behavior": "CrossTheRoad",
        "algos": [
            {"algo": "PPO", "dirs": ["ctr01"]},                 # 2.0M steps
            {"algo": "SAC", "dirs": ["CrossTheRoad_SAC_01"]},   # hoi tu som (200K)
            {"algo": "MA-POCA", "dirs": ["ctr_poca_v1"]},       # 2.0M steps
            {"algo": "MAPPO", "dirs": ["ctr_mappo_v1"]},        # 2.0M steps
        ],
    },
    {
        "key": "CaptureTheFlag",
        "name": "Capture The Flag",
        "behavior": "PuzzleBehavior",
        "algos": [
            {"algo": "MA-POCA", "dirs": ["ctf_poca_v2"]},       # 1.68M
            {"algo": "MAPPO", "dirs": ["ctf_mappo_v2"]},        # 1.52M
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
    """Trung binh truot lui, cua so ngan dan o dau chuoi (min_periods=1).

    Khong dung np.convolve(mode='valid') roi chen dau bang gia tri dau tien:
    cach do lam phang mat toan bo giai doan hoc ban dau cua duong cong.
    """
    if window <= 1 or len(values) < 2:
        return list(values)
    arr = np.asarray(values, dtype=float)
    cum = np.cumsum(np.insert(arr, 0, 0.0))
    idx = np.arange(len(arr))
    start = np.maximum(0, idx - window + 1)
    sums = cum[idx + 1] - cum[start]
    counts = (idx - start + 1).astype(float)
    return list(sums / counts)


def downsample(steps, values, n):
    """Lay n diem cach deu (giu diem dau + cuoi)."""
    m = len(steps)
    if m <= n:
        return steps, values
    idx = np.linspace(0, m - 1, n).round().astype(int)
    idx = sorted(set(idx.tolist()))
    return [steps[i] for i in idx], [values[i] for i in idx]


def converge_step(steps, vals_sm):
    """Buoc ma tu do duong cong (da lam muot) khong con tut xuong duoi 90% muc
    on dinh cuoi cung. On dinh hon nhieu so voi 'lan dau cham 90% max' vi
    khong bi mot dinh nhieu don le keo ve dau chuoi."""
    if not steps:
        return 0
    n_last = max(1, len(vals_sm) // 10)
    plateau = float(np.mean(vals_sm[-n_last:]))
    lo = plateau * 0.9 if plateau > 0 else plateau * 1.1
    idx = 0
    for i in range(len(vals_sm) - 1, -1, -1):
        if vals_sm[i] < lo:
            idx = min(i + 1, len(vals_sm) - 1)
            break
    return int(steps[idx])


def stats_of(series, vals_sm):
    """Thong ke tinh tren duong cong DA LAM MUOT - dung chuoi ma bieu do ve,
    de bang so lieu va do thi luon khop nhau."""
    if not series:
        return None
    steps = [s for s, _ in series]
    vals = np.array(vals_sm, dtype=float)
    n_last = max(1, len(vals) // 10)
    return {
        "steps": int(steps[-1]),
        "final": float(vals[-1]),
        "max": float(np.max(vals)),
        "min": float(np.min(vals)),
        "meanLast10": float(np.mean(vals[-n_last:])),
        "convergeStep": converge_step(steps, vals_sm),
        "actualCount": len(series),
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
        "steps": 0, "maxEnvSteps": 0, "actualCount": 0,
        "final": 0.0, "max": 0.0, "meanLast10": 0.0,
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

    steps = [s for s, _ in reward]
    vals = [v for _, v in reward]
    vals_sm = smooth(vals, max(3, len(vals) // 12))
    st = stats_of(reward, vals_sm)
    cs, cv = downsample(steps, vals_sm, MAX_POINTS)

    eplen = read_series(tf_paths, EPLEN_KEY)
    ep_final = (float(np.mean([v for _, v in eplen[-max(1, len(eplen) // 10):]]))
                if eplen else 0.0)

    out.update({
        "found": True,
        "steps": st["steps"], "actualCount": st["actualCount"],
        "final": round(st["final"], 4),
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

        # Truc hoanh dung chung cho ca moi truong = run dai nhat; cac run ngan hon
        # ket thuc som tren bieu do thay vi bi keo dan ra cho bang.
        env_steps = max([a["steps"] for a in algos] + [0])
        for a in algos:
            a["maxEnvSteps"] = env_steps

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
