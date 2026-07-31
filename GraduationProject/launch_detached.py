#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
launch_detached.py — khoi chay train_all.py TACH ROI HAN khoi console goi no.

Vi sao can: luot huan luyen dai 20+ tieng da bi giet HAI lan giua chung, ca hai
lan deu do console cha dong lai:

  * Lan 1 (Start-Process): tien trinh nam trong cay tien trinh cua phien goi,
    bi ha theo khi phien ket thuc. Log dung giua chung, hai job sau do co log
    RONG vi mlagents-learn con chua kip chay.
  * Lan 2 (WMI Win32_Process.Create + cmd.exe): van gan vao console do, nen khi
    console dong thi CTRL_CLOSE_EVENT lan toi. Log ket thuc bang dung mot ky tu
    '^C' o buoc 1.440.000/1.700.000.

Cach chua: DETACHED_PROCESS (khong co console nao ca) cong CREATE_NEW_PROCESS_GROUP
(khong nhan tin hieu Ctrl-C cua nhom khac). Chay bang python.exe chu KHONG phai
pythonw.exe: pythonw dat sys.stdout = None nen moi loi goi print() trong
train_all.py se no AttributeError. O day stdout duoc noi thang vao file log,
nen print() van chay binh thuong.

Dung:
    python launch_detached.py                       # chay tiep, ngan sach full
    python launch_detached.py --only football       # chi mot moi truong
    python launch_detached.py --base-port 5100 --only football   # luong thu hai

Moi tham so deu duoc chuyen thang cho train_all.py.
"""

from __future__ import annotations

import subprocess
import sys
from datetime import datetime
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent
LOG_DIR = PROJECT_DIR / "training_logs"

DEFAULT_ARGS = ["--mode", "build", "--budget", "full", "--resume", "--force"]


def main() -> int:
    extra = sys.argv[1:]
    args = extra if extra else DEFAULT_ARGS

    LOG_DIR.mkdir(exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_path = LOG_DIR / f"detached_{stamp}.log"

    # Dung cung python dang chay file nay -> luon dung env conda 'mlagents'.
    cmd = [sys.executable, "train_all.py"] + args

    log = open(log_path, "w", encoding="utf-8", buffering=1)
    proc = subprocess.Popen(
        cmd,
        cwd=str(PROJECT_DIR),
        stdout=log,
        stderr=subprocess.STDOUT,
        stdin=subprocess.DEVNULL,
        creationflags=subprocess.DETACHED_PROCESS
        | subprocess.CREATE_NEW_PROCESS_GROUP,
    )

    print(f"PID       : {proc.pid}")
    print(f"Lenh      : {' '.join(cmd)}")
    print(f"Log       : {log_path}")
    print("Tien trinh nay khong gan vao console nao, dong terminal khong giet no.")
    print(f"Theo doi  : Get-Content -Wait '{log_path}'")
    print("Dung han  : Stop-Process -Id " + str(proc.pid))
    return 0


if __name__ == "__main__":
    sys.exit(main())
