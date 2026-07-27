#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
train_all.py — dieu phoi toan bo 9 lan huan luyen cho do an.

Thay the train_all_sequential.py (script cu tro sai duong dan conda cua may khac
va con liet ke bo job 3x3 khong con dung voi bao cao).

9 to hop (run-id PHAI trung voi export_training_data.py, dung sua tuy tien):
    Football Table   : FB01 (PPO) | Football_SAC_01 | Football_POCA_01
    Cross The Road   : ctr01 (PPO) | CrossTheRoad_SAC_01 | ctr_poca_v1 | ctr_mappo_v1
    Capture The Flag : ctf_poca_v2 (MA-POCA) | ctf_mappo_v2 (MAPPO)

Hai che do chay:
  --mode build   (KHUYEN NGHI) tro toi file .exe da build san; chay hoan toan tu
                 dong, khong can mo Editor, dung duoc --num-envs de chay song song.
  --mode editor  giu cach cu: script in ra loi nhac roi cho ban bam Play trong
                 Unity Editor. Khong tu dong hoa duoc, chi dung khi chua co build.

ViDu:
  # 1. Kiem tra cau hinh trong ~10 phut truoc khi dot ca dem
  python train_all.py --smoke

  # 2. Chay that (build mode)
  python train_all.py --mode build --num-envs 2

  # 3. Chay tiep sau khi ngat
  python train_all.py --mode build --resume

  # 4. Chi mot moi truong
  python train_all.py --mode build --only crossroad
"""

from __future__ import annotations

import argparse
import json
import os
import re
import signal
import subprocess
import sys
import time
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta
from pathlib import Path

# ─────────────────────────────────────────────────────────────────────────────
# Duong dan
# ─────────────────────────────────────────────────────────────────────────────
PROJECT_DIR = Path(__file__).resolve().parent
CONFIG_DIR = PROJECT_DIR / "config"
RESULTS_DIR = PROJECT_DIR / "results"
BUILD_DIR = PROJECT_DIR / "Builds"
LOG_DIR = PROJECT_DIR / "training_logs"
STATUS_FILE = PROJECT_DIR / "training_status.json"

# Env conda: do tim theo nhieu vi tri de script chay duoc tren CA HAI may
# (laptop 'vanhu' va may desktop). Script cu hardcode 'Admin' nen hong tren may nay.
# Uu tien: bien moi truong MLAGENTS_ENV > env dang kich hoat > cac vi tri quen thuoc.
def _find_conda_env() -> Path:
    candidates: list[Path] = []
    if os.environ.get("MLAGENTS_ENV"):
        candidates.append(Path(os.environ["MLAGENTS_ENV"]))
    if os.environ.get("CONDA_PREFIX"):
        candidates.append(Path(os.environ["CONDA_PREFIX"]))
    for user in (os.environ.get("USERNAME", ""), "vanhu", "Admin"):
        if not user:
            continue
        for base in ("miniconda3", "anaconda3"):
            candidates.append(Path(rf"C:\Users\{user}\{base}\envs\mlagents"))
    for c in candidates:
        if (c / "Scripts" / "mlagents-learn.exe").exists():
            return c
    return candidates[0] if candidates else Path(".")


CONDA_ENV = _find_conda_env()
MLAGENTS_LEARN = CONDA_ENV / "Scripts" / "mlagents-learn.exe"
CONDA_PYTHON = CONDA_ENV / "python.exe"


# ─────────────────────────────────────────────────────────────────────────────
# Dinh nghia job
# ─────────────────────────────────────────────────────────────────────────────
@dataclass
class Job:
    id: str
    env: str            # football | crossroad | capture
    algo: str           # PPO | SAC | MA-POCA | MAPPO
    config: str         # ten file trong config/
    run_id: str         # PHAI trung export_training_data.py
    behavior: str
    steps_full: int     # do dai da bao cao trong chuong 4
    steps_reduced: int  # ngan sach rut gon (mac dinh)
    build: str          # ten thu muc + file .exe trong Builds/
    scene: str          # chi de nhac khi chay --mode editor
    # Ghi chu rui ro: hien len trong buoc kiem tra truoc khi chay.
    risky: str = ""

    def budget(self, profile: str) -> int:
        return self.steps_full if profile == "full" else self.steps_reduced


# Ngan sach buoc.
#   full    = dung do dai THUC TE cua cac lan chay da bao cao o chuong 4 (12,9M).
#   reduced = mac dinh, cat khoang 35-50% moi run (8,5M) de co ket qua som.
#
# LUU Y QUAN TRONG — hai cho KHONG duoc cat theo ti le:
#   * ctf_mappo: MAPPO chi giai duoc cau do tu ~1,28M buoc tro di. Day la PHAT
#     HIEN CHINH cua ca do an. Cat xuong 0,8M thi duong cong khong bao gio the
#     hien buoc ngoat, va ket luan trung tam cua chuong 4 sup do. Vi vay giu
#     1,5M, va ctf_poca giu bang dung nhu vay de so sanh cong bang.
#   * ctr_sac: SAC hoi tu o ~150K nen ban than lan chay da rat ngan; cat nua thi
#     mat luon doan plateau la bang chung cua ket luan "hieu qua mau vuot troi".
#     Giu nguyen 200K (chi chiem ~2% tong ngan sach).
JOBS: list[Job] = [
    # ── Cross The Road: chay TRUOC vi nhanh nhat, phat hien loi som ──────────
    Job("ctr_ppo",   "crossroad", "PPO",     "ctr_ppo.yaml",   "ctr01",
        "CrossTheRoad", 2_000_000, 1_200_000, "CrossTheRoad",
        "Assets/CrossTheRoad/Scenes/CrossTheRoad.unity"),
    Job("ctr_sac",   "crossroad", "SAC",     "ctr_sac.yaml",   "CrossTheRoad_SAC_01",
        "CrossTheRoad",   200_000,   200_000, "CrossTheRoad",
        "Assets/CrossTheRoad/Scenes/CrossTheRoad.unity"),
    Job("ctr_poca",  "crossroad", "MA-POCA", "ctr_poca.yaml",  "ctr_poca_v1",
        "CrossTheRoad", 2_000_000, 1_200_000, "CrossTheRoad",
        "Assets/CrossTheRoad/Scenes/CrossTheRoad.unity"),
    Job("ctr_mappo", "crossroad", "MAPPO",   "ctr_mappo.yaml", "ctr_mappo_v1",
        "CrossTheRoad", 2_000_000, 1_200_000, "CrossTheRoad",
        "Assets/CrossTheRoad/Scenes/CrossTheRoad.unity"),

    # ── Capture The Flag: co curriculum handoff_required ─────────────────────
    Job("ctf_poca",  "capture", "MA-POCA", "ctf_poca.yaml",  "ctf_poca_v2",
        "PuzzleBehavior", 1_700_000, 1_500_000, "CaptureTheFlag",
        "Assets/Collaboration/Scenes/CaptureTheFlag.unity",
        risky="Khong cat duoi 1,5M: MAPPO chi giai duoc cau do tu ~1,28M buoc."),
    Job("ctf_mappo", "capture", "MAPPO",   "ctf_mappo.yaml", "ctf_mappo_v2",
        "PuzzleBehavior", 1_600_000, 1_500_000, "CaptureTheFlag",
        "Assets/Collaboration/Scenes/CaptureTheFlag.unity",
        risky="Khong cat duoi 1,5M: day la lan chay chua PHAT HIEN CHINH cua do an."),

    # ── Football Table: self-play, nang nhat, chay cuoi ──────────────────────
    Job("fb_ppo",    "football", "PPO",     "football_ppo.yaml",  "FB01",
        "Football", 1_600_000, 800_000, "Football", "Assets/Football/Football.unity"),
    Job("fb_poca",   "football", "MA-POCA", "football_poca.yaml", "Football_POCA_01",
        "Football",   900_000, 450_000, "Football", "Assets/Football/Football.unity"),
    Job("fb_sac",    "football", "SAC",     "football_sac.yaml",  "Football_SAC_01",
        "Football",   900_000, 450_000, "Football", "Assets/Football/Football.unity",
        risky="SAC + self_play: ML-Agents khong ho tro chinh thuc. Neu trainer bao "
              "loi, xem muc 'SAC tren Football' trong ke hoach."),
]

ENV_ORDER = ["crossroad", "capture", "football"]


# ─────────────────────────────────────────────────────────────────────────────
# Log
# ─────────────────────────────────────────────────────────────────────────────
# Console Windows mac dinh la cp1252 -> in ky tu ke khung se no UnicodeEncodeError.
for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass


class Tee:
    def __init__(self, path: Path):
        LOG_DIR.mkdir(exist_ok=True)
        self.f = open(path, "a", encoding="utf-8")

    def __call__(self, msg: str = "", level: str = "INFO"):
        ts = datetime.now().strftime("%H:%M:%S")
        line = f"{ts} [{level}] {msg}" if msg else ""
        print(line, flush=True)
        self.f.write(line + "\n")
        self.f.flush()


log = Tee(LOG_DIR / f"train_{datetime.now():%Y%m%d_%H%M%S}.log")


def hms(sec: float) -> str:
    return str(timedelta(seconds=int(sec)))


# ─────────────────────────────────────────────────────────────────────────────
# Trang thai (cho --resume)
# ─────────────────────────────────────────────────────────────────────────────
def load_status() -> dict:
    if STATUS_FILE.exists():
        try:
            return json.loads(STATUS_FILE.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {}


def save_status(st: dict) -> None:
    STATUS_FILE.write_text(json.dumps(st, indent=2, ensure_ascii=False),
                           encoding="utf-8")


def run_has_output(job: Job) -> bool:
    """Da co tfevents thuc su chua (dung de bo qua job da xong khi --resume)."""
    d = RESULTS_DIR / job.run_id
    return d.exists() and any(d.glob("**/*.tfevents.*"))


# ─────────────────────────────────────────────────────────────────────────────
# Kiem tra moi truong truoc khi chay
# ─────────────────────────────────────────────────────────────────────────────
def preflight(jobs: list[Job], mode: str) -> bool:
    ok = True
    log("─" * 70)
    log("KIEM TRA TRUOC KHI CHAY")
    log("─" * 70)

    if not MLAGENTS_LEARN.exists():
        log(f"KHONG thay mlagents-learn: {MLAGENTS_LEARN}", "ERROR")
        ok = False
    else:
        log(f"mlagents-learn : {MLAGENTS_LEARN}")

    # plugin trainer (mappo la plugin ngoai, khong co san)
    try:
        out = subprocess.run(
            [str(CONDA_PYTHON), "-c",
             "import importlib.metadata as m;"
             "print(','.join(e.name for e in m.entry_points(group='mlagents.trainer_type')))"],
            capture_output=True, text=True, timeout=60)
        plugins = out.stdout.strip()
        log(f"trainer plugins: {plugins}")
        if "mappo" not in plugins:
            log("Thieu plugin 'mappo'. Cai bang:", "ERROR")
            log(r'  pip install --no-build-isolation -e ..\ml-agents\ml-agents-trainer-plugin',
                "ERROR")
            ok = False
    except Exception as e:
        log(f"Khong kiem tra duoc plugin: {e}", "WARN")

    for j in jobs:
        cfg = CONFIG_DIR / j.config
        if not cfg.exists():
            log(f"[{j.id}] thieu config {cfg}", "ERROR")
            ok = False
        if cfg.exists() and cfg.stat().st_size == 0:
            log(f"[{j.id}] config RONG: {cfg}", "ERROR")
            ok = False
        if mode == "build":
            exe = BUILD_DIR / j.build / f"{j.build}.exe"
            if not exe.exists():
                log(f"[{j.id}] thieu build {exe}", "ERROR")
                ok = False
        if j.risky:
            log(f"[{j.id}] CANH BAO: {j.risky}", "WARN")

    # canh bao trung run-id da co du lieu
    for j in jobs:
        if run_has_output(j):
            log(f"[{j.id}] run-id '{j.run_id}' DA co tfevents — se bo qua neu "
                f"--resume, hoac can --force de ghi de", "WARN")

    log(f"Ket qua kiem tra: {'OK' if ok else 'CO LOI'}")
    log("─" * 70)
    return ok


# ─────────────────────────────────────────────────────────────────────────────
# Chay mot job
# ─────────────────────────────────────────────────────────────────────────────
STEP_RE = re.compile(r"Step:\s*([\d,]+)\.\s*Time Elapsed:\s*([\d.]+)")


def build_cmd(job: Job, args, steps: int) -> list[str]:
    cmd = [str(MLAGENTS_LEARN), str(CONFIG_DIR / job.config),
           "--run-id", job.run_id,
           "--results-dir", str(RESULTS_DIR)]
    if args.force:
        cmd.append("--force")
    if args.mode == "build":
        cmd += ["--env", str(BUILD_DIR / job.build / f"{job.build}.exe"),
                "--no-graphics"]
        if args.num_envs > 1:
            cmd += ["--num-envs", str(args.num_envs),
                    "--base-port", str(args.base_port)]
    cmd += ["--time-scale", str(args.time_scale)]
    # ghi de ngan sach buoc ma khong phai sua yaml
    cmd += ["--max-steps", str(steps)] if args.override_steps else []
    return cmd


def run_job(job: Job, args, idx: int, total: int) -> tuple[bool, float, int]:
    steps = args.smoke_steps if args.smoke else job.budget(args.budget)
    log("")
    log("=" * 70)
    log(f"[{idx}/{total}]  {job.id}   {job.algo} @ {job.env}")
    log(f"        run-id  : {job.run_id}")
    log(f"        config  : {job.config}")
    log(f"        steps   : {steps:,}")
    log("=" * 70)

    if args.mode == "editor":
        log(f">>> MO Unity Editor voi scene: {job.scene}")
        log(">>> Khi thay dong 'Listening on port 5004' thi BAM PLAY.")

    cmd = build_cmd(job, args, steps)
    log("cmd: " + " ".join(cmd))
    if args.dry_run:
        return True, 0.0, 0

    t0 = time.time()
    last_step = 0
    logf = LOG_DIR / f"{job.run_id}.log"
    proc = subprocess.Popen(cmd, cwd=str(PROJECT_DIR), stdout=subprocess.PIPE,
                            stderr=subprocess.STDOUT, text=True, bufsize=1,
                            encoding="utf-8", errors="replace")
    try:
        with open(logf, "w", encoding="utf-8") as fh:
            for line in proc.stdout:
                fh.write(line)
                m = STEP_RE.search(line)
                if m:
                    last_step = int(m.group(1).replace(",", ""))
                    el = time.time() - t0
                    sps = last_step / el if el > 0 else 0
                    eta = (steps - last_step) / sps if sps > 0 else 0
                    log(f"    {last_step:>10,} / {steps:,}  "
                        f"({100*last_step/steps:5.1f}%)  "
                        f"{sps:6.0f} step/s  ETA {hms(eta)}")
                elif any(k in line for k in ("Error", "error", "Traceback",
                                             "Exception", "UnityTrainerException")):
                    log("    " + line.rstrip(), "WARN")
        proc.wait(timeout=args.timeout)
    except subprocess.TimeoutExpired:
        log(f"Qua thoi gian {args.timeout}s — dung job", "ERROR")
        proc.kill()
        return False, time.time() - t0, last_step
    except KeyboardInterrupt:
        log("Nguoi dung ngat (Ctrl-C) — dung job", "WARN")
        proc.terminate()
        raise

    dur = time.time() - t0
    ok = proc.returncode == 0 and run_has_output(job)
    log(f"--> {'XONG' if ok else 'THAT BAI'}  ({hms(dur)}, "
        f"{last_step:,} steps, log: {logf.name})",
        "INFO" if ok else "ERROR")
    if not ok:
        log(f"    xem chi tiet: {logf}", "ERROR")
    return ok, dur, last_step


# ─────────────────────────────────────────────────────────────────────────────
def main() -> int:
    p = argparse.ArgumentParser(description="Dieu phoi 9 lan huan luyen")
    p.add_argument("--mode", choices=["build", "editor"], default="build",
                   help="build = tu dong bang file .exe (khuyen nghi); "
                        "editor = cho bam Play thu cong")
    p.add_argument("--only", choices=ENV_ORDER, help="chi chay mot moi truong")
    p.add_argument("--jobs", help="danh sach id job, phan cach dau phay")
    p.add_argument("--skip", default="", help="id job bo qua, phan cach dau phay")
    p.add_argument("--resume", action="store_true",
                   help="bo qua job da co tfevents")
    p.add_argument("--force", action="store_true",
                   help="truyen --force cho mlagents-learn (ghi de run-id cu)")
    p.add_argument("--num-envs", type=int, default=1,
                   help="so tien trinh Unity song song (chi voi --mode build)")
    p.add_argument("--base-port", type=int, default=5005)
    p.add_argument("--time-scale", type=float, default=20.0)
    p.add_argument("--timeout", type=int, default=6 * 3600,
                   help="tran thoi gian moi job, giay")
    p.add_argument("--override-steps", action="store_true",
                   help="truyen --max-steps de ghi de yaml theo ngan sach trong JOBS")
    p.add_argument("--budget", choices=["reduced", "full"], default="reduced",
                   help="reduced (mac dinh, ~8,5M buoc) hoac full (~12,9M buoc, "
                        "bang dung do dai da bao cao o chuong 4)")
    p.add_argument("--smoke", action="store_true",
                   help="chay thu moi job vai chuc nghin buoc de kiem tra cau hinh")
    p.add_argument("--smoke-steps", type=int, default=20_000)
    p.add_argument("--dry-run", action="store_true", help="chi in lenh, khong chay")
    p.add_argument("--no-export", action="store_true",
                   help="khong chay export_training_data.py sau khi xong")
    args = p.parse_args()

    if args.smoke:
        args.override_steps = True
        args.force = True

    jobs = list(JOBS)
    if args.only:
        jobs = [j for j in jobs if j.env == args.only]
    if args.jobs:
        want = {s.strip() for s in args.jobs.split(",")}
        jobs = [j for j in jobs if j.id in want]
    if args.skip:
        drop = {s.strip() for s in args.skip.split(",")}
        jobs = [j for j in jobs if j.id not in drop]
    if not jobs:
        log("Khong co job nao khop bo loc", "ERROR")
        return 1

    st = load_status()
    if args.resume:
        before = len(jobs)
        jobs = [j for j in jobs if not run_has_output(j)]
        log(f"--resume: bo qua {before - len(jobs)} job da co ket qua")
        if not jobs:
            log("Tat ca job da xong.")
            return 0

    if not preflight(jobs, args.mode) and not args.dry_run:
        log("Dung lai vi kiem tra that bai. Sua roi chay lai.", "ERROR")
        return 1

    total_steps = sum(args.smoke_steps if args.smoke else j.budget(args.budget)
                      for j in jobs)
    log(f"Se chay {len(jobs)} job, tong {total_steps:,} buoc "
        f"(ngan sach: {args.budget})")
    log(f"Che do: {args.mode} | num-envs {args.num_envs} | "
        f"time-scale {args.time_scale}")

    t_start = time.time()
    done, failed = [], []
    for i, job in enumerate(jobs, 1):
        try:
            ok, dur, steps_done = run_job(job, args, i, len(jobs))
        except KeyboardInterrupt:
            log("Ngat toan bo. Chay lai voi --resume de tiep tuc.", "WARN")
            save_status(st)
            return 130
        st[job.id] = {
            "run_id": job.run_id, "ok": ok, "seconds": round(dur, 1),
            "steps": steps_done, "at": datetime.now().isoformat(timespec="seconds"),
            "smoke": bool(args.smoke),
        }
        save_status(st)
        (done if ok else failed).append(job.id)
        if not ok and not args.smoke:
            log("Job that bai — van chay tiep cac job con lai.", "WARN")

    log("")
    log("=" * 70)
    log(f"TONG KET  ({hms(time.time() - t_start)})")
    log(f"  Thanh cong : {len(done)}  {done}")
    log(f"  That bai   : {len(failed)}  {failed}")
    log("=" * 70)

    if failed:
        log("Chay lai rieng cac job loi:", "WARN")
        log(f"  python train_all.py --mode {args.mode} --jobs {','.join(failed)}",
            "WARN")

    if not args.smoke and not args.no_export and not args.dry_run and done:
        log("")
        log("Xuat training_data.json ...")
        r = subprocess.run([str(CONDA_PYTHON), "export_training_data.py"],
                           cwd=str(PROJECT_DIR))
        if r.returncode == 0:
            log("Da xuat. Nho paste lai toa do pgfplots vao sec6.tex.")
        else:
            log("export_training_data.py loi — chay tay de xem chi tiet", "ERROR")

    return 0 if not failed else 1


if __name__ == "__main__":
    sys.exit(main())
