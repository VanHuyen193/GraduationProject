# -*- coding: utf-8 -*-
"""Trích đường cong reward / ELO từ các tệp TensorBoard của 15 lần huấn luyện.

Chạy bằng môi trường mlagents:
  C:\\Users\\Admin\\miniconda3\\envs\\mlagents\\python.exe extract_curves.py
"""
import json
import os
from pathlib import Path

from tensorboard.backend.event_processing.event_accumulator import EventAccumulator

RES = Path(r"C:\Users\Admin\Documents\GitHub\GraduationProject\GraduationProject\results")
OUT = Path(__file__).resolve().parent / "curves.json"

REWARD = "Environment/Cumulative Reward"
GROUP = "Environment/Group Cumulative Reward"
ELO = "Self-play/ELO"


def event_files(run_dir):
    return sorted(run_dir.rglob("events.out.tfevents.*"))


def load(run_dir):
    """Gộp mọi tệp event trong một thư mục chạy, khử trùng bước."""
    merged = {}
    for f in event_files(run_dir):
        try:
            ea = EventAccumulator(str(f), size_guidance={"scalars": 0})
            ea.Reload()
        except Exception as e:              # tệp hỏng hoặc đang ghi dở
            print(f"    bỏ qua {f.name}: {type(e).__name__}")
            continue
        for tag in ea.Tags().get("scalars", []):
            d = merged.setdefault(tag, {})
            for ev in ea.Scalars(tag):
                d[ev.step] = ev.value
    return {t: sorted(v.items()) for t, v in merged.items()}


def tail_mean(series, frac=0.10):
    if not series:
        return None
    n = max(1, int(len(series) * frac))
    vals = [v for _, v in series[-n:]]
    return sum(vals) / len(vals)


runs = {}
for d in sorted(RES.iterdir()):
    if not d.is_dir():
        continue
    print("»", d.name)
    sc = load(d)
    if not sc:
        print("    không có scalar")
        continue
    # Chương 4 báo cáo theo Environment/Cumulative Reward cho cả năm thuật toán;
    # tag nhóm chỉ dùng khi bản chạy không ghi tag thường.
    rew = sc.get(REWARD) or sc.get(GROUP) or []
    elo = sc.get(ELO) or []
    runs[d.name] = {
        "tags": sorted(sc.keys()),
        "reward": rew,
        "elo": elo,
        "group": not sc.get(REWARD) and bool(sc.get(GROUP)),
        "last_step": rew[-1][0] if rew else None,
        "tail_reward": tail_mean(rew),
        "tail_elo": tail_mean(elo) if elo else None,
        "final_elo": elo[-1][1] if elo else None,
    }
    print(f"    n={len(rew):5d}  bước cuối={runs[d.name]['last_step']}"
          f"  reward 10% cuối={runs[d.name]['tail_reward']}"
          f"  ELO cuối={runs[d.name]['final_elo']}"
          f"  {'(nhóm)' if runs[d.name]['group'] else ''}")

OUT.write_text(json.dumps(runs, ensure_ascii=False), encoding="utf-8")
print("\nĐã ghi", OUT, f"({OUT.stat().st_size/1024:.0f} KB)")
