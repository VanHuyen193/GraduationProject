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
                 Moi env mat ~20-26 phut (phan lon la chuan bi 36 ti shader
                 variant cua URP/Lit), nen ca ba mat khoang mot tieng.

Vi du:
    python prepare_envs.py --areas 8 --build      # lam ca hai
    python prepare_envs.py --areas 1              # tra ve 1 area nhu cu
    python prepare_envs.py --build                # chi build lai ca ba
    python prepare_envs.py --build --envs Football  # chi build lai mot env
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

# Ten thu muc + file .exe trong Builds/, khop mang Targets trong HeadlessBuilder.cs.
# FootballDiscrete = ban action roi rac cua Football, chi DQN dung.
ALL_ENVS = ["CrossTheRoad", "CaptureTheFlag", "Football", "FootballDiscrete"]


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
        lines = text.splitlines()
        for line in lines:
            if any(k in line for k in ("[AreaMultiplier]", "[HeadlessBuilder]")):
                log("  " + line.strip())

        if not ok:
            # Loi bien dich C# nam GIUA log chu khong phai o cuoi, nen phai loc
            # rieng — neu chi in 25 dong cuoi thi khong bao gio thay.
            compile_errors = [l for l in lines
                              if "error CS" in l or ": error" in l.lower()]
            if compile_errors:
                log("  --- LOI BIEN DICH C# ---", "ERROR")
                for line in compile_errors[:20]:
                    log("  " + line.strip(), "ERROR")
                log("  Sua script trong Assets/Editor/ roi chay lai.", "ERROR")
            else:
                log("  --- 25 dong cuoi cua log Unity ---", "ERROR")
                for line in lines[-25:]:
                    log("  " + line.rstrip(), "ERROR")
    return ok


def unity_is_holding_project() -> bool:
    """
    Unity KHONG mo duoc project dang bi mot instance khac chiem, va o che do
    batch no thoat voi exit code 1 ma khong in ly do — log chi dung o dong
    'Successfully changed project path to: ...'. Bat truoc de bao cho ro.

    Cach kiem tra chac an nhat: Temp/UnityLockfile bi Editor giu mo doc quyen,
    nen mo de ghi se bi PermissionError. (Chi ton tai file thi chua du: file
    con sot lai sau khi Unity crash.)
    """
    lock = PROJECT_DIR / "Temp" / "UnityLockfile"
    if not lock.exists():
        return False
    try:
        with open(lock, "a"):
            return False       # mo duoc -> lockfile mo coi, Unity da dong
    except PermissionError:
        return True
    except OSError:
        return True


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
    p.add_argument("--envs", help="chi build cac env nay, phan cach dau phay "
                                  "(CrossTheRoad,CaptureTheFlag,Football)")
    p.add_argument("--yes", action="store_true", help="khong hoi xac nhan")
    p.add_argument("--timeout", type=int, default=3600,
                   help="tran thoi gian buoc nhan area, giay")
    # Tran thoi gian tinh THEO MOI ENV chu khong phai cho ca lenh build. Ban dau
    # dung chung mot --timeout 3600 cho ca buoc build ba env, nhung ba env mat
    # ~1555+1144+1200 = 3900s nen Unity luon bi giet dung o env cuoi cung.
    p.add_argument("--build-timeout", type=int, default=2400, metavar="SEC",
                   help="tran thoi gian MOI ENV khi build, giay "
                        "(mac dinh 2400; do thuc te 1100-1600s/env)")
    args = p.parse_args()

    envs = ALL_ENVS
    if args.envs:
        envs = [e.strip() for e in args.envs.split(",") if e.strip()]
        unknown = [e for e in envs if e not in ALL_ENVS]
        if unknown:
            log(f"--envs co ten la: {', '.join(unknown)}. "
                f"Hop le: {', '.join(ALL_ENVS)}", "ERROR")
            return 1

    if not args.areas and not args.build:
        p.print_help()
        return 1

    unity = find_unity()
    if unity is None:
        log("Khong tim thay Unity Editor. Dat bien UNITY_EXE tro toi Unity.exe.", "ERROR")
        return 1
    log(f"Unity: {unity}")

    if unity_is_holding_project():
        log("")
        log("PROJECT DANG BI UNITY EDITOR MO — khong chay batch mode duoc.", "ERROR")
        log("Unity khong cho hai instance mo cung mot project; o che do batch no", "ERROR")
        log("thoat luon voi exit code 1 ma khong in ly do gi.", "ERROR")
        log("", "ERROR")
        log("Cach xu ly: DONG hoan toan Unity Editor (ca Unity Hub cang tot),", "ERROR")
        log("doi vai giay cho Temp/UnityLockfile duoc nha ra, roi chay lai lenh nay.", "ERROR")
        return 1

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
        budget = args.build_timeout * len(envs)
        log("")
        log("═" * 66)
        log(f"BUOC 2 — build {len(envs)} moi truong: {', '.join(envs)}")
        log(f"         ~20-26 phut/env, tran thoi gian {budget}s "
            f"({args.build_timeout}s x {len(envs)})")
        log("═" * 66)
        extra = ["-envs", ",".join(envs)] if args.envs else []
        steps_ok &= run_unity(unity, BUILDER, extra, "build", budget)

        # In ca khi that bai: build chay tuan tu nen thuong da xong vai env,
        # biet env nao con thieu thi chay lai duoc dung phan con lai.
        log("")
        log("File da build:")
        missing = []
        for env in ALL_ENVS:
            exe = BUILD_DIR / env / f"{env}.exe"
            if exe.exists():
                size = sum(f.stat().st_size for f in exe.parent.rglob("*")
                           if f.is_file()) / 1e6
                log(f"  [OK   ] {exe}  {size:.0f} MB")
            else:
                log(f"  [THIEU] {exe}")
                missing.append(env)
        if missing:
            log("")
            log(f"Con thieu {len(missing)} env. Build lai DUNG phan con lai:", "WARN")
            log(f"  python prepare_envs.py --build --envs {','.join(missing)}", "WARN")

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
