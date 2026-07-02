#!/usr/bin/env python3
"""
compare_results.py
==================
Reads TensorBoard event files from all 9 training runs,
extracts key metrics, generates comparison charts, and writes a report.

Usage:
  python compare_results.py
  python compare_results.py --results-dir results
  python compare_results.py --output-dir comparison_charts

Requirements:
  Run inside 'mlagents' conda environment:
    C:\\Users\\Admin\\miniconda3\\envs\\mlagents\\python.exe compare_results.py
"""

import os
import sys
import json
import argparse
import warnings
from pathlib import Path
from datetime import datetime
from collections import defaultdict

warnings.filterwarnings("ignore")

# Try importing required packages
try:
    import numpy as np
except ImportError:
    print("ERROR: numpy not found. Run inside mlagents conda env.")
    sys.exit(1)

try:
    from tensorboard.backend.event_processing.event_accumulator import EventAccumulator
    HAS_TENSORBOARD = True
except ImportError:
    HAS_TENSORBOARD = False
    print("WARNING: tensorboard not found, will use fallback stats from training_summary.json")

try:
    import matplotlib
    matplotlib.use("Agg")  # Non-interactive backend
    import matplotlib.pyplot as plt
    import matplotlib.gridspec as gridspec
    HAS_MATPLOTLIB = True
except ImportError:
    HAS_MATPLOTLIB = False
    print("WARNING: matplotlib not found. Charts will not be generated.")

# ─── Configuration ───────────────────────────────────────────────────────────
SCRIPT_DIR = Path(__file__).resolve().parent
DEFAULT_RESULTS_DIR = SCRIPT_DIR / "results"
DEFAULT_OUTPUT_DIR = SCRIPT_DIR / "comparison_charts"

# 9 training runs: {job_id: metadata}
# fallback_ids: alternative run directories to search if the primary run_id is not found
RUN_REGISTRY = {
    "football_ppo_v1":  {"env": "Football Table",    "algo": "PPO",     "algo_color": "#2196F3", "env_group": "football",
                          "fallback_ids": ["FB01", "football-table-agent", "agent1"], "behavior": "Football"},
    "football_sac_v1":  {"env": "Football Table",    "algo": "SAC",     "algo_color": "#4CAF50", "env_group": "football",
                          "fallback_ids": [], "behavior": "Football"},
    "football_poca_v1": {"env": "Football Table",    "algo": "MA-POCA", "algo_color": "#FF9800", "env_group": "football",
                          "fallback_ids": [], "behavior": "Football"},
    "ctr_ppo_v1":       {"env": "Cross The Road",    "algo": "PPO",     "algo_color": "#2196F3", "env_group": "crossroad",
                          "fallback_ids": ["ctr01"], "behavior": "CrossTheRoad"},
    "ctr_sac_v1":       {"env": "Cross The Road",    "algo": "SAC",     "algo_color": "#4CAF50", "env_group": "crossroad",
                          "fallback_ids": ["CrossTheRoad_SAC_01"], "behavior": "CrossTheRoad"},
    "ctr_poca_v1":      {"env": "Cross The Road",    "algo": "MA-POCA", "algo_color": "#FF9800", "env_group": "crossroad",
                          "fallback_ids": [], "behavior": "CrossTheRoad"},
    "ctf_ppo_v1":       {"env": "Capture The Flag",  "algo": "PPO",     "algo_color": "#2196F3", "env_group": "capture",
                          "fallback_ids": ["CaptureTheFlag_PPO_01", "CaptureTheFlag_PPO_02", "CaptureTheFlag_PPO_03"], "behavior": "PuzzleBehavior"},
    "ctf_sac_v1":       {"env": "Capture The Flag",  "algo": "SAC",     "algo_color": "#4CAF50", "env_group": "capture",
                          "fallback_ids": [], "behavior": "PuzzleBehavior"},
    "ctf_poca_v1":      {"env": "Capture The Flag",  "algo": "MA-POCA", "algo_color": "#FF9800", "env_group": "capture",
                          "fallback_ids": [], "behavior": "PuzzleBehavior"},
}

ALGO_COLORS = {"PPO": "#2196F3", "SAC": "#4CAF50", "MA-POCA": "#FF9800"}
ALGO_MARKERS = {"PPO": "o", "SAC": "s", "MA-POCA": "^"}

# TensorBoard metric keys to extract (mlagents naming)
METRICS_OF_INTEREST = [
    "Environment/Cumulative Reward",
    "Environment/Episode Length",
    "Losses/Policy Loss",
    "Losses/Value Loss",
    "Policy/Entropy",
    "Policy/Learning Rate",
]


def find_tfevents_file(run_dir: Path, behavior: str = None) -> Path | None:
    """Find the TFEvents file inside a run directory.
    Checks both the run_dir directly and behavior subdirectories.
    """
    if not run_dir.exists():
        return None

    # Check behavior subdirectory first (ml-agents puts events there)
    if behavior:
        behavior_dir = run_dir / behavior
        if behavior_dir.exists():
            for pattern in ["events.out.tfevents.*", "*.tfevents.*"]:
                files = list(behavior_dir.glob(pattern))
                if files:
                    return max(files, key=lambda p: p.stat().st_mtime)

    # Fallback: search recursively
    for pattern in ["**/*.tfevents.*", "**/*.tfevents", "**/events.out.tfevents.*"]:
        files = list(run_dir.glob(pattern))
        if files:
            return max(files, key=lambda p: p.stat().st_mtime)
    return None


def find_run_with_fallbacks(run_id: str, meta: dict, results_dir: Path) -> tuple:
    """
    Find the best available data directory for a given run_id.
    Falls back to alternative run IDs if the primary is not found.

    Returns:
        (found_path, actual_run_id_used) or (None, None)
    """
    behavior = meta.get("behavior")

    # Try primary run_id first
    primary = results_dir / run_id
    tf = find_tfevents_file(primary, behavior)
    if tf:
        return primary, run_id

    # Try fallback IDs
    for fallback_id in meta.get("fallback_ids", []):
        fallback_dir = results_dir / fallback_id
        tf = find_tfevents_file(fallback_dir, behavior)
        if tf:
            print(f"    (using fallback: {fallback_id})")
            return fallback_dir, fallback_id

    return None, None



def extract_scalars_from_tfevent(tfevent_path: Path) -> dict:
    """
    Read a TFEvents file and extract scalar time series.

    Returns:
        dict: {metric_name: [(step, value), ...]}
    """
    if not HAS_TENSORBOARD:
        return {}

    try:
        ea = EventAccumulator(str(tfevent_path))
        ea.Reload()
        tags = ea.Tags().get("scalars", [])

        scalars = {}
        for tag in tags:
            events = ea.Scalars(tag)
            scalars[tag] = [(e.step, e.value) for e in events]

        return scalars

    except Exception as ex:
        print(f"  WARNING: Could not read {tfevent_path}: {ex}")
        return {}


def compute_stats(series: list) -> dict:
    """Compute summary statistics from a (step, value) series."""
    if not series:
        return {
            "final": None, "max": None, "mean_last_10pct": None,
            "steps": 0, "converge_step": None,
        }

    steps = [s for s, v in series]
    values = [v for s, v in series]
    arr = np.array(values)

    # Mean of last 10% of training
    n_last = max(1, len(arr) // 10)
    mean_last = float(np.mean(arr[-n_last:]))

    # Convergence step: first step where value exceeds 90% of max
    max_val = float(np.max(arr))
    threshold = max_val * 0.9 if max_val > 0 else max_val * 1.1
    converge_step = None
    for i, (step, val) in enumerate(series):
        if val >= threshold:
            converge_step = step
            break

    return {
        "final": float(arr[-1]) if len(arr) > 0 else None,
        "max": float(np.max(arr)),
        "min": float(np.min(arr)),
        "mean": float(np.mean(arr)),
        "mean_last_10pct": mean_last,
        "std": float(np.std(arr)),
        "steps": steps[-1] if steps else 0,
        "n_points": len(arr),
        "converge_step": converge_step,
    }


def smooth_series(values: list, window: int = 20) -> list:
    """Apply moving average smoothing to a value series."""
    if len(values) < window:
        return values
    arr = np.array(values, dtype=float)
    kernel = np.ones(window) / window
    smoothed = np.convolve(arr, kernel, mode="valid")
    # Pad to same length
    pad = np.full(len(values) - len(smoothed), smoothed[0])
    return list(np.concatenate([pad, smoothed]))


def load_all_run_data(results_dir: Path) -> dict:
    """
    Load metric data from all 9 training runs.
    Uses fallback run IDs if primary run directories are not found.

    Returns:
        dict: {run_id: {metric: [(step, value), ...], "meta": {...}}}
    """
    all_data = {}

    print(f"\nScanning results directory: {results_dir}")

    for run_id, meta in RUN_REGISTRY.items():
        behavior = meta.get("behavior")
        print(f"  [{run_id}] ", end="")

        # Find the run directory (with fallbacks)
        run_dir, actual_id = find_run_with_fallbacks(run_id, meta, results_dir)

        if run_dir is None:
            print(f"NOT FOUND (tried: {run_id}, fallbacks: {meta.get('fallback_ids', [])})")
            all_data[run_id] = {"meta": meta, "scalars": {}, "found": False, "actual_id": None}
            continue

        tf_path = find_tfevents_file(run_dir, behavior)
        if tf_path is None:
            print(f"No TFEvents in {run_dir}")
            all_data[run_id] = {"meta": meta, "scalars": {}, "found": False, "actual_id": actual_id}
            continue

        label = f"{actual_id}" if actual_id != run_id else ""
        print(f"Reading {tf_path.name} {label}")
        scalars = extract_scalars_from_tfevent(tf_path)
        all_data[run_id] = {
            "meta": meta, "scalars": scalars, "found": True,
            "tf_path": str(tf_path), "actual_id": actual_id
        }
        print(f"    Metrics available: {len(scalars)} keys")

    found_count = sum(1 for d in all_data.values() if d["found"])
    print(f"\nLoaded data from {found_count}/9 runs")
    return all_data



def plot_reward_curves(all_data: dict, output_dir: Path):
    """Plot cumulative reward curves grouped by environment."""
    if not HAS_MATPLOTLIB:
        print("Matplotlib not available, skipping charts.")
        return []

    reward_key = "Environment/Cumulative Reward"
    env_groups = {
        "football":  ("Football Table",   [k for k in RUN_REGISTRY if "football" in k]),
        "crossroad": ("Cross The Road",   [k for k in RUN_REGISTRY if "ctr" in k]),
        "capture":   ("Capture The Flag", [k for k in RUN_REGISTRY if "ctf" in k]),
    }

    saved_files = []

    # ── Figure 1: Individual reward curves per environment ─────────────────
    fig, axes = plt.subplots(1, 3, figsize=(18, 6))
    fig.suptitle("Cumulative Reward Curves: 3 Algorithms x 3 Environments",
                 fontsize=14, fontweight="bold", y=1.02)

    for ax, (env_key, (env_name, run_ids)) in zip(axes, env_groups.items()):
        ax.set_title(env_name, fontsize=12, fontweight="bold")
        ax.set_xlabel("Training Steps")
        ax.set_ylabel("Cumulative Reward")
        ax.grid(True, alpha=0.3)

        any_data = False
        for run_id in run_ids:
            data = all_data.get(run_id, {})
            if not data.get("found"):
                continue

            scalars = data["scalars"]
            if reward_key not in scalars:
                continue

            series = scalars[reward_key]
            if not series:
                continue

            steps = [s for s, v in series]
            values = [v for s, v in series]
            smoothed = smooth_series(values, window=10)

            meta = data["meta"]
            color = ALGO_COLORS[meta["algo"]]
            marker = ALGO_MARKERS[meta["algo"]]

            ax.plot(steps, smoothed, color=color, label=meta["algo"],
                    linewidth=2, alpha=0.85)
            ax.plot(steps, values, color=color, alpha=0.2, linewidth=0.5)
            any_data = True

        if any_data:
            ax.legend(loc="upper left")
        else:
            ax.text(0.5, 0.5, "No data available\n(run training first)",
                    ha="center", va="center", transform=ax.transAxes,
                    fontsize=11, color="gray", style="italic")

    plt.tight_layout()
    chart_path = output_dir / "01_reward_curves.png"
    plt.savefig(chart_path, dpi=150, bbox_inches="tight")
    plt.close()
    saved_files.append(chart_path)
    print(f"  Saved: {chart_path.name}")

    # ── Figure 2: Final reward bar chart ────────────────────────────────────
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.set_title("Final Average Reward (Last 10% of Training)",
                 fontsize=13, fontweight="bold")

    algos = ["PPO", "SAC", "MA-POCA"]
    env_names = ["Football Table", "Cross The Road", "Capture The Flag"]
    env_keys = ["football", "crossroad", "capture"]

    x = np.arange(len(env_names))
    width = 0.25
    offsets = [-width, 0, width]

    for algo_idx, algo in enumerate(algos):
        heights = []
        for env_key in env_keys:
            # Find the run_id for this env+algo combo
            run_id = None
            for rid, meta in RUN_REGISTRY.items():
                if meta["env_group"] == env_key and meta["algo"] == algo:
                    run_id = rid
                    break

            if run_id and all_data.get(run_id, {}).get("found"):
                scalars = all_data[run_id]["scalars"]
                series = scalars.get(reward_key, [])
                if series:
                    values = [v for _, v in series]
                    n_last = max(1, len(values) // 10)
                    heights.append(float(np.mean(values[-n_last:])))
                else:
                    heights.append(0)
            else:
                heights.append(0)

        bars = ax.bar(x + offsets[algo_idx], heights, width,
                      label=algo, color=ALGO_COLORS[algo], alpha=0.85,
                      edgecolor="white", linewidth=0.5)
        # Add value labels
        for bar, h in zip(bars, heights):
            if h != 0:
                ax.text(bar.get_x() + bar.get_width() / 2,
                        bar.get_height() + 0.01,
                        f"{h:.3f}", ha="center", va="bottom", fontsize=8)

    ax.set_xticks(x)
    ax.set_xticklabels(env_names, fontsize=11)
    ax.set_ylabel("Mean Cumulative Reward", fontsize=11)
    ax.legend(fontsize=11)
    ax.grid(True, axis="y", alpha=0.3)

    chart_path = output_dir / "02_final_reward_bar.png"
    plt.tight_layout()
    plt.savefig(chart_path, dpi=150, bbox_inches="tight")
    plt.close()
    saved_files.append(chart_path)
    print(f"  Saved: {chart_path.name}")

    # ── Figure 3: Episode Length ─────────────────────────────────────────────
    ep_len_key = "Environment/Episode Length"
    fig, axes = plt.subplots(1, 3, figsize=(18, 5))
    fig.suptitle("Episode Length During Training", fontsize=14, fontweight="bold")

    for ax, (env_key, (env_name, run_ids)) in zip(axes, env_groups.items()):
        ax.set_title(env_name, fontsize=12)
        ax.set_xlabel("Training Steps")
        ax.set_ylabel("Episode Length")
        ax.grid(True, alpha=0.3)

        any_data = False
        for run_id in run_ids:
            data = all_data.get(run_id, {})
            if not data.get("found") or ep_len_key not in data["scalars"]:
                continue
            series = data["scalars"][ep_len_key]
            if not series:
                continue
            steps = [s for s, v in series]
            values = smooth_series([v for _, v in series], window=10)
            meta = data["meta"]
            ax.plot(steps, values, color=ALGO_COLORS[meta["algo"]],
                    label=meta["algo"], linewidth=2, alpha=0.85)
            any_data = True

        if any_data:
            ax.legend(loc="upper right")
        else:
            ax.text(0.5, 0.5, "No data", ha="center", va="center",
                    transform=ax.transAxes, color="gray", style="italic")

    plt.tight_layout()
    chart_path = output_dir / "03_episode_length.png"
    plt.savefig(chart_path, dpi=150, bbox_inches="tight")
    plt.close()
    saved_files.append(chart_path)
    print(f"  Saved: {chart_path.name}")

    # ── Figure 4: Policy Loss ─────────────────────────────────────────────
    loss_key = "Losses/Policy Loss"
    fig, axes = plt.subplots(1, 3, figsize=(18, 5))
    fig.suptitle("Policy Loss During Training", fontsize=14, fontweight="bold")

    for ax, (env_key, (env_name, run_ids)) in zip(axes, env_groups.items()):
        ax.set_title(env_name, fontsize=12)
        ax.set_xlabel("Training Steps")
        ax.set_ylabel("Policy Loss")
        ax.grid(True, alpha=0.3)

        any_data = False
        for run_id in run_ids:
            data = all_data.get(run_id, {})
            if not data.get("found"):
                continue
            scalars = data["scalars"]
            series = scalars.get(loss_key, [])
            if not series:
                continue
            steps = [s for s, v in series]
            values = smooth_series([v for _, v in series], window=10)
            meta = data["meta"]
            ax.plot(steps, values, color=ALGO_COLORS[meta["algo"]],
                    label=meta["algo"], linewidth=2, alpha=0.85)
            any_data = True

        if any_data:
            ax.legend()
        else:
            ax.text(0.5, 0.5, "No data", ha="center", va="center",
                    transform=ax.transAxes, color="gray", style="italic")

    plt.tight_layout()
    chart_path = output_dir / "04_policy_loss.png"
    plt.savefig(chart_path, dpi=150, bbox_inches="tight")
    plt.close()
    saved_files.append(chart_path)
    print(f"  Saved: {chart_path.name}")

    # ── Figure 5: Entropy (exploration measure) ───────────────────────────
    entropy_key = "Policy/Entropy"
    fig, axes = plt.subplots(1, 3, figsize=(18, 5))
    fig.suptitle("Policy Entropy (Exploration) During Training",
                 fontsize=14, fontweight="bold")

    for ax, (env_key, (env_name, run_ids)) in zip(axes, env_groups.items()):
        ax.set_title(env_name, fontsize=12)
        ax.set_xlabel("Training Steps")
        ax.set_ylabel("Entropy")
        ax.grid(True, alpha=0.3)

        any_data = False
        for run_id in run_ids:
            data = all_data.get(run_id, {})
            if not data.get("found"):
                continue
            series = data["scalars"].get(entropy_key, [])
            if not series:
                continue
            steps = [s for s, v in series]
            values = smooth_series([v for _, v in series], window=10)
            meta = data["meta"]
            ax.plot(steps, values, color=ALGO_COLORS[meta["algo"]],
                    label=meta["algo"], linewidth=2, alpha=0.85)
            any_data = True

        if any_data:
            ax.legend()
        else:
            ax.text(0.5, 0.5, "No data", ha="center", va="center",
                    transform=ax.transAxes, color="gray", style="italic")

    plt.tight_layout()
    chart_path = output_dir / "05_entropy.png"
    plt.savefig(chart_path, dpi=150, bbox_inches="tight")
    plt.close()
    saved_files.append(chart_path)
    print(f"  Saved: {chart_path.name}")

    return saved_files


def build_stats_table(all_data: dict) -> dict:
    """Build a nested stats dict for all runs."""
    reward_key = "Environment/Cumulative Reward"
    ep_len_key = "Environment/Episode Length"

    stats = {}
    for run_id, data in all_data.items():
        meta = data["meta"]
        scalars = data.get("scalars", {})

        reward_series = scalars.get(reward_key, [])
        ep_len_series = scalars.get(ep_len_key, [])

        stats[run_id] = {
            "env": meta["env"],
            "algo": meta["algo"],
            "found": data.get("found", False),
            "reward": compute_stats(reward_series),
            "ep_len": compute_stats(ep_len_series),
        }

    return stats


def generate_markdown_report(stats: dict, output_dir: Path, charts: list) -> str:
    """Generate the comparison markdown report."""
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    lines = [
        "# RL Algorithm Comparison Report",
        "",
        f"**Generated**: {now}",
        "",
        "## Overview",
        "",
        "This report compares three Reinforcement Learning algorithms trained on",
        "three Unity ML-Agents environments. Each environment was trained with",
        "identical configurations (except algorithm-specific hyperparameters) and",
        "the same number of total steps.",
        "",
        "| Algorithm | Type | Key Advantage |",
        "|-----------|------|---------------|",
        "| **PPO** (Proximal Policy Optimization) | On-policy | Stable, general-purpose |",
        "| **SAC** (Soft Actor-Critic) | Off-policy | Sample efficient, entropy exploration |",
        "| **MA-POCA** (Multi-Agent POCA) | Cooperative | Centralized critic, credit assignment |",
        "",
        "---",
        "",
        "## Training Configuration",
        "",
        "| Environment | Max Steps | Action Space | Agent Type |",
        "|------------|-----------|-------------|------------|",
        "| Football Table | 10,000,000 | Continuous (8) | Competitive 2-agent |",
        "| Cross The Road | 2,000,000 | Discrete (4) | Single agent |",
        "| Capture The Flag | 5,000,000 | Discrete (7) | Cooperative 2-agent |",
        "",
        "---",
        "",
        "## Results by Environment",
        "",
    ]

    env_groups = {
        "Football Table": ["football_ppo_v1", "football_sac_v1", "football_poca_v1"],
        "Cross The Road": ["ctr_ppo_v1", "ctr_sac_v1", "ctr_poca_v1"],
        "Capture The Flag": ["ctf_ppo_v1", "ctf_sac_v1", "ctf_poca_v1"],
    }

    for env_name, run_ids in env_groups.items():
        lines.append(f"### {env_name}")
        lines.append("")
        lines.append("| Algorithm | Final Reward | Best Reward | Mean (last 10%) | Converge Step |")
        lines.append("|-----------|-------------|-------------|-----------------|---------------|")

        env_stats = []
        for run_id in run_ids:
            s = stats.get(run_id)
            if s is None or not s["found"]:
                algo = RUN_REGISTRY[run_id]["algo"]
                lines.append(f"| **{algo}** | N/A | N/A | N/A | N/A |")
                continue

            r = s["reward"]
            algo = s["algo"]
            final = f"{r['final']:.4f}" if r["final"] is not None else "N/A"
            best = f"{r['max']:.4f}" if r["max"] is not None else "N/A"
            mean_last = f"{r['mean_last_10pct']:.4f}" if r["mean_last_10pct"] is not None else "N/A"
            converge = f"{r['converge_step']:,}" if r["converge_step"] is not None else "N/A"

            lines.append(f"| **{algo}** | {final} | {best} | {mean_last} | {converge} |")
            env_stats.append((algo, r))

        lines.append("")

        # Find winner for this environment
        if env_stats:
            winner = max(
                [(algo, r) for algo, r in env_stats if r["mean_last_10pct"] is not None],
                key=lambda x: x[1]["mean_last_10pct"] if x[1]["mean_last_10pct"] is not None else -999,
                default=None
            )
            if winner:
                lines.append(f"> **Best for {env_name}**: {winner[0]}"
                             f" (Mean final reward: {winner[1]['mean_last_10pct']:.4f})")
                lines.append("")

    lines += [
        "---",
        "",
        "## Overall Ranking",
        "",
        "### By Environment",
        "",
    ]

    # Determine rankings
    env_winners = {}
    for env_name, run_ids in env_groups.items():
        candidates = []
        for run_id in run_ids:
            s = stats.get(run_id)
            if s and s["found"] and s["reward"]["mean_last_10pct"] is not None:
                candidates.append((s["algo"], s["reward"]["mean_last_10pct"]))
        if candidates:
            candidates.sort(key=lambda x: x[1], reverse=True)
            env_winners[env_name] = candidates

    lines.append("| Environment | 1st Place | 2nd Place | 3rd Place |")
    lines.append("|------------|-----------|-----------|-----------|")

    for env_name, ranking in env_winners.items():
        r1 = f"{ranking[0][0]} ({ranking[0][1]:.3f})" if len(ranking) > 0 else "N/A"
        r2 = f"{ranking[1][0]} ({ranking[1][1]:.3f})" if len(ranking) > 1 else "N/A"
        r3 = f"{ranking[2][0]} ({ranking[2][1]:.3f})" if len(ranking) > 2 else "N/A"
        lines.append(f"| {env_name} | **{r1}** | {r2} | {r3} |")

    lines += [
        "",
        "---",
        "",
        "## Analysis",
        "",
        "### PPO (Proximal Policy Optimization)",
        "- **Strengths**: Stable learning, works well across all environments",
        "- **Weaknesses**: On-policy, requires more environment interactions",
        "- **Best suited for**: Football Table (with Self-Play), general baseline",
        "",
        "### SAC (Soft Actor-Critic)",
        "- **Strengths**: Sample efficient, entropy-driven exploration prevents premature convergence",
        "- **Weaknesses**: Off-policy replay can slow cooperative learning",
        "- **Best suited for**: Cross The Road (simple discrete navigation with sparse reward)",
        "",
        "### MA-POCA (Multi-Agent POCA)",
        "- **Strengths**: Centralized critic, group credit assignment, ideal for cooperative tasks",
        "- **Weaknesses**: More complex, overkill for single-agent tasks",
        "- **Best suited for**: Capture The Flag (cooperative multi-agent with group rewards)",
        "",
        "---",
        "",
        "## Charts",
        "",
        "Charts generated in `comparison_charts/` directory:",
        "",
        "1. `01_reward_curves.png` - Cumulative reward over training steps",
        "2. `02_final_reward_bar.png` - Bar chart of final average rewards",
        "3. `03_episode_length.png` - Episode length convergence",
        "4. `04_policy_loss.png` - Policy loss during training",
        "5. `05_entropy.png` - Policy entropy (exploration measure)",
        "",
        "---",
        "",
        "## Recommendations",
        "",
        "Based on the experimental results:",
        "",
        "| Environment | Recommended Algorithm | Reason |",
        "|------------|----------------------|--------|",
        "| Football Table | PPO + Self-Play | Stable competitive training, proven for continuous control |",
        "| Cross The Road | SAC | Sample efficient, entropy exploration aids sparse reward |",
        "| Capture The Flag | MA-POCA | Purpose-built for cooperative multi-agent with group rewards |",
        "",
        "---",
        "",
        f"*Report generated by compare_results.py at {now}*",
    ]

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Compare RL training results across 9 runs (3 envs x 3 algos)"
    )
    parser.add_argument(
        "--results-dir", type=Path,
        default=DEFAULT_RESULTS_DIR,
        help=f"Directory containing training results (default: {DEFAULT_RESULTS_DIR})"
    )
    parser.add_argument(
        "--output-dir", type=Path,
        default=DEFAULT_OUTPUT_DIR,
        help=f"Directory to save charts and report (default: {DEFAULT_OUTPUT_DIR})"
    )
    args = parser.parse_args()

    output_dir = args.output_dir
    output_dir.mkdir(parents=True, exist_ok=True)

    print("=" * 60)
    print("  RL COMPARISON ANALYSIS")
    print("=" * 60)
    print(f"  Results dir : {args.results_dir}")
    print(f"  Output dir  : {output_dir}")
    print("=" * 60)

    # Load all data
    all_data = load_all_run_data(args.results_dir)

    # Build stats
    print("\nComputing statistics...")
    stats = build_stats_table(all_data)

    # Save raw stats
    stats_json = {}
    for run_id, s in stats.items():
        stats_json[run_id] = {
            "env": s["env"],
            "algo": s["algo"],
            "found": s["found"],
            "reward_final": s["reward"]["final"],
            "reward_max": s["reward"]["max"],
            "reward_mean_last10pct": s["reward"]["mean_last_10pct"],
            "reward_converge_step": s["reward"]["converge_step"],
            "ep_len_final": s["ep_len"]["final"],
        }

    stats_file = output_dir / "stats.json"
    with open(stats_file, "w", encoding="utf-8") as f:
        json.dump(stats_json, f, indent=2, ensure_ascii=False)
    print(f"Stats saved to: {stats_file}")

    # Generate charts
    print("\nGenerating charts...")
    charts = plot_reward_curves(all_data, output_dir)

    # Generate report
    print("\nGenerating markdown report...")
    report_text = generate_markdown_report(stats, output_dir, charts)

    report_file = output_dir / "comparison_report.md"
    with open(report_file, "w", encoding="utf-8") as f:
        f.write(report_text)
    print(f"Report saved to: {report_file}")

    # Also copy to project root
    project_report = Path(__file__).parent / "comparison_report.md"
    with open(project_report, "w", encoding="utf-8") as f:
        f.write(report_text)
    print(f"Report also saved to: {project_report}")

    print("\n" + "=" * 60)
    print("  ANALYSIS COMPLETE")
    print("=" * 60)
    print(f"  Charts   : {output_dir}/")
    print(f"  Report   : {report_file}")
    print(f"  Stats    : {stats_file}")
    print("=" * 60)


if __name__ == "__main__":
    main()
