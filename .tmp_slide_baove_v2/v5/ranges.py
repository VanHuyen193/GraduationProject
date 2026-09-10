# -*- coding: utf-8 -*-
"""Kiểm tra biên giá trị để đặt trục cho các biểu đồ đường."""
import json
import os

ROOT = os.path.dirname(os.path.abspath(__file__))
C = json.load(open(os.path.join(ROOT, "curves.json"), encoding="utf-8"))
RUNS = {
    "Football Table": {"PPO": "FB01", "SAC": "Football_SAC_01",
                       "MA-POCA": "Football_POCA_01", "MAPPO": "Football_MAPPO_01",
                       "DQN": "football_dqn_v1"},
    "Capture The Flag": {"PPO": "ctf_ppo_v1", "SAC": "ctf_sac_v1",
                         "MA-POCA": "ctf_poca_v2", "MAPPO": "ctf_mappo_v2",
                         "DQN": "ctf_dqn_v1"},
    "Cross The Road": {"PPO": "ctr01", "SAC": "CrossTheRoad_SAC_01",
                       "MA-POCA": "ctr_poca_v1", "MAPPO": "ctr_mappo_v1",
                       "DQN": "ctr_dqn_v1"},
}


def smooth(pts, w):
    h = w // 2
    return [(s, sum(v for _, v in pts[max(0, i - h):i + h + 1])
             / len(pts[max(0, i - h):i + h + 1]))
            for i, (s, _) in enumerate(pts)]


for env, m in RUNS.items():
    print("==", env)
    for a, r in m.items():
        p = C[r]["reward"]
        raw = [v for _, v in p]
        s9 = [v for _, v in smooth(p, 9)]
        elo = [v for _, v in C[r]["elo"]]
        e = f"  ELO[{min(elo):.1f},{max(elo):.1f}]" if elo else ""
        print(f"  {a:8s} n={len(p):4d} thô[{min(raw):7.3f},{max(raw):7.3f}]"
              f"  mượt9[{min(s9):7.3f},{max(s9):7.3f}]{e}")
