#!/usr/bin/env python3
"""
train_sequential.py
====================
Script huấn luyện tuần tự 3 môi trường RL sử dụng Unity ML-Agents.

Môi trường & Thuật toán:
  1. Football Table    → PPO + Self-Play
  2. Cross The Road    → SAC (Soft Actor-Critic)
  3. Capture The Flag  → MA-POCA (Multi-Agent POCA)

Cách chạy:
  python train_sequential.py

Yêu cầu:
  - Conda environment 'mlagents' đã cài mlagents 1.2.0
  - Unity Editor mở đúng Scene tương ứng (Play Mode) khi từng training bắt đầu
  - Hoặc build .exe và truyền --env-path

Tác giả: Tự động tạo bởi Antigravity Agent
"""

import subprocess
import sys
import os
import time
import argparse
import logging
from datetime import datetime
from pathlib import Path

# ─── Cấu hình logging ───────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(
            f"training_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
            encoding="utf-8"
        ),
    ],
)
log = logging.getLogger(__name__)

# ─── Đường dẫn ──────────────────────────────────────────────────────────────
SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_DIR = SCRIPT_DIR  # GraduationProject/
CONFIG_DIR = PROJECT_DIR / "config"
RESULTS_DIR = PROJECT_DIR / "results"
MLAGENTS_LEARN = Path(r"C:\Users\Admin\miniconda3\envs\mlagents\Scripts\mlagents-learn.exe")

# ─── Cấu hình 3 training jobs ────────────────────────────────────────────────
TRAINING_JOBS = [
    {
        "name": "Football_PPO_SelfPlay",
        "description": "Football Table — PPO + Self-Play",
        "config": CONFIG_DIR / "football_ppo.yaml",
        "run_id": f"Football_PPO_{datetime.now().strftime('%Y%m%d')}",
        # Uncommment nếu dùng .exe build:
        # "env_path": r"Builds\Football\FootballTable.exe",
        "extra_args": [],
    },
    {
        "name": "CrossTheRoad_SAC",
        "description": "Cross The Road — SAC",
        "config": CONFIG_DIR / "crosstheroad_sac.yaml",
        "run_id": f"CrossTheRoad_SAC_{datetime.now().strftime('%Y%m%d')}",
        # "env_path": r"Builds\CrossTheRoad\CrossTheRoad.exe",
        "extra_args": [],
    },
    {
        "name": "CaptureFlag_POCA",
        "description": "Capture The Flag — MA-POCA",
        "config": CONFIG_DIR / "captureflag_poca.yaml",
        "run_id": f"CaptureFlag_POCA_{datetime.now().strftime('%Y%m%d')}",
        # "env_path": r"Builds\Collaboration\CaptureFlag.exe",
        "extra_args": [],
    },
]

# ─── Cài đặt chung ──────────────────────────────────────────────────────────
COMMON_ARGS = {
    "time_scale": "20",          # Tăng tốc độ simulation
    "base_port": "5005",         # Port giao tiếp Unity ↔ Python
    "results_dir": str(RESULTS_DIR),
}


def build_command(job: dict, resume: bool = False, force: bool = False) -> list:
    """Xây dựng command line cho mlagents-learn."""
    cmd = [str(MLAGENTS_LEARN), str(job["config"])]

    # Run ID
    cmd += ["--run-id", job["run_id"]]

    # Common args
    cmd += ["--time-scale", COMMON_ARGS["time_scale"]]
    cmd += ["--base-port", COMMON_ARGS["base_port"]]
    cmd += ["--results-dir", COMMON_ARGS["results_dir"]]

    # Env path (nếu dùng .exe)
    if "env_path" in job and job["env_path"]:
        env_full = PROJECT_DIR / job["env_path"]
        if env_full.exists():
            cmd += ["--env", str(env_full)]
            cmd += ["--no-graphics"]
        else:
            log.warning(f"Env path không tồn tại: {env_full}. Sẽ dùng Unity Editor.")

    # Resume hoặc force
    if resume:
        cmd += ["--resume"]
    elif force:
        cmd += ["--force"]

    # Extra args đặc thù cho từng job
    cmd += job.get("extra_args", [])

    return cmd


def run_training(job: dict, resume: bool = False, force: bool = False) -> bool:
    """
    Chạy một training job.

    Returns:
        True nếu thành công, False nếu lỗi.
    """
    log.info("=" * 60)
    log.info(f"▶ Bắt đầu: {job['description']}")
    log.info(f"  Config : {job['config']}")
    log.info(f"  Run ID : {job['run_id']}")
    log.info("=" * 60)

    cmd = build_command(job, resume=resume, force=force)
    log.info(f"Command: {' '.join(cmd)}")

    # Thông báo người dùng cần mở Unity
    if "env_path" not in job:
        log.warning("")
        log.warning("⚠️  YÊU CẦU: Mở Unity Editor và load đúng Scene:")
        if "Football" in job["name"]:
            log.warning("   → Scene: Assets/Football/Football.unity")
        elif "CrossTheRoad" in job["name"]:
            log.warning("   → Scene: Assets/CrossTheRoad/Scenes/")
        elif "CaptureFlag" in job["name"]:
            log.warning("   → Scene: Assets/Collaboration/Collaboration.unity")
        log.warning("   Sau đó nhấn Play trong Unity Editor.")
        log.warning("")
        input("Nhấn ENTER khi Unity đã sẵn sàng (đang Play)...")

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

        # Stream output theo thời gian thực
        for line in process.stdout:
            line = line.rstrip()
            if line:
                log.info(line)

        process.wait()
        elapsed = time.time() - start_time
        hours = int(elapsed // 3600)
        minutes = int((elapsed % 3600) // 60)

        if process.returncode == 0:
            log.info(f"✅ Hoàn thành: {job['description']}")
            log.info(f"   Thời gian: {hours}h {minutes}m")
            return True
        else:
            log.error(f"❌ Lỗi (exit code {process.returncode}): {job['description']}")
            log.error(f"   Thời gian đã chạy: {hours}h {minutes}m")
            return False

    except KeyboardInterrupt:
        log.warning(f"\n⚠️ Người dùng ngắt training: {job['description']}")
        try:
            process.terminate()
            process.wait(timeout=10)
        except Exception:
            process.kill()
        return False

    except Exception as e:
        log.error(f"❌ Exception khi chạy {job['description']}: {e}")
        return False


def check_prerequisites():
    """Kiểm tra các điều kiện trước khi chạy."""
    errors = []

    # Kiểm tra mlagents-learn
    if not MLAGENTS_LEARN.exists():
        errors.append(f"Không tìm thấy mlagents-learn: {MLAGENTS_LEARN}")

    # Kiểm tra config files
    for job in TRAINING_JOBS:
        if not job["config"].exists():
            errors.append(f"Không tìm thấy config: {job['config']}")

    # Kiểm tra results dir
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    if errors:
        log.error("Lỗi tiên quyết:")
        for err in errors:
            log.error(f"  - {err}")
        return False

    log.info("✅ Kiểm tra tiên quyết: OK")
    return True


def print_summary(results: list):
    """In tóm tắt kết quả training."""
    log.info("\n" + "=" * 60)
    log.info("📊 KẾT QUẢ HUẤN LUYỆN")
    log.info("=" * 60)

    for i, (job, success) in enumerate(results):
        status = "✅ THÀNH CÔNG" if success else "❌ THẤT BẠI"
        log.info(f"  {i+1}. {job['description']}: {status}")
        if success:
            result_dir = RESULTS_DIR / job["run_id"]
            log.info(f"     → Kết quả: {result_dir}")

    log.info("=" * 60)


def main():
    parser = argparse.ArgumentParser(
        description="Huấn luyện tuần tự 3 môi trường RL: Football, CrossTheRoad, CaptureFlag"
    )
    parser.add_argument(
        "--resume", action="store_true",
        help="Tiếp tục từ checkpoint (dùng run-id hiện có)"
    )
    parser.add_argument(
        "--force", action="store_true",
        help="Ghi đè kết quả training cũ với cùng run-id"
    )
    parser.add_argument(
        "--only", type=str, default=None,
        choices=["football", "crosstheroad", "captureflag"],
        help="Chỉ chạy một môi trường cụ thể"
    )
    parser.add_argument(
        "--skip", nargs="+", default=[],
        choices=["football", "crosstheroad", "captureflag"],
        help="Bỏ qua một hoặc nhiều môi trường"
    )

    args = parser.parse_args()

    log.info("🚀 TRAINING PIPELINE - 3 RL ALGORITHMS")
    log.info("━" * 60)
    log.info("  1. Football Table    → PPO + Self-Play")
    log.info("  2. Cross The Road    → SAC")
    log.info("  3. Capture The Flag  → MA-POCA")
    log.info("━" * 60)

    if not check_prerequisites():
        sys.exit(1)

    # Lọc jobs theo tham số
    jobs_to_run = []
    filter_map = {
        "football": "Football_PPO_SelfPlay",
        "crosstheroad": "CrossTheRoad_SAC",
        "captureflag": "CaptureFlag_POCA",
    }

    for job in TRAINING_JOBS:
        job_key = [k for k, v in filter_map.items() if v == job["name"]]
        if job_key:
            key = job_key[0]
            if args.only and args.only != key:
                continue
            if key in args.skip:
                log.info(f"⏭ Bỏ qua: {job['description']}")
                continue
        jobs_to_run.append(job)

    if not jobs_to_run:
        log.warning("Không có job nào để chạy!")
        sys.exit(0)

    log.info(f"\nSẽ chạy {len(jobs_to_run)} training job(s):")
    for i, job in enumerate(jobs_to_run):
        log.info(f"  {i+1}. {job['description']}")

    # Chạy tuần tự
    results = []
    for i, job in enumerate(jobs_to_run):
        log.info(f"\n[{i+1}/{len(jobs_to_run)}] Chuẩn bị: {job['description']}")

        success = run_training(job, resume=args.resume, force=args.force)
        results.append((job, success))

        if not success:
            log.warning(f"Job thất bại: {job['description']}")
            answer = input("Tiếp tục với job tiếp theo? [y/N]: ").strip().lower()
            if answer != "y":
                log.info("Dừng pipeline.")
                break

        # Nghỉ ngắn giữa các job
        if i < len(jobs_to_run) - 1 and success:
            log.info("⏸ Nghỉ 5 giây trước job tiếp theo...")
            time.sleep(5)

    print_summary(results)

    # Exit với code 1 nếu có job thất bại
    if not all(success for _, success in results):
        sys.exit(1)


if __name__ == "__main__":
    main()
