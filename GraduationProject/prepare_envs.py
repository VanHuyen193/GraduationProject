#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
prepare_envs.py — chuan bi moi truong TRUOC khi chay train_all.py.

Hai viec, deu chay Unity o che do batch nen khong phai mo Editor bang tay:

  1. --areas N   Nhan ban training area cua ca ba scene thanh N ban.
                 Day la don bay toc do lon nhat: moi scene hien chi co DUNG MOT
                 area nen mot buoc mo phong chi sinh mot mau kinh nghiem.
                 CANH BAO: sua truc tiep file .unity. Commit git truoc khi chay.

  2. --build     Build ba file .exe (moi file mot scene) vao Builds/.
                 Co .exe thi mlagents-learn tu khoi chay moi truong qua --env:
                 chay duoc qua dem, khong can bam Play, va dung duoc --num-envs.

Vi du:
    python prepare_envs.py --areas 8 --build      # lam ca hai
    python prepare_envs.py --areas 1              # tra ve 1 area nhu cu
    python prepare_envs.py --build                # chi build lai
"""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent
LOG_DIR = PROJECT_DIR / "training_logs"
BUILD_DIR = PROJECT_DIR / "Builds"

for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

MULTIPLIER = "GraduationProject.EditorTools.TrainingAreaMultiplier.BuildAllFromCommandLine"
BUILDER = "GraduationProject.EditorTools.HeadlessBuilder.BuildAllFromCommandLine"

SCENES = [
    "Assets/CrossTheRoad/Scenes/CrossTheRoad.unity",
    "Assets/Collaboration/Scenes/CaptureTheFlag.unity",
    "Assets/Football/Football.unity",
]


def log(msg: str = "", level: str = "INFO") -> None:
    print(f"{datetime.now():%H:%M:%S} [{level}] {msg}" if msg else "", flush=True)


def find_unity() -> Path | None:
    """Do tim Unity Editor dung phien ban ghi trong ProjectVersion.txt."""
    if os.environ.get("UNITY_EXE"):
        p = Path(os.environ["UNITY_EXE"])
        if p.exists():
            return p

    version = None
    pv = PROJECT_DIR / "ProjectSettings" / "ProjectVersion.txt"
    if pv.exists():
        for line in pv.read_text(encoding="utf-8").splitlines():
            if line.startswith("m_EditorVersion:"):
                version = line.split(":", 1)[1].strip()
                break

    roots = [Path(r"C:\Program Files\Unity\Hub\Editor"),
             Path(r"C:\Program Files (x86)\Unity\Hub\Editor")]
    if version:
        for r in roots:
            exe = r / version / "Editor" / "Unity.exe"
            if exe.exists():
                return exe
    # du phong: ban moi nhat tim duoc
    found = []
    for r in roots:
        if r.exists():
            found += [d / "Editor" / "Unity.exe" for d in r.iterdir()
                      if (d / "Editor" / "Unity.exe").exists()]
    return sorted(found)[-1] if found else None


def run_unity(unity: Path, method: str, extra: list[str], tag: str,
              timeout: int) -> bool:
    LOG_DIR.mkdir(exist_ok=True)
    logfile = LOG_DIR / f"unity_{tag}_{datetime.now():%Y%m%d_%H%M%S}.log"
    cmd = [str(unity), "-batchmode", "-nographics",
           "-projectPath", str(PROJECT_DIR),
           "-executeMethod", method,
           "-logFile", str(logfile)] + extra

    log(f"Chay Unity: {method}")
    log("  " + " ".join(cmd))
    log(f"  log: {logfile}")
    log("  (Unity im lang khi chay batch — cho, dung tuong treo)")

    t0 = time.time()
    try:
        proc = subprocess.run(cmd, timeout=timeout)
        rc = proc.returncode
    except subprocess.TimeoutExpired:
        log(f"Qua {timeout}s — Unity co the dang bi ket. Xem {logfile}", "ERROR")
        return False

    dur = timedelta(seconds=int(time.time() - t0))
    ok = rc == 0
    log(f"--> {'XONG' if ok else f'LOI (exit {rc})'}  ({dur})",
        "INFO" if ok else "ERROR")

    # in cac dong quan trong tu log Unity
    if logfile.exists():
        text = logfile.read_text(encoding="utf-8", errors="replace")
        for line in text.splitlines():
            if any(k in line for k in ("[AreaMultiplier]", "[HeadlessBuilder]")):
                log("  " + line.strip())
        if not ok:
            log("  --- 25 dong cuoi cua log Unity ---", "ERROR")
            for line in text.splitlines()[-25:]:
                log("  " + line.rstrip(), "ERROR")
    return ok


def git_dirty() -> bool:
    try:
        r = subprocess.run(["git", "status", "--porcelain"] + SCENES,
                           cwd=str(PROJECT_DIR.parent), capture_output=True,
                           text=True, timeout=30)
        return bool(r.stdout.strip())
    except Exception:
        return False


def main() -> int:
    p = argparse.ArgumentParser(description="Chuan bi scene va build truoc khi train")
    p.add_argument("--areas", type=int, metavar="N",
                   help="nhan training area cua ca 3 scene thanh N ban (1 = tra ve cu)")
    p.add_argument("--columns", type=int, default=4, help="so cot cua luoi area")
    p.add_argument("--build", action="store_true", help="build 3 file .exe vao Builds/")
    p.add_argument("--yes", action="store_true", help="khong hoi xac nhan")
    p.add_argument("--timeout", type=int, default=3600, help="tran thoi gian moi buoc, giay")
    args = p.parse_args()

    if not args.areas and not args.build:
        p.print_help()
        return 1

    unity = find_unity()
    if unity is None:
        log("Khong tim thay Unity Editor. Dat bien UNITY_EXE tro toi Unity.exe.", "ERROR")
        return 1
    log(f"Unity: {unity}")

    if args.areas and not args.yes:
        log("")
        log("!! Buoc nhan area SUA TRUC TIEP ba file .unity:", "WARN")
        for s in SCENES:
            log(f"     {s}", "WARN")
        if git_dirty():
            log("   Cac scene nay DANG co thay doi chua commit.", "WARN")
        log("   Nen commit git truoc de con quay lai duoc.", "WARN")
        try:
            if input("   Tiep tuc? [y/N] ").strip().lower() not in ("y", "yes"):
                log("Da huy.")
                return 1
        except EOFError:
            log("Khong co stdin — chay lai voi --yes neu chac chan.", "ERROR")
            return 1

    steps_ok = True

    if args.areas:
        log("")
        log("═" * 66)
        log(f"BUOC 1 — nhan training area thanh {args.areas} ban / scene")
        log("═" * 66)
        steps_ok &= run_unity(
            unity, MULTIPLIER,
            ["-areaCount", str(args.areas), "-areaColumns", str(args.columns)],
            "areas", args.timeout)

    if args.build and steps_ok:
        log("")
        log("═" * 66)
        log("BUOC 2 — build 3 moi truong (lan dau co the mat 10-20 phut/env)")
        log("═" * 66)
        steps_ok &= run_unity(unity, BUILDER, [], "build", args.timeout)

        if steps_ok:
            log("")
            log("File da build:")
            for env in ("CrossTheRoad", "CaptureTheFlag", "Football"):
                exe = BUILD_DIR / env / f"{env}.exe"
                mark = "OK " if exe.exists() else "THIEU"
                size = f"{exe.stat().st_size / 1e6:.0f} MB" if exe.exists() else ""
                log(f"  [{mark}] {exe}  {size}")

    log("")
    if steps_ok:
        log("Chuan bi xong. Buoc tiep theo:")
        log("  python train_all.py --smoke            # kiem tra cau hinh ~10 phut")
        log("  python train_all.py --mode build       # chay that")
    else:
        log("Co buoc that bai — doc log Unity o tren truoc khi chay tiep.", "ERROR")
    return 0 if steps_ok else 1


if __name__ == "__main__":
    sys.exit(main())
