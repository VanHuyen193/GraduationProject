#!/usr/bin/env python3
"""
train_all_sequential.py
========================
Sequential training of 3 RL algorithms across 3 Unity environments.

9 Training runs:
  Football Table    x [PPO, SAC, MA-POCA]
  Cross The Road    x [PPO, SAC, MA-POCA]
  Capture The Flag  x [PPO, SAC, MA-POCA]

Usage:
  python train_all_sequential.py
  python train_all_sequential.py --only football
  python train_all_sequential.py --only crossroad
  python train_all_sequential.py --only capture
  python train_all_sequential.py --resume
  python train_all_sequential.py --skip football_sac

Requirements:
  - Miniconda env 'mlagents' with mlagents 1.2.0 installed
  - Unity Editor open with correct Scene in Play Mode for each run
"""

import subprocess
import sys
import os
import time
import argparse
import json
import logging
from datetime import datetime
from pathlib import Path

# ─── Logging setup ──────────────────────────────────────────────────────────
LOG_FILE = f"training_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(LOG_FILE, encoding="utf-8"),
    ],
)
log = logging.getLogger(__name__)

# ─── Paths ───────────────────────────────────────────────────────────────────
PROJECT_DIR = Path(__file__).resolve().parent
CONFIG_DIR = PROJECT_DIR / "config"
RESULTS_DIR = PROJECT_DIR / "results"
MLAGENTS_EXE = Path(r"C:\Users\Admin\miniconda3\envs\mlagents\Scripts\mlagents-learn.exe")
STATUS_FILE = PROJECT_DIR / "training_status.json"

# ─── Training Job Definitions ────────────────────────────────────────────────
# Each environment trains with the same max_steps for all 3 algorithms.
# This ensures fair comparison.

FOOTBALL_STEPS = 10000000   # 10M - competitive continuous env needs more steps
CROSSROAD_STEPS = 2000000   # 2M  - simple navigation converges fast
CAPTURE_STEPS = 5000000     # 5M  - cooperative puzzle needs moderate steps

TRAINING_JOBS = [
    # ── Football Table ─────────────────────────────────────────────────────
    {
        "id": "football_ppo",
        "name": "Football - PPO + Self-Play",
        "env": "football",
        "algo": "ppo",
        "config": CONFIG_DIR / "football_ppo.yaml",
        "run_id": "football_ppo_v1",
        "scene_hint": "Assets/Football/Football.unity",
        "behavior": "Football",
        "max_steps": FOOTBALL_STEPS,
    },
    {
        "id": "football_sac",
        "name": "Football - SAC",
        "env": "football",
        "algo": "sac",
        "config": CONFIG_DIR / "football_sac.yaml",
        "run_id": "football_sac_v1",
        "scene_hint": "Assets/Football/Football.unity",
        "behavior": "Football",
        "max_steps": FOOTBALL_STEPS,
    },
    {
        "id": "football_poca",
        "name": "Football - MA-POCA",
        "env": "football",
        "algo": "poca",
        "config": CONFIG_DIR / "football_poca.yaml",
        "run_id": "football_poca_v1",
        "scene_hint": "Assets/Football/Football.unity",
        "behavior": "Football",
        "max_steps": FOOTBALL_STEPS,
    },
    # ── Cross The Road ─────────────────────────────────────────────────────
    {
        "id": "ctr_ppo",
        "name": "Cross The Road - PPO",
        "env": "crossroad",
        "algo": "ppo",
        "config": CONFIG_DIR / "ctr_ppo.yaml",
        "run_id": "ctr_ppo_v1",
        "scene_hint": "Assets/CrossTheRoad/Scenes/",
        "behavior": "CrossTheRoad",
        "max_steps": CROSSROAD_STEPS,
    },
    {
        "id": "ctr_sac",
        "name": "Cross The Road - SAC",
        "env": "crossroad",
        "algo": "sac",
        "config": CONFIG_DIR / "ctr_sac.yaml",
        "run_id": "ctr_sac_v1",
        "scene_hint": "Assets/CrossTheRoad/Scenes/",
        "behavior": "CrossTheRoad",
        "max_steps": CROSSROAD_STEPS,
    },
    {
        "id": "ctr_poca",
        "name": "Cross The Road - MA-POCA",
        "env": "crossroad",
        "algo": "poca",
        "config": CONFIG_DIR / "ctr_poca.yaml",
        "run_id": "ctr_poca_v1",
        "scene_hint": "Assets/CrossTheRoad/Scenes/",
        "behavior": "CrossTheRoad",
        "max_steps": CROSSROAD_STEPS,
    },
    # ── Capture The Flag ───────────────────────────────────────────────────
    {
        "id": "ctf_ppo",
        "name": "Capture The Flag - PPO",
        "env": "capture",
        "algo": "ppo",
        "config": CONFIG_DIR / "ctf_ppo.yaml",
        "run_id": "ctf_ppo_v1",
        "scene_hint": "Assets/Collaboration/Collaboration.unity",
        "behavior": "PuzzleBehavior",
        "max_steps": CAPTURE_STEPS,
    },
    {
        "id": "ctf_sac",
        "name": "Capture The Flag - SAC",
        "env": "capture",
        "algo": "sac",
        "config": CONFIG_DIR / "ctf_sac.yaml",
        "run_id": "ctf_sac_v1",
        "scene_hint": "Assets/Collaboration/Collaboration.unity",
        "behavior": "PuzzleBehavior",
        "max_steps": CAPTURE_STEPS,
    },
    {
        "id": "ctf_poca",
        "name": "Capture The Flag - MA-POCA (ideal)",
        "env": "capture",
        "algo": "poca",
        "config": CONFIG_DIR / "ctf_poca.yaml",
        "run_id": "ctf_poca_v1",
        "scene_hint": "Assets/Collaboration/Collaboration.unity",
        "behavior": "PuzzleBehavior",
        "max_steps": CAPTURE_STEPS,
    },
]


def load_status() -> dict:
    """Load training status from JSON file."""
    if STATUS_FILE.exists():
        try:
            with open(STATUS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {}


def save_status(status: dict):
    """Save training status to JSON file."""
    with open(STATUS_FILE, "w", encoding="utf-8") as f:
        json.dump(status, f, indent=2, ensure_ascii=False)


def check_prerequisites() -> bool:
    """Check all prerequisites before starting."""
    errors = []

    if not MLAGENTS_EXE.exists():
        errors.append(f"mlagents-learn not found: {MLAGENTS_EXE}")

    for job in TRAINING_JOBS:
        if not job["config"].exists():
            errors.append(f"Config missing: {job['config']}")

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    if errors:
        for err in errors:
            log.error(f"MISSING: {err}")
        return False

    log.info("Prerequisites check: ALL OK")
    return True


def prompt_unity_ready(job: dict):
    """Prompt user to prepare Unity Editor."""
    log.info("")
    log.info("=" * 65)
    log.info(f"  NEXT: {job['name']}")
    log.info("=" * 65)
    log.info(f"  Algorithm : {job['algo'].upper()}")
    log.info(f"  Run ID    : {job['run_id']}")
    log.info(f"  Config    : {job['config'].name}")
    log.info(f"  Max Steps : {job['max_steps']:,}")
    log.info("")
    log.info(f"  ACTION REQUIRED:")
    log.info(f"  1. Open Unity Editor")
    log.info(f"  2. Load Scene: {job['scene_hint']}")
    log.info(f"  3. Press PLAY in Unity Editor")
    log.info(f"  4. Then press ENTER here")
    log.info("=" * 65)
    input("  [Press ENTER when Unity is in Play Mode] ")
    log.info("")


def run_training(job: dict, resume: bool = False, force: bool = False) -> dict:
    """
    Run a single training job and return result dict.

    Returns:
        dict with keys: success, duration_s, exit_code
    """
    result = {
        "job_id": job["id"],
        "run_id": job["run_id"],
        "success": False,
        "duration_s": 0,
        "exit_code": -1,
        "started_at": datetime.now().isoformat(),
        "finished_at": None,
    }

    cmd = [
        str(MLAGENTS_EXE),
        str(job["config"]),
        "--run-id", job["run_id"],
        "--results-dir", str(RESULTS_DIR),
        "--time-scale", "20",
        "--base-port", "5005",
    ]

    if resume:
        cmd.append("--resume")
    elif force:
        cmd.append("--force")

    log.info(f"Command: {' '.join(cmd)}")
    start_time = time.time()

    try:
        process = subprocess.Popen(
            cmd,
            cwd=str(PROJECT_DIR),
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding="utf-8",
            errors="replace",
            bufsize=1,
        )

        for line in process.stdout:
            line = line.rstrip()
            if line:
                log.info(line)

        process.wait()
        elapsed = time.time() - start_time

        result["duration_s"] = elapsed
        result["exit_code"] = process.returncode
        result["success"] = (process.returncode == 0)
        result["finished_at"] = datetime.now().isoformat()

        h = int(elapsed // 3600)
        m = int((elapsed % 3600) // 60)

        if result["success"]:
            log.info(f"SUCCESS: {job['name']} completed in {h}h {m}m")
        else:
            log.error(f"FAILED: {job['name']} (exit {process.returncode}) after {h}h {m}m")

    except KeyboardInterrupt:
        log.warning(f"INTERRUPTED: {job['name']}")
        try:
            process.terminate()
            process.wait(timeout=10)
        except Exception:
            try:
                process.kill()
            except Exception:
                pass
        result["duration_s"] = time.time() - start_time
        result["finished_at"] = datetime.now().isoformat()

    except Exception as e:
        log.error(f"EXCEPTION in {job['name']}: {e}")
        result["finished_at"] = datetime.now().isoformat()

    return result


def print_summary(all_results: list):
    """Print a final summary table of all training results."""
    log.info("")
    log.info("=" * 70)
    log.info("  TRAINING SUMMARY")
    log.info("=" * 70)
    log.info(f"  {'Job':<30} {'Status':<12} {'Duration'}")
    log.info("  " + "-" * 60)

    for r in all_results:
        status = "SUCCESS" if r["success"] else "FAILED"
        elapsed = r.get("duration_s", 0)
        h = int(elapsed // 3600)
        m = int((elapsed % 3600) // 60)
        duration = f"{h}h {m}m" if h > 0 else f"{m}m"
        log.info(f"  {r['run_id']:<30} {status:<12} {duration}")

    log.info("=" * 70)
    successful = sum(1 for r in all_results if r["success"])
    log.info(f"  Completed: {successful}/{len(all_results)} jobs")

    if successful == len(all_results):
        log.info("  ALL TRAINING RUNS COMPLETED SUCCESSFULLY!")
        log.info("")
        log.info(f"  Results directory: {RESULTS_DIR}")
        log.info("  Next step: Run compare_results.py to generate analysis report.")
    log.info("=" * 70)


def main():
    parser = argparse.ArgumentParser(
        description="Sequential RL training: 3 algorithms x 3 environments = 9 runs"
    )
    parser.add_argument(
        "--only", type=str,
        choices=["football", "crossroad", "capture"],
        help="Only run jobs for one environment"
    )
    parser.add_argument(
        "--skip", nargs="+", default=[],
        help="Skip specific job IDs (e.g. football_sac ctr_poca)"
    )
    parser.add_argument(
        "--resume", action="store_true",
        help="Resume from existing checkpoints"
    )
    parser.add_argument(
        "--force", action="store_true",
        help="Overwrite existing results"
    )
    parser.add_argument(
        "--from-job", type=str, default=None,
        help="Start from a specific job ID (skip all before it)"
    )
    args = parser.parse_args()

    log.info("=" * 65)
    log.info("  RL TRAINING PIPELINE - 9 Runs")
    log.info("=" * 65)
    log.info("  Environments x Algorithms:")
    log.info("  Football Table   : PPO | SAC | MA-POCA")
    log.info("  Cross The Road   : PPO | SAC | MA-POCA")
    log.info("  Capture The Flag : PPO | SAC | MA-POCA")
    log.info("=" * 65)

    if not check_prerequisites():
        log.error("Prerequisites failed. Exiting.")
        sys.exit(1)

    # Filter jobs
    status = load_status()
    jobs_to_run = []
    reached_from = (args.from_job is None)

    for job in TRAINING_JOBS:
        # --from-job: skip until we find the job
        if not reached_from:
            if job["id"] == args.from_job:
                reached_from = True
            else:
                log.info(f"Skipping (before --from-job): {job['id']}")
                continue

        # --only filter
        if args.only and job["env"] != args.only:
            log.info(f"Skipping (--only {args.only}): {job['id']}")
            continue

        # --skip filter
        if job["id"] in args.skip:
            log.info(f"Skipping (--skip): {job['id']}")
            continue

        # Already completed (from status file) - skip unless force
        if not args.force and job["id"] in status and status[job["id"]].get("success"):
            log.info(f"Already completed (skipping): {job['id']}")
            continue

        jobs_to_run.append(job)

    if not jobs_to_run:
        log.info("No jobs to run. All done or filtered out.")
        sys.exit(0)

    log.info(f"\nWill run {len(jobs_to_run)} job(s):")
    for i, j in enumerate(jobs_to_run, 1):
        log.info(f"  {i}. {j['name']} (run_id: {j['run_id']})")
    log.info("")

    all_results = []

    for i, job in enumerate(jobs_to_run):
        log.info(f"\n[Job {i+1}/{len(jobs_to_run)}] Starting: {job['name']}")

        # Prompt user to prepare Unity
        prompt_unity_ready(job)

        result = run_training(job, resume=args.resume, force=args.force)
        all_results.append(result)

        # Persist status
        status[job["id"]] = result
        save_status(status)

        if not result["success"]:
            log.warning(f"Job failed: {job['name']}")
            answer = input("Continue to next job? [y/N]: ").strip().lower()
            if answer != "y":
                log.info("Pipeline stopped by user.")
                break

        if i < len(jobs_to_run) - 1 and result["success"]:
            log.info("Pausing 5 seconds before next job...")
            time.sleep(5)

    print_summary(all_results)

    # Write summary JSON
    summary_file = RESULTS_DIR / "training_summary.json"
    with open(summary_file, "w", encoding="utf-8") as f:
        json.dump(all_results, f, indent=2, ensure_ascii=False)
    log.info(f"Summary saved to: {summary_file}")
    log.info(f"Log saved to: {LOG_FILE}")

    failed = [r for r in all_results if not r["success"]]
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
