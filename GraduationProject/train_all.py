#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
train_all.py — dieu phoi toan bo 15 lan huan luyen cho do an.

Thay the train_all_sequential.py (script cu tro sai duong dan conda cua may khac
va con liet ke bo job 3x3 khong con dung voi bao cao).

Luoi day du 5 thuat toan x 3 moi truong = 15 lan chay. Run-id PHAI trung voi
export_training_data.py, dung sua tuy tien:

                     PPO        SAC                  MA-POCA           MAPPO               DQN
    Cross The Road   ctr01      CrossTheRoad_SAC_01  ctr_poca_v1       ctr_mappo_v1        ctr_dqn_v1
    Capture The Flag ctf_ppo_v1 ctf_sac_v1           ctf_poca_v2       ctf_mappo_v2        ctf_dqn_v1
    Football Table   FB01       Football_SAC_01      Football_POCA_01  Football_MAPPO_01   football_dqn_v1

DQN va MAPPO den tu trainer plugin ngoai (ml-agents-trainer-plugin), khong co
san trong ML-Agents — preflight se kiem tra plugin da cai chua.

LUU Y: fb_dqn can mot ban build rieng 'FootballDiscrete'. Xem ACTION_SPACE_CONFLICT.

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

import yaml  # ml-agents phu thuoc pyyaml nen env 'mlagents' luon co san

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
    build: str          # ten thu muc + file .exe trong Builds/
    scene: str          # chi de nhac khi chay --mode editor
    # Ghi chu rui ro: hien len trong buoc kiem tra truoc khi chay.
    risky: str = ""

    def budget(self, profile: str) -> int:
        full, reduced = STEPS[self.env]
        return full if profile == "full" else reduced


# ─────────────────────────────────────────────────────────────────────────────
# Ngan sach buoc — tra theo MOI TRUONG, khong theo tung job.
#
# So buoc phai la thuoc tinh cua moi truong chu khong phai cua job: so sanh nam
# thuat toan chi co nghia khi ca nam chay CUNG mot so buoc tren cung mot moi
# truong. Truoc day moi Job tu khai hai con so rieng nen da troi mat ba cho:
# Football PPO 800K trong khi bon cai kia 450K; CrossTheRoad SAC 1,2M trong khi
# bon cai kia 2,0M; CTF MA-POCA 1,7M trong khi bon cai kia 1,6M. De o day thi
# khong the lech duoc nua.
#
# Cac gia tri deu lay theo huong NANG LEN cho bang cai dai nhat, khong ha xuong
# — ha thi cat mat phan duong cong da co, con nang chi ton them thoi gian chay.
#
# LUU Y: 'full' truoc day duoc ghi la "dung do dai thuc te da bao cao o chuong
# 4". Sau khi can bang thi khong con dung nghia do nua (cac lan chay cu von
# khong bang nhau). Gio 'full' chi con nghia la ngan sach dai.
#
#   * CTF: ghi chu cu o day noi "khong duoc xuong duoi 1,5M vi MAPPO chi giai
#     duoc cau do tu ~1,28M buoc tro di". Do dung voi cac lan chay CU (1 training
#     area). Voi 8 area — cau hinh hien tai — dieu do KHONG con dung:
#         reward tai 60K buoc : PPO 0.791 | MA-POCA 0.466 | MAPPO 0.756
#         reward tai 1,62M    : PPO 0.837 | MA-POCA 0.844 | MAPPO 0.844
#     Ca ba deu vuot curriculum sang Lesson1_Handoff rat som va ve cung mot muc,
#     khong con buoc ngoat nao. Nhan 8 area lam moi lan cap nhat chinh sach nhan
#     kinh nghiem tu 8 moi truong song song, batch da dang hon nen bai toan de
#     hon han tinh theo so buoc.
#     => So lieu moi KHONG ghep duoc voi chuong 4 cu. Da chon huong viet lai
#        ket luan theo bo 8 area (quyet dinh ngay 30/07/2026).
STEPS: dict[str, tuple[int, int]] = {
    #              full        reduced
    "crossroad": (2_000_000, 1_200_000),
    "capture":   (1_700_000, 1_500_000),
    "football":  (1_600_000,   800_000),
}

CTR_SCENE = "Assets/CrossTheRoad/Scenes/CrossTheRoad.unity"
CTF_SCENE = "Assets/Collaboration/Scenes/CaptureTheFlag.unity"
FB_SCENE = "Assets/Football/Football.unity"

JOBS: list[Job] = [
    # ── Cross The Road: chay TRUOC vi nhanh nhat, phat hien loi som ──────────
    Job("ctr_ppo",   "crossroad", "PPO",     "ctr_ppo.yaml",   "ctr01",
        "CrossTheRoad", "CrossTheRoad", CTR_SCENE),
    Job("ctr_sac",   "crossroad", "SAC",     "ctr_sac.yaml",   "CrossTheRoad_SAC_01",
        "CrossTheRoad", "CrossTheRoad", CTR_SCENE,
        risky="Ngan sach cu 200K dua tren lap luan 'SAC hoi tu ~150K', do voi "
              "steps_per_update=1. Nay config da doi sang 20 (nhanh gap 12 lan "
              "nhung ton mau hon) nen 200K khong con du."),
    Job("ctr_poca",  "crossroad", "MA-POCA", "ctr_poca.yaml",  "ctr_poca_v1",
        "CrossTheRoad", "CrossTheRoad", CTR_SCENE),
    Job("ctr_mappo", "crossroad", "MAPPO",   "ctr_mappo.yaml", "ctr_mappo_v1",
        "CrossTheRoad", "CrossTheRoad", CTR_SCENE),
    Job("ctr_dqn",   "crossroad", "DQN",     "ctr_dqn.yaml",   "ctr_dqn_v1",
        "CrossTheRoad", "CrossTheRoad", CTR_SCENE),

    # ── Capture The Flag: co curriculum handoff_required ─────────────────────
    Job("ctf_ppo",   "capture", "PPO",     "ctf_ppo.yaml",   "ctf_ppo_v1",
        "PuzzleBehavior", "CaptureTheFlag", CTF_SCENE),
    Job("ctf_sac",   "capture", "SAC",     "ctf_sac.yaml",   "ctf_sac_v1",
        "PuzzleBehavior", "CaptureTheFlag", CTF_SCENE),
    Job("ctf_poca",  "capture", "MA-POCA", "ctf_poca.yaml",  "ctf_poca_v2",
        "PuzzleBehavior", "CaptureTheFlag", CTF_SCENE),
    Job("ctf_mappo", "capture", "MAPPO",   "ctf_mappo.yaml", "ctf_mappo_v2",
        "PuzzleBehavior", "CaptureTheFlag", CTF_SCENE,
        risky="Voi 8 area, MAPPO khong con the hien buoc ngoat ~1,28M nhu cac lan "
              "chay 1-area cu; ket qua gan nhu trung PPO va MA-POCA. Xem ghi chu "
              "o khoi STEPS."),
    Job("ctf_dqn",   "capture", "DQN",     "ctf_dqn.yaml",   "ctf_dqn_v1",
        "PuzzleBehavior", "CaptureTheFlag", CTF_SCENE),

    # ── Football Table: self-play, nang nhat, chay cuoi ──────────────────────
    Job("fb_ppo",    "football", "PPO",     "football_ppo.yaml",  "FB01",
        "Football", "Football", FB_SCENE),
    Job("fb_sac",    "football", "SAC",     "football_sac.yaml",  "Football_SAC_01",
        "Football", "Football", FB_SCENE,
        risky="SAC + self_play: ML-Agents khong ho tro chinh thuc. Da chay duoc "
              "20K buoc trong smoke test nen khong chan, nhung theo doi ky."),
    Job("fb_poca",   "football", "MA-POCA", "football_poca.yaml", "Football_POCA_01",
        "Football", "Football", FB_SCENE),
    Job("fb_mappo",  "football", "MAPPO",   "football_mappo.yaml", "Football_MAPPO_01",
        "Football", "Football", FB_SCENE),
    # Football + DQN can BAN BUILD RIENG. Xem ghi chu ACTION_SPACE_CONFLICT duoi.
    Job("fb_dqn",    "football", "DQN",     "football_dqn.yaml",  "football_dqn_v1",
        "Football", "FootballDiscrete", FB_SCENE,
        risky="CAN BUILD RIENG 'FootballDiscrete'. Football dang la continuous(8) "
              "nhung DQN chi chay duoc action roi rac, nen phai co mot ban scene "
              "voi Behavior Parameters doi sang 8 nhanh x 3 muc. Khong dung chung "
              "build 'Football' voi PPO/SAC/POCA/MAPPO duoc."),
]

# ACTION_SPACE_CONFLICT
# --------------------
# Bon thuat toan PPO/SAC/MA-POCA/MAPPO tren Football dung continuous(8);
# DQN bat buoc discrete. Hai thu nay khong the o chung mot file .exe vi
# Behavior Parameters duoc nuong vao build. Cach lam:
#   1. Nhan ban Football.unity thanh FootballDiscrete.unity, sua Behavior
#      Parameters cua CA HAI agent: Continuous Actions 8 -> 0,
#      Discrete Branches 0 -> 8, moi branch size 3.
#      (FootballAgent.OnActionReceived da co san che do roi rac — xem
#       config/HUONG_DAN_DQN.md muc 3.)
#   2. Them scene do vao mang Targets trong Assets/Editor/HeadlessBuilder.cs
#      voi Exe = "FootballDiscrete".
#   3. python prepare_envs.py --build --envs FootballDiscrete
# Truoc khi lam xong buoc do, chay fb_dqn se bi preflight chan vi thieu build.

ENV_ORDER = ["crossroad", "capture", "football"]


def _check_grid() -> None:
    """
    Lưới phải là ĐỦ 5 thuật toán x 3 môi trường, khong thua khong thieu.

    STEPS da bao dam moi job trong cung mot moi truong co cung so buoc, nhung
    khong bao dam duoc la co du ca nam thuat toan — them nham hai job MAPPO hay
    quen mot job DQN thi bang so sanh thung mot o ma khong ai biet cho toi luc
    ve bieu do. Kiem o day de hong la hong ngay luc import.
    """
    expected = {"PPO", "SAC", "MA-POCA", "MAPPO", "DQN"}
    for env in ENV_ORDER:
        got = [j.algo for j in JOBS if j.env == env]
        if sorted(got) != sorted(expected):
            raise AssertionError(
                f"JOBS: moi truong '{env}' co {sorted(got)}, can {sorted(expected)}")
        if env not in STEPS:
            raise AssertionError(f"STEPS thieu moi truong '{env}'")
    if len(JOBS) != len(ENV_ORDER) * len(expected):
        raise AssertionError(f"JOBS co {len(JOBS)} muc, can {len(ENV_ORDER) * 5}")
    if len({j.run_id for j in JOBS}) != len(JOBS):
        raise AssertionError("JOBS: co run_id bi trung — se ghi de len nhau")


_check_grid()

# Ten nguoi dung go cho --algo -> gia tri trong Job.algo.
# Khong tu chuan hoa chuoi duoc: bo gach noi khoi 'MA-POCA' ra 'mapoca', khong
# bang 'poca' ma nguoi dung se go; con kiem tra chuoi con thi 'poca' lai dinh
# luon 'MAPPO'. Liet ke tuong minh la cach duy nhat khong nhap nhang.
ALGO_ALIASES = {
    "ppo": "PPO",
    "sac": "SAC",
    "poca": "MA-POCA", "mapoca": "MA-POCA", "ma-poca": "MA-POCA",
    "mappo": "MAPPO",
    "dqn": "DQN",
}


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


def run_is_complete(job: Job) -> bool:
    """
    Job da chay XONG chua — khac han voi 'da chay chua'.

    ML-Agents chi ghi results/<run-id>/<behavior>.onnx khi ket thuc binh thuong.
    Trong luc dang chay thi chi co <behavior>/<behavior>-<step>.onnx (checkpoint
    moi 500K buoc) va tfevents.

    Truoc day ham nay kiem tra su ton tai cua TFEVENTS. Nhung tfevents xuat hien
    ngay tu moc summary dau tien (10K buoc), nen mot job bi ngat giua chung — mat
    dien, tat may, Ctrl-C — van bi coi la 'da xong'. Chay lai voi --resume se BO
    QUA no, de lai mot lan chay cut ngun trong bang so sanh ma khong he bao gi.
    Voi lan chay 25 tieng thi day la kieu hong dat nhat: phat hien ra luc ve bieu
    do, va phai chay lai tu dau.
    """
    return (RESULTS_DIR / job.run_id / f"{job.behavior}.onnx").exists()


def run_dir_exists(job: Job) -> bool:
    """
    Thu muc results/<run-id> co ton tai khong — KHAC voi run_is_complete().

    mlagents-learn chan bang os.path.isdir(output_path) (directory_utils.py:21),
    tuc la chi can THU MUC ton tai la no nem UnityTrainerException va thoat ngay,
    khong quan tam ben trong co tfevents hay khong. Cac thu muc chi con file .pt
    (tfevents da bi xoa) van du de lam job chet, trong khi run_is_complete() bao
    la "chua co gi" — nen phai kiem tra rieng.
    """
    return (RESULTS_DIR / job.run_id).is_dir()


# ─────────────────────────────────────────────────────────────────────────────
# Kiem tra moi truong truoc khi chay
# ─────────────────────────────────────────────────────────────────────────────
def preflight(jobs: list[Job], args) -> bool:
    ok = True
    mode = args.mode
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
        # Chi doi hoi plugin ma bo job dang chay thuc su can.
        need = {"mappo", "dqn"} & {j.algo.lower() for j in jobs}
        missing = sorted(n for n in need if n not in plugins)
        if missing:
            log(f"Thieu plugin {', '.join(missing)}. Cai bang:", "ERROR")
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

    # Trung run-id: day la LOI, khong phai canh bao. mlagents-learn thoat ngay
    # lap tuc neu results/<run-id> da ton tai ma khong co --force, nen job se
    # chet trong vai giay chu khong phai chay duoc mot phan.
    clash = [j for j in jobs if run_dir_exists(j)]
    if clash and not args.force:
        log("", "ERROR")
        log(f"{len(clash)} run-id DA co thu muc trong results/ — mlagents-learn "
            f"se tu choi chay:", "ERROR")
        for j in clash:
            n = len(list((RESULTS_DIR / j.run_id).rglob("*.pt")))
            log(f"    [{j.id}] results/{j.run_id}  ({n} checkpoint .pt)", "ERROR")
        log("Chon mot trong hai:", "ERROR")
        log("  a) them --force  (ghi de, XOA checkpoint .pt cu trong cac thu muc tren)",
            "ERROR")
        log("  b) doi cho cac thu muc do sang results_old/ de giu lai", "ERROR")
        ok = False
    elif clash:
        log(f"--force: se GHI DE {len(clash)} thu muc run-id da co "
            f"({', '.join(j.run_id for j in clash)})", "WARN")

    log(f"Ket qua kiem tra: {'OK' if ok else 'CO LOI'}")
    log("─" * 70)
    return ok


# ─────────────────────────────────────────────────────────────────────────────
# Chay mot job
# ─────────────────────────────────────────────────────────────────────────────
STEP_RE = re.compile(r"Step:\s*([\d,]+)\.\s*Time Elapsed:\s*([\d.]+)")


TMP_CONFIG_DIR = LOG_DIR / "_config_override"


def config_with_steps(job: Job, steps: int) -> Path:
    """
    Sinh mot ban YAML tam voi max_steps da doi, tra ve duong dan ban do.

    mlagents-learn KHONG co tham so dong lenh --max-steps (chay
    `mlagents-learn --help` de kiem chung): max_steps la thiet lap trong YAML,
    nam o behaviors.<ten hanh vi>.max_steps. Ban dau build_cmd() truyen thang
    "--max-steps <n>" nen argparse cua mlagents-learn tu choi va MOI job chet
    sau mot giay — nghia la --smoke va --override-steps chua bao gio chay duoc.
    File config goc khong bi dong den; ban tam nam trong training_logs/.
    """
    src = CONFIG_DIR / job.config
    cfg = yaml.safe_load(src.read_text(encoding="utf-8"))

    behaviors = (cfg or {}).get("behaviors") or {}
    if not behaviors:
        raise ValueError(f"{src.name}: khong tim thay khoa 'behaviors'")
    for spec in behaviors.values():
        spec["max_steps"] = steps
        # summary_freq phai nho hon max_steps, khong thi tfevents khong co diem
        # nao va viec kiem tra ket qua bao that bai du training chay tot. Vap o
        # ctf_*.yaml: summary_freq 20000 dung bang ngan sach smoke 20000.
        # Chi ha xuong khi can — ngan sach that (>=1,2M) giu nguyen 10000.
        spec["summary_freq"] = min(int(spec.get("summary_freq", 10_000)),
                                   max(1_000, steps // 4))

    TMP_CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    out = TMP_CONFIG_DIR / f"{job.run_id}_{steps}.yaml"
    out.write_text(
        f"# Sinh tu {job.config} boi train_all.py — max_steps={steps:,}. Dung sua tay.\n"
        + yaml.safe_dump(cfg, sort_keys=False, allow_unicode=True),
        encoding="utf-8")
    return out


def build_cmd(job: Job, args, steps: int) -> list[str]:
    cfg = config_with_steps(job, steps) if args.override_steps \
        else CONFIG_DIR / job.config
    cmd = [str(MLAGENTS_LEARN), str(cfg),
           "--run-id", job.run_id,
           "--results-dir", str(RESULTS_DIR)]

    # Job do dang: co thu muc nhung chua co ONNX cuoi — tuc la lan truoc bi ngat
    # giua chung (mat dien, tat may, Ctrl-C). Truyen --resume cua mlagents de
    # chay TIEP tu checkpoint gan nhat thay vi --force lam lai tu buoc 0.
    # Checkpoint duoc ghi moi 500K buoc, nen voi job 5 tieng nhu ctf_sac thi day
    # la khac biet giua mat vai chuc phut va mat ca buoi.
    # Chi lam khi nguoi dung da yeu cau --resume; khong thi giu nguyen --force.
    # Phai co checkpoint that su thi --resume moi co nghia. Checkpoint chi duoc
    # ghi moi 500K buoc, nen mot job chet o buoc 310K co thu muc + tfevents ma
    # KHONG co checkpoint.pt nao — truyen --resume vao do thi mlagents khong co
    # gi de nap va bao loi. Truong hop do phai chay lai tu dau bang --force.
    ckpt = (RESULTS_DIR / job.run_id / job.behavior / "checkpoint.pt").exists()
    if args.resume and ckpt and not run_is_complete(job):
        cmd.append("--resume")
    elif args.force:
        cmd.append("--force")
    if args.mode == "build":
        cmd += ["--env", str(BUILD_DIR / job.build / f"{job.build}.exe"),
                "--no-graphics"]
        if args.num_envs > 1:
            cmd += ["--num-envs", str(args.num_envs),
                    "--base-port", str(args.base_port)]
    cmd += ["--time-scale", str(args.time_scale)]
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
    # Moc bat dau THUC TE cua lan chay nay. Khi --resume, mlagents bao cao tu
    # buoc cua checkpoint (vi du 1.000.000) chu khong tu 0; lay tong buoc chia
    # thoi gian ke tu luc khoi dong lai se ra nhip vo nghia — da thay
    # "67640 step/s, ETA 0:00:10" cho mot job con hon hai tieng nua moi xong.
    base_step: int | None = None
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
                    if base_step is None:
                        base_step = last_step
                    el = time.time() - t0
                    done_now = last_step - base_step
                    sps = done_now / el if el > 0 and done_now > 0 else 0
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
    ok = proc.returncode == 0 and run_is_complete(job)
    log(f"--> {'XONG' if ok else 'THAT BAI'}  ({hms(dur)}, "
        f"{last_step:,} steps, log: {logf.name})",
        "INFO" if ok else "ERROR")
    if not ok:
        log(f"    xem chi tiet: {logf}", "ERROR")
    return ok, dur, last_step


# ─────────────────────────────────────────────────────────────────────────────
def main() -> int:
    p = argparse.ArgumentParser(description="Dieu phoi 15 lan huan luyen "
                                            "(5 thuat toan x 3 moi truong)")
    p.add_argument("--mode", choices=["build", "editor"], default="build",
                   help="build = tu dong bang file .exe (khuyen nghi); "
                        "editor = cho bam Play thu cong")
    p.add_argument("--only", choices=ENV_ORDER, help="chi chay mot moi truong")
    p.add_argument("--algo", help="chi chay mot thuat toan tren ca 3 moi truong "
                                  "(ppo | sac | poca | mappo | dqn)")
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
    # MAC DINH BAT. Truoc day day la co phai tu bat (--override-steps), nen chay
    # 'train_all.py --budget full' ma quen no thi ngan sach trong STEPS bi bo qua
    # hoan toan va trainer doc max_steps tho trong YAML — ma cac file YAML dang de
    # 2M/5M/10M, tuc la lech nhau, dung thu ma viec can bang vua roi phai chua.
    # Hong kieu do khong bao gio bao loi, chi lang le cho ra bo so sanh khong dung.
    p.add_argument("--use-yaml-steps", dest="override_steps", action="store_false",
                   help="KHONG ghi de max_steps; dung nguyen so trong file config "
                        "(bo qua STEPS — chi dung khi co chu dich)")
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
    if args.algo:
        want = ALGO_ALIASES.get(args.algo.strip().lower())
        if want is None:
            log(f"--algo '{args.algo}' khong hop le. Dung mot trong: "
                f"{', '.join(sorted(set(ALGO_ALIASES)))}", "ERROR")
            return 1
        jobs = [j for j in jobs if j.algo == want]
    if args.jobs:
        # GIU DUNG THU TU nguoi dung go. Truoc day dung set roi loc theo JOBS nen
        # thu tu goc luon thang — '--jobs fb_poca,ctf_dqn' van chay ctf_dqn truoc.
        # Can thu tu that de xep job ngan chay truoc, thay vi de mot job 6 tieng
        # chan ca hang doi.
        want = [s.strip() for s in args.jobs.split(",") if s.strip()]
        by_id = {j.id: j for j in jobs}
        unknown = [w for w in want if w not in by_id]
        if unknown:
            log(f"--jobs co id la: {', '.join(unknown)}. Hop le: "
                f"{', '.join(j.id for j in JOBS)}", "ERROR")
            return 1
        jobs = [by_id[w] for w in want]
    if args.skip:
        drop = {s.strip() for s in args.skip.split(",")}
        jobs = [j for j in jobs if j.id not in drop]
    if not jobs:
        log("Khong co job nao khop bo loc", "ERROR")
        return 1

    st = load_status()
    if args.resume:
        before = len(jobs)
        jobs = [j for j in jobs if not run_is_complete(j)]
        log(f"--resume: bo qua {before - len(jobs)} job da co ket qua")
        if not jobs:
            log("Tat ca job da xong.")
            return 0

    if not preflight(jobs, args) and not args.dry_run:
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
        # --dry-run KHONG duoc ghi trang thai. run_job() tra ve ok=True ma khong
        # chay gi, nen mot lan dry-run se danh dau ca 15 job la "ok, 0 buoc" —
        # file trang thai tu do noi doi ve nhung job chua he chay.
        if not args.dry_run:
            st[job.id] = {
                "run_id": job.run_id, "ok": ok, "seconds": round(dur, 1),
                "steps": steps_done,
                "at": datetime.now().isoformat(timespec="seconds"),
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
