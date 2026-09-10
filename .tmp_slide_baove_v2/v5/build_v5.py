# -*- coding: utf-8 -*-
"""Dựng lại bộ slide bảo vệ đồ án theo khung 17 slide, giữ nguyên template Phenikaa."""
import copy
import json
import os
import sys

from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE
from pptx.chart.data import CategoryChartData, XyChartData
from pptx.chart.axis import ValueAxis
from pptx.enum.chart import XL_CHART_TYPE, XL_LEGEND_POSITION, XL_LABEL_POSITION

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from deckkit import *  # noqa

ROOT = os.path.dirname(os.path.abspath(__file__))
SRC = r"C:\Users\Admin\Downloads\DoAn\Slide_BaoVe_DoAnTotNghiep_v4.pptx"
OUT = os.path.join(ROOT, "Slide_BaoVe_DoAnTotNghiep_v5.pptx")
IMG = r"C:\Users\Admin\Documents\GitHub\GraduationProject\Đồ_án_tốt_nghiệp\image\app"

RID = "{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id"

ALG_COLOR = {
    "PPO": RGBColor(0x2E, 0x86, 0xC1), "SAC": RGBColor(0x27, 0x92, 0x4F),
    "MA-POCA": RGBColor(0xE0, 0x7B, 0x18), "MAPPO": RGBColor(0x7D, 0x3C, 0x98),
    "DQN": RGBColor(0xC0, 0x39, 0x2B),
}
ALGS = ["PPO", "SAC", "MA-POCA", "MAPPO", "DQN"]


def alg_color(name):
    return ALG_COLOR.get(name.split(" ")[0], NAVY)


# ------------------------------- đường cong huấn luyện trích từ TensorBoard ---
# Ánh xạ thư mục kết quả → (môi trường, thuật toán). Mỗi giá trị phần thưởng
# trung bình 10% cuối của các bản chạy này khớp đúng bảng ở Chương 4.
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
with open(os.path.join(ROOT, "curves.json"), encoding="utf-8") as fh:
    CURVES = json.load(fh)


def series_for(env, metric="reward", scale=1000.0, max_pts=110, smooth=1):
    """Trả về [(tên thuật toán, [(triệu bước, giá trị × scale)])] cho một môi trường.

    smooth > 1 lấy trung bình trượt trên số điểm tương ứng; mặc định giữ số liệu thô.
    """
    out = []
    for alg in ALGS:
        pts = CURVES[RUNS[env][alg]][metric]
        if not pts:
            continue
        if smooth > 1:
            half = smooth // 2
            pts = [(s, sum(v for _, v in pts[max(0, i - half):i + half + 1])
                    / len(pts[max(0, i - half):i + half + 1]))
                   for i, (s, _) in enumerate(pts)]
        step = max(1, len(pts) // max_pts)
        thin = pts[::step]
        if thin[-1] != pts[-1]:
            thin.append(pts[-1])
        out.append((alg, [(s / 1e6, v * scale) for s, v in thin]))
    return out


def line_chart(slide, x, y, w, h, series, ymin, ymax, yunit, xmax, xunit,
               xtitle, ytitle, numfmt='0","000', legend=True):
    """Biểu đồ đường theo số bước huấn luyện, dựng bằng chart gốc của PowerPoint."""
    cd = XyChartData()
    for name, pts in series:
        sr = cd.add_series(name)
        for px, py in pts:
            sr.add_data_point(px, py)
    gf = slide.shapes.add_chart(XL_CHART_TYPE.XY_SCATTER_LINES_NO_MARKERS,
                                Inches(x), Inches(y), Inches(w), Inches(h), cd)
    ch = gf.chart
    ch.has_title = False
    ch.has_legend = legend
    if legend:
        ch.legend.position = XL_LEGEND_POSITION.TOP
        ch.legend.include_in_layout = False
        ch.legend.font.size = Pt(10.5)
        ch.legend.font.name = FONT
        ch.legend.font.color.rgb = INK
    for sr in ch.series:
        sr.format.line.color.rgb = alg_color(sr.name)
        sr.format.line.width = Pt(1.75)
        sr.smooth = False

    ax = ch._chartSpace.valAx_lst
    xax, yax = ValueAxis(ax[0]), ValueAxis(ax[1])
    for a, (lo, hi, unit, fmt, ttl) in zip(
            (xax, yax),
            ((0, xmax, xunit, "0.0", xtitle), (ymin, ymax, yunit, numfmt, ytitle))):
        a.minimum_scale, a.maximum_scale, a.major_unit = lo, hi, unit
        a.tick_labels.number_format = fmt
        a.tick_labels.number_format_is_linked = False
        a.tick_labels.font.size = Pt(9.5)
        a.tick_labels.font.name = FONT
        a.tick_labels.font.color.rgb = MUTED
        a.format.line.color.rgb = LINE
        a.has_title = True
        a.axis_title.text_frame.text = ttl
        r = a.axis_title.text_frame.paragraphs[0].runs[0]
        r.font.size = Pt(9.5)
        r.font.bold = False
        r.font.name = FONT
        r.font.color.rgb = MUTED
    xax.has_major_gridlines = False
    yax.has_major_gridlines = True
    yax.major_gridlines.format.line.color.rgb = ICE
    yax.major_gridlines.format.line.width = Pt(0.75)
    return ch


# --------------------------------------------------------------------- khởi tạo
prs = Presentation(SRC)

# xoá toàn bộ slide cũ, giữ nguyên master / layout / theme / thương hiệu
sldIdLst = prs.slides._sldIdLst
for sldId in list(sldIdLst):
    prs.part.drop_rel(sldId.get(RID))
    sldIdLst.remove(sldId)

master = prs.slide_masters[0]
LAY = {l.name: l for l in master.slide_layouts}
LAY_TITLE = LAY["Title Slide"]
LAY_BODY = LAY["1_Title and Content"]

OVERFLOW = []


def new_slide_t(t, tsz=26, tw=9.90):
    s = prs.slides.add_slide(LAY_BODY)
    for ph in list(s.placeholders):
        ph._element.getparent().remove(ph._element)
    w = text_w(t, tsz, bold=True)
    while w > tw and tsz > 19.5:
        tsz -= 0.5
        w = text_w(t, tsz, bold=True)
    title(s, t, sz=tsz, w=tw)
    return s


def blank_title_slide():
    s = prs.slides.add_slide(LAY_TITLE)
    for ph in list(s.placeholders):
        ph._element.getparent().remove(ph._element)
    return s


def check(name, box_h, need_h):
    if need_h > box_h + 0.005:
        OVERFLOW.append(f"{name}: cần {need_h:.2f}in > khung {box_h:.2f}in")


# ============================================================== 1. TRANG BÌA ===
s = blank_title_slide()
simple(s, 1.00, 2.42, 11.33, 0.32,
       "ĐỒ ÁN TỐT NGHIỆP ĐẠI HỌC  •  NGÀNH KHOA HỌC MÁY TÍNH",
       sz=13, b=True, c=RGBColor(0xF2, 0x9F, 0x5B), align="c", wrap=False)
textbox(s, 1.00, 2.78, 11.33, 1.16, [
    {"runs": [("HỌC TĂNG CƯỜNG ĐỂ TỐI ƯU HÓA KHẢ NĂNG", {"sz": 30, "b": True, "c": WHITE})],
     "align": "c", "line": 1.12},
    {"runs": [("TƯƠNG TÁC CỦA AI TRONG GAME", {"sz": 30, "b": True, "c": WHITE})],
     "align": "c", "line": 1.12},
], anchor="t")
simple(s, 1.60, 3.94, 10.13, 0.38,
       "Đồ án tập trung vào xây dựng và kiểm chứng môi trường học tăng cường cho game 3D.",
       sz=14, i=True, c=RGBColor(0xCF, 0xD8, 0xEC), align="c", wrap=False)

_env = [("env_football.png", "Football Table"),
        ("env_puzzle.png", "Capture The Flag"),
        ("env_crossroad.png", "Cross The Road")]
_w, _gap = 2.66, 0.30
_x0 = (SLIDE_W - (3 * _w + 2 * _gap)) / 2
for i, (fn, lab) in enumerate(_env):
    x = _x0 + i * (_w + _gap)
    picture_plate(s, x, 4.38, _w, 1.62, os.path.join(IMG, fn), pad=0.08)
    simple(s, x, 6.04, _w, 0.26, lab, sz=11, b=True,
           c=RGBColor(0xCF, 0xD8, 0xEC), align="c", wrap=False)

textbox(s, 1.00, 6.36, 11.33, 0.70, [
    {"runs": [("Sinh viên thực hiện: ", {"sz": 14, "c": RGBColor(0xCF, 0xD8, 0xEC)}),
              ("Văn Thị Minh Huyền", {"sz": 14, "b": True, "c": WHITE}),
              ("   ·   MSSV: ", {"sz": 14, "c": RGBColor(0xCF, 0xD8, 0xEC)}),
              ("22010329", {"sz": 14, "b": True, "c": WHITE}),
              ("   ·   Khóa: ", {"sz": 14, "c": RGBColor(0xCF, 0xD8, 0xEC)}),
              ("K16", {"sz": 14, "b": True, "c": WHITE})],
     "align": "c", "line": 1.15, "space_after": 3},
    {"runs": [("Giảng viên hướng dẫn: ", {"sz": 14, "c": RGBColor(0xCF, 0xD8, 0xEC)}),
              ("ThS. Nguyễn Văn Sơn", {"sz": 14, "b": True, "c": WHITE})],
     "align": "c", "line": 1.15},
], anchor="t")
notes(s, "Kính chào hội đồng. Em là Văn Thị Minh Huyền, lớp K16 ngành Khoa học máy tính. "
         "Đồ án của em tập trung vào xây dựng và kiểm chứng môi trường học tăng cường cho game 3D "
         "trên Unity ML-Agents. Ba ảnh phía dưới là ba môi trường em đã dựng: Football Table, "
         "Capture The Flag và Cross The Road.")

# ======================================================= 2. BỐI CẢNH & VẤN ĐỀ ==
s = new_slide_t("Bối cảnh — phần khó không nằm ở thuật toán")
chip(s, 0.55, 1.16, "Vì sao khâu xây dựng môi trường mới là phần khó thật sự")

L_X, L_W = 0.55, 6.30
_cards = [
    ("Thuật toán là tài sản dùng chung",
     "PPO, SAC và MA-POCA có sẵn trong ML-Agents. Đổi thuật toán chỉ là sửa một tệp YAML, "
     "và đổi bài toán vẫn dùng lại được gần như nguyên vẹn."),
    ("Môi trường là tài sản riêng",
     "Mỗi môi trường mẫu được đặc tả cho đúng bài toán của người viết ra nó. Đổi cơ chế game "
     "thì quan sát, hành động và phần thưởng gần như không kế thừa được gì."),
    ("Đặc tả sai không báo lỗi",
     "Chương trình vẫn chạy, đường cong vẫn được vẽ ra. Tác nhân chỉ đơn giản là học một hành vi "
     "khác với hành vi ta muốn — và không có thông báo nào cho biết điều đó."),
]
_y = 1.76
for h, b in _cards:
    need = card_text(s, L_X, _y, L_W, 1.62, h, b, hsz=16, bsz=14)
    check(f"S2 card {h}", 1.26, need)
    _y += 1.72

R_X, R_W = 7.15, 5.65
card(s, R_X, 1.76, R_W, 3.72)
simple(s, R_X + 0.24, 1.92, R_W - 0.48, 0.32, "VÒNG LẶP HỌC TĂNG CƯỜNG",
       sz=12.5, b=True, c=ORANGE, align="c", wrap=False)

_bx, _bw, _bh = R_X + 1.05, 3.55, 0.62
_boxes = [("TÁC NHÂN", "mạng chính sách π(a|s)", 2.36),
          ("MÔI TRƯỜNG UNITY", "cơ chế game · vật lý · va chạm", 3.42),
          ("HÀM PHẦN THƯỞNG", "tín hiệu duy nhất định nghĩa mục tiêu", 4.48)]
for i, (h, sub, by) in enumerate(_boxes):
    fill = NAVY if i == 2 else WHITE
    ln = None if i == 2 else NAVY
    round_rect(s, _bx, by, _bw, _bh, fill=fill, line=ln, lw=1.0, adj=0.12)
    textbox(s, _bx + 0.10, by + 0.06, _bw - 0.20, _bh - 0.12, [
        {"runs": [(h, {"sz": 12.5, "b": True, "c": WHITE if i == 2 else NAVY})],
         "align": "c", "line": 1.0, "space_after": 1},
        {"runs": [(sub, {"sz": 10.5, "c": ICE if i == 2 else MUTED})],
         "align": "c", "line": 1.0}], anchor="c")
    if i < 2:
        arrow(s, _bx + _bw / 2 - 0.10, by + _bh + 0.06, 0.20, 0.32,
              MSO_SHAPE.DOWN_ARROW)
simple(s, _bx + _bw / 2 + 0.16, 3.02, 1.60, 0.22, "hành động aₜ", sz=10, i=True,
       c=MUTED, wrap=False)
simple(s, _bx + _bw / 2 + 0.16, 4.08, 1.90, 0.22, "trạng thái sₜ₊₁", sz=10, i=True,
       c=MUTED, wrap=False)

# nhánh phản hồi chạy vòng bên trái
_rail = RGBColor(0xB4, 0xBE, 0xD6)
rect(s, R_X + 0.42, 2.65, 0.05, 2.17, fill=_rail)
rect(s, R_X + 0.42, 4.77, 0.63, 0.05, fill=_rail)
rect(s, R_X + 0.42, 2.65, 0.45, 0.05, fill=_rail)
arrow(s, R_X + 0.85, 2.53, 0.24, 0.28, MSO_SHAPE.RIGHT_ARROW)
simple(s, R_X + 0.24, 5.16, R_W - 0.48, 0.28,
       "quan sát sₜ₊₁ và phần thưởng rₜ₊₁ quay lại tác nhân",
       sz=10.5, i=True, c=MUTED, align="c", wrap=False)

callout(s, R_X, 5.62, R_W, 1.28)
_, need = head_body(s, R_X + 0.26, 5.62, R_W - 0.52,
                    "Đo trên chính đồ án này",
                    "Thiết kế ba môi trường: hơn 30 trang.  ·  Cấu hình cả năm thuật toán: "
                    "3 trang tệp YAML. Đó cũng là tỉ lệ công sức mà một dự án học tăng cường "
                    "thực tế phải trả.", hsz=15, bsz=13.5, hcolor=ORANGE,
                    h=1.28, anchor="c")
check("S2 callout", 1.10, need)
notes(s, "Thuật toán học tăng cường ngày nay đã được đóng gói sẵn trong thư viện: chọn PPO hay SAC "
         "chỉ là sửa một tệp cấu hình. Phần khó nằm ở chỗ khác — đặc tả môi trường. Quan sát nào, "
         "hành động nào, phần thưởng bao nhiêu, cơ chế game vận hành ra sao. Và điều nguy hiểm nhất: "
         "một môi trường đặc tả sai không hề báo lỗi. Chương trình vẫn chạy, đường cong vẫn được vẽ, "
         "nhưng tác nhân đang học sai. Trên chính đồ án này, phần thiết kế ba môi trường chiếm hơn 30 "
         "trang, còn cấu hình cả năm thuật toán chỉ 3 trang YAML.")

# ==================================================== 3. MỤC TIÊU & ĐÓNG GÓP ===
s = new_slide_t("Mục tiêu và đóng góp")
chip(s, 0.55, 1.16, "Bốn mục tiêu, đo được bằng sản phẩm bàn giao")

_goals = [
    ("1", "Xây dựng ba môi trường Unity ML-Agents",
     "Ba dạng bài toán khác nhau: đối kháng, hợp tác và điều hướng đơn tác nhân."),
    ("2", "Kiểm chứng bằng năm thuật toán",
     "PPO, SAC, MA-POCA, MAPPO và DQN đóng vai phép thử độc lập cho từng môi trường."),
    ("3", "Đóng gói để dùng lại được",
     "Gói Unity Package Manager kèm 15 cấu hình đã chạy thật và bộ công cụ Editor."),
    ("4", "Xây ứng dụng demo trực quan",
     "Nạp 15 mô hình ONNX tại thời gian chạy, ba chế độ chơi và hai tab số liệu."),
]
for i, (n, h, b) in enumerate(_goals):
    x = 0.55 + (i % 2) * 6.33
    y = 1.76 + (i // 2) * 2.16
    card(s, x, y, 5.92, 1.96)
    oval(s, x + 0.28, y + 0.76, 0.44, fill=ORANGE, label=n, sz=15)
    _, need = head_body(s, x + 0.90, y + 0.20, 4.74, h, b, hsz=16.5, bsz=14.5,
                        h=1.56, anchor="c")
    check(f"S3 goal {n}", 1.56, need)

callout(s, 0.55, 6.14, 12.25, 0.88)
textbox(s, 0.80, 6.14, 11.75, 0.88, [
    {"runs": [("Phạm vi:  ", {"sz": 14, "b": True, "c": ORANGE}),
              ("ba môi trường Unity 3D, năm thuật toán đóng vai phép thử. ", {"sz": 14}),
              ("Không bao gồm:  ", {"sz": 14, "b": True, "c": ORANGE}),
              ("đồ họa, âm thanh hay một sản phẩm game thương mại — đồ án cũng không đề xuất "
               "thuật toán mới.", {"sz": 14})], "line": 1.10}], anchor="c")
notes(s, "Đồ án đặt ra bốn mục tiêu, mỗi mục tiêu gắn với một sản phẩm bàn giao cụ thể chứ không "
         "dừng ở mô tả. Ba môi trường, mười lăm lần huấn luyện, một gói cài đặt lại được, và một "
         "ứng dụng demo. Xin nhấn mạnh phạm vi: năm thuật toán ở đây là phép thử để dò đặc tính "
         "môi trường, đồ án không đề xuất thuật toán mới.")

# ======================================================= 4. KIẾN TRÚC TỔNG THỂ =
s = new_slide_t("Kiến trúc tổng thể — một đường ống đo duy nhất")
chip(s, 0.55, 1.16, "Từ cơ chế game tới mô hình chạy được trong ứng dụng")

_stages = [
    ("MÔI TRƯỜNG UNITY", "quan sát · hành động · reward"),
    ("ML-AGENTS TRAINER", "năm thuật toán phép thử"),
    ("TENSORBOARD", "reward · entropy · độ dài"),
    ("XUẤT ONNX", "15 mô hình đã huấn luyện"),
    ("ỨNG DỤNG DEMO", "ba chế độ · hai tab số liệu"),
]
_sw, _sgap = 2.21, 0.29
_sx = 0.55
for i, (h, b) in enumerate(_stages):
    x = _sx + i * (_sw + _sgap)
    fill = NAVY if i in (0, 4) else CARD
    round_rect(s, x, 1.80, _sw, 1.46, fill=fill, adj=0.09)
    textbox(s, x + 0.10, 1.92, _sw - 0.20, 1.22, [
        {"runs": [(h, {"sz": 13, "b": True, "c": WHITE if i in (0, 4) else NAVY})],
         "align": "c", "line": 1.02, "space_after": 5},
        {"runs": [(b, {"sz": 11, "c": ICE if i in (0, 4) else MUTED})],
         "align": "c", "line": 1.02}], anchor="c")
    if i < 4:
        arrow(s, x + _sw + 0.03, 2.39, 0.23, 0.28, MSO_SHAPE.RIGHT_ARROW)

_info = [
    ("ML-Agents 4.0.2",
     "Bản phát hành chỉ đăng ký sẵn ba trainer: ppo, poca và sac. Ba thuật toán này chạy "
     "trực tiếp bằng tệp cấu hình."),
    ("Trainer mở rộng cho MAPPO và DQN",
     "Hai thuật toán còn lại được đăng ký thêm theo tên, dùng chung gRPC, TensorBoard và "
     "đường xuất ONNX của ML-Agents."),
    ("Vì sao phải chung một đường ống",
     "Chỉ khi cả năm cùng thu quỹ đạo, cùng ghi nhật ký và cùng xuất mô hình theo một cách, "
     "chênh lệch đo được mới nói về môi trường."),
]
for i, (h, b) in enumerate(_info):
    x = 0.55 + i * 4.15
    need = card_text(s, x, 3.56, 3.95, 1.98, h, b, hsz=15.5, bsz=13.5)
    check(f"S4 info {i}", 1.62, need)

callout(s, 0.55, 5.72, 12.25, 1.06)
textbox(s, 0.82, 5.72, 11.71, 1.06, [
    {"runs": [("Mỗi lần chạy dùng 8 khu vực huấn luyện song song trong cùng một cảnh Unity. ",
               {"sz": 14, "b": True, "c": NAVY}),
              ("Mọi số liệu báo cáo đều trích thẳng từ TensorBoard, không làm mượt — biểu đồ nào có "
               "làm mượt đều ghi rõ ở chú thích.", {"sz": 14})], "line": 1.12}],
    anchor="c")
notes(s, "Kiến trúc rất thẳng: môi trường Unity sinh quan sát và nhận hành động; trainer ML-Agents "
         "huấn luyện; TensorBoard ghi lại; mô hình được xuất ra ONNX; ứng dụng demo nạp mô hình đó. "
         "Điểm cần nói thêm là ML-Agents 4.0.2 chỉ có sẵn ba trainer, nên MAPPO và DQN được em bổ sung "
         "dưới dạng trainer mở rộng, dùng chung đường ống đo. Nhờ vậy mười lăm lần chạy mới so sánh "
         "được với nhau.")

# ================================================== 5. BA MÔI TRƯỜNG ĐẠI DIỆN ==
s = new_slide_t("Ba môi trường đại diện ba dạng bài toán")
chip(s, 0.55, 1.16, "Ba dạng bài toán, ba nhóm thách thức thiết kế khác hẳn nhau")

_envs = [
    ("env_football.png", "Football Table", "ĐỐI KHÁNG 1-1", RGBColor(0x2E, 0x86, 0xC1),
     ["Hành động liên tục 8 chiều · quan sát 60 giá trị",
      "Cơ chế tự chơi, đo tiến bộ bằng chỉ số ELO",
      "Thách thức: gán công lao trong tự chơi"]),
    ("env_puzzle.png", "Capture The Flag", "HỢP TÁC HAI TÁC NHÂN", RGBColor(0x7D, 0x3C, 0x98),
     ["7 hành động rời rạc · quan sát 61 giá trị",
      "Phần thưởng nhóm kèm học theo chương trình",
      "Thách thức: gán công lao cho cả nhóm"]),
    ("env_crossroad.png", "Cross The Road", "ĐIỀU HƯỚNG ĐƠN TÁC NHÂN", RGBColor(0x27, 0x92, 0x4F),
     ["4 hành động rời rạc · quan sát 132 giá trị",
      "Phần thưởng thưa, không giới hạn số bước",
      "Thách thức: chống chính sách tự đóng băng"]),
]
for i, (fn, name, kind, kc, bullets) in enumerate(_envs):
    x = 0.55 + i * 4.15
    card(s, x, 1.76, 3.95, 4.72)
    picture_plate(s, x + 0.18, 1.94, 3.59, 2.10, os.path.join(IMG, fn), pad=0.05)
    simple(s, x + 0.26, 4.14, 3.43, 0.34, name, sz=17, b=True, c=NAVY, wrap=False)
    simple(s, x + 0.26, 4.50, 3.43, 0.28, kind, sz=11.5, b=True, c=kc, wrap=False)
    dash_bullets(s, x + 0.26, 4.86, 3.43, 1.46, bullets, sz=13.5, line=1.08,
                 space_after=7)

caption(s, 0.55, 6.58, 12.25,
        "Ảnh chụp trực tiếp trong Unity. Cả ba môi trường chạy trên cùng phần cứng và cùng đường ống đo.")
notes(s, "Ba môi trường được chọn để phủ ba dạng bài toán khác hẳn nhau, chứ không phải ba biến thể "
         "của cùng một dạng. Football Table là đối kháng một chọi một với hành động liên tục. "
         "Capture The Flag là hợp tác hai tác nhân với phần thưởng nhóm. Cross The Road là điều hướng "
         "đơn tác nhân với phần thưởng thưa. Ba nhóm thách thức thiết kế hoàn toàn khác nhau.")

# ================================================ 6. TRỌNG TÂM: HÀM PHẦN THƯỞNG
s = new_slide_t("Trọng tâm thiết kế — hàm phần thưởng")
chip(s, 0.55, 1.16, "Thành phần khó thiết kế nhất của một hệ thống học tăng cường")

card(s, 0.55, 1.76, 5.30, 2.34)
_bn = {"sz": 15.5, "b": True, "c": NAVY}
_sb = {"sz": 15.5, "b": True, "c": NAVY, "sub": True}
textbox(s, 0.80, 1.92, 4.80, 0.40, [
    {"runs": [("R(s, a, s′)  =  R", _bn), ("mt", _sb), ("(s′)  +  F(s, s′)  +  R", _bn),
              ("b", _sb), ("(s)", _bn)], "align": "c", "line": 1.0}], wrap=False)
_parts = [(("R", "mt"), " · mục tiêu",
           "thưa, chỉ khác không tại cột mốc — thành phần định nghĩa bài toán"),
          (("F", ""), " · định hình thế năng",
           "F = γΦ(s′) − Φ(s), bảo đảm không đổi lời giải tối ưu"),
          (("R", "b"), " · theo bước",
           "dày, mỗi bước — nơi phát sinh lợi dụng phần thưởng")]
_py = 2.42
for (sym, sub), lab, b in _parts:
    runs = [(sym, {"sz": 13, "b": True, "c": ORANGE})]
    if sub:
        runs.append((sub, {"sz": 13, "b": True, "c": ORANGE, "sub": True}))
    runs.append((lab + "  ", {"sz": 13, "b": True, "c": ORANGE}))
    runs.append((b, {"sz": 13, "c": INK}))
    textbox(s, 0.80, _py, 4.80, 0.52, [{"runs": runs, "line": 1.06}])
    _py += 0.56

card(s, 6.15, 1.76, 6.65, 2.34)
simple(s, 6.40, 1.92, 6.15, 0.28, "ĐẶC TẢ ĐI THEO MỘT CHIỀU DUY NHẤT",
       sz=12.5, b=True, c=ORANGE, align="c", wrap=False)
_flow = [("HÀNH VI MỤC TIÊU", "lời giải mẫu do người thiết kế viết ra"),
         ("HÀM PHẦN THƯỞNG", "phát biểu lại hành vi đó bằng số"),
         ("CHÍNH SÁCH HỌC ĐƯỢC", "hành vi thật mà tác nhân chọn")]
_fw, _fgap = 1.92, 0.24
_fx = 6.40
for i, (h, b) in enumerate(_flow):
    x = _fx + i * (_fw + _fgap)
    round_rect(s, x, 2.34, _fw, 1.04, fill=WHITE, line=NAVY, lw=1.0, adj=0.10)
    textbox(s, x + 0.08, 2.42, _fw - 0.16, 0.88, [
        {"runs": [(h, {"sz": 11.5, "b": True, "c": NAVY})], "align": "c",
         "line": 1.0, "space_after": 3},
        {"runs": [(b, {"sz": 10, "c": MUTED})], "align": "c", "line": 1.02}],
        anchor="c")
    if i < 2:
        arrow(s, x + _fw + 0.01, 2.73, 0.22, 0.26, MSO_SHAPE.RIGHT_ARROW)
simple(s, 6.40, 3.50, 6.15, 0.46,
       "Sai lệch chỉ lộ ra ở bước cuối: quan sát hành vi thật rồi lần ngược về đặc tả — "
       "không có thông báo lỗi nào chỉ đường.", sz=11.5, i=True, c=MUTED, align="c", line=1.06)

_pr = [
    ("1", "Bám theo lời giải mẫu",
     "Viết ra trình tự thao tác mà một người chơi giỏi sẽ làm, rồi mới đặt phần thưởng lên từng mốc của trình tự đó."),
    ("2", "Ưu tiên sự kiện và thế năng",
     "Thưởng một lần tại cột mốc, hoặc định hình theo thế năng. Tránh cộng dồn theo bước vì đó là nơi sinh lối tắt."),
    ("3", "Giữ trật tự độ lớn",
     "Tổng mọi khoản phụ trên trọn một lượt chơi phải nhỏ hơn phần thưởng hoàn thành nhiệm vụ."),
    ("4", "Sửa cơ chế trước khi tăng hệ số",
     "Nếu hành vi mong muốn không xuất hiện, hãy sửa cơ chế game hoặc chương trình học trước khi nhân hệ số lên."),
]
for i, (n, h, b) in enumerate(_pr):
    x = 0.55 + i * 3.11
    card(s, x, 4.28, 2.92, 2.20)
    oval(s, x + 0.22, 4.44, 0.36, fill=NAVY, label=n, sz=12.5)
    simple(s, x + 0.66, 4.40, 2.04, 0.46, h, sz=13.5, b=True, c=NAVY, line=1.02,
           anchor="c")
    simple(s, x + 0.22, 4.96, 2.48, 1.46, b, sz=12.5, c=INK, line=1.08, anchor="c")

caption(s, 0.55, 6.58, 12.25,
        "Bốn nguyên tắc dùng chung cho cả ba môi trường; mỗi hằng số ở ba slide sau đều kèm một lập luận định lượng.")
notes(s, "Hàm phần thưởng là thành phần khó thiết kế nhất. Em tách nó thành ba thành phần: phần mục tiêu "
         "thưa tại cột mốc, phần định hình theo thế năng, và phần theo bước. Đặc tả đi theo một chiều: "
         "từ hành vi mục tiêu sang hàm phần thưởng sang chính sách học được — nhưng sai lệch chỉ lộ ra ở "
         "bước cuối. Vì vậy em rút ra bốn nguyên tắc, và ba slide tiếp theo sẽ cho thấy mỗi hằng số đều "
         "có một lập luận định lượng đứng sau.")

# ================================================== 7. FOOTBALL TABLE (THIẾT KẾ)
s = new_slide_t("Football Table — đối kháng 1-1, hành động liên tục")
picture_plate(s, 0.55, 1.18, 5.55, 3.30, os.path.join(IMG, "env_football.png"), pad=0.16)
caption(s, 0.55, 4.54, 5.55,
        "Bàn bi lắc 3D: bốn thanh gạt mỗi đội, mỗi thanh có hai bậc tự do là trượt và xoay.")
callout(s, 0.55, 4.96, 5.55, 1.74)
_, need = head_body(s, 0.80, 5.14, 5.05,
                    "Vì sao tỉ lệ 5 trên 1",
                    "Nếu thưởng và phạt cân bằng, tác nhân chỉ chịu tấn công khi tự tin thắng 40% số "
                    "pha bóng — điều gần như không đúng ở đầu huấn luyện, nên chính sách hội tụ về "
                    "phòng ngự tuyệt đối. Với +5 và −1, ngưỡng đó bằng đúng 0.",
                    hsz=15, bsz=13, hcolor=ORANGE)
check("S7 callout", 1.38, need)

_fb = [
    ("Không gian quan sát", "60 giá trị",
     "Trạng thái bóng, 4 thanh gạt đội nhà và 4 thanh gạt đối thủ. Đối xứng hóa để một mạng dùng chung hai phía."),
    ("Không gian hành động", "Liên tục, 8 chiều",
     "Mỗi thanh gạt có trượt và xoay; một tác nhân điều khiển cả bốn thanh, 25 quyết định mỗi giây."),
    ("Hàm phần thưởng", "+5  ·  −1  ·  −1/3000",
     "Cộng 5 khi ghi bàn, trừ 1 khi thủng lưới, trừ 1/3000 mỗi bước. Nhân với 3.000 bước, phạt thời gian tối đa vừa đúng 1."),
    ("Cơ chế tự chơi", "đo bằng ELO",
     "Đối thủ là các phiên bản trước của chính mình. Ngân sách 1.600.000 bước; DQN cần một bản dựng rời rạc riêng."),
]
for i, (lab, val, body) in enumerate(_fb):
    spec_row(s, 6.42, 1.18 + i * 1.39, 6.38, 1.30, lab, val, body)
notes(s, "Football Table là bàn bi lắc ba chiều. Quan sát 60 giá trị gồm trạng thái bóng cùng bốn thanh "
         "gạt mỗi bên. Hành động liên tục tám chiều: mỗi thanh gạt trượt và xoay. Phần thưởng cộng 5 khi "
         "ghi bàn, trừ 1 khi thủng lưới, trừ một phần ba nghìn mỗi bước. Tỉ lệ 5 trên 1 không tùy tiện: "
         "nếu để cân bằng, ngưỡng đáng tấn công là 40% — quá cao ở đầu huấn luyện nên tác nhân sẽ chỉ "
         "phòng ngự. Với 5 trên 1 thì ngưỡng bằng 0. Còn phạt thời gian nhân với 3.000 bước cho đúng 1 "
         "điểm, bằng đúng hình phạt thủng lưới, nên hòa không bàn thắng bị đánh ngang với thua một bàn.")

# ================================================ 8. CAPTURE THE FLAG (THIẾT KẾ)
s = new_slide_t("Capture The Flag — hợp tác hai tác nhân")
picture_plate(s, 0.55, 1.18, 5.55, 3.30, os.path.join(IMG, "env_puzzle.png"), pad=0.16)
caption(s, 0.55, 4.54, 5.55,
        "Hành lang ba khoang: hai bàn đạp nằm hai phía đối diện nhưng cùng điều khiển một cổng cửa.")
callout(s, 0.55, 4.96, 5.55, 1.74)
_, need = head_body(s, 0.80, 5.14, 5.05,
                    "Khoảng ân hạn cửa 1 giây",
                    "Khoảng cách từ bàn đạp tới cổng là 19 đơn vị. Ngay cả khi giả định tác nhân đã chạy "
                    "sẵn ở vận tốc tối đa 17,5 đơn vị/giây thì vẫn chưa tới; xuất phát từ trạng thái "
                    "đứng yên chỉ đi được khoảng 13,2. Không tồn tại quỹ đạo đơn độc nào vượt được cổng.",
                    hsz=15, bsz=12.5, hcolor=ORANGE)
check("S8 callout", 1.38, need)

_ctf = [
    ("Không gian quan sát", "61 giá trị",
     "5 cờ logic về bàn đạp và trạng thái vượt cổng của bản thân lẫn đồng đội, cộng 7 tia cảm biến × 8 giá trị."),
    ("Không gian hành động", "Rời rạc, 7 hành động",
     "2,5 quyết định mỗi giây — bài toán thiên về chiến thuật hơn phản xạ. Hai tác nhân cùng đẩy khối thì nhanh gần gấp đôi."),
    ("Phần thưởng nhóm", "+1  ·  +0,5  ·  κ = 0,01",
     "Cộng 1 khi cả hai cùng tới đích, cộng 0,5 mỗi lần vượt cổng, định hình thế năng với κ = 0,01."),
    ("Các khoản theo bước", "chuẩn hóa theo N = 100.000",
     "Bàn đạp +0,5/N, đẩy khối +0,25/N, phạt thời gian −0,1/N. Chuẩn hóa giữ tổng khoản phụ luôn nhỏ hơn phần thưởng hoàn thành."),
]
for i, (lab, val, body) in enumerate(_ctf):
    spec_row(s, 6.42, 1.18 + i * 1.39, 6.38, 1.30, lab, val, body, bsz=12.5)
notes(s, "Capture The Flag là câu đố bàn giao: hai bàn đạp cùng điều khiển một cổng cửa, nhưng nằm ở hai "
         "phía đối diện của cổng đó, nên không ai tự mình giải được. Quan sát 61 giá trị, trong đó 5 cờ "
         "logic là mấu chốt vì chúng cho tác nhân biết khi nào nên rời bàn đạp. Mọi khoản theo bước đều "
         "chuẩn hóa theo N bằng một trăm nghìn để tổng của chúng luôn nhỏ hơn phần thưởng hoàn thành. "
         "Khoảng ân hạn một giây là điểm em phải chứng minh: nó đủ để màn bàn giao khả học, nhưng không "
         "đủ để một tác nhân tự vượt cổng — nên mọi kết quả cao đều là hợp tác thật.")

# ================================================== 9. CROSS THE ROAD (THIẾT KẾ)
s = new_slide_t("Cross The Road — điều hướng với phần thưởng thưa")
picture_plate(s, 0.55, 1.18, 5.55, 3.30, os.path.join(IMG, "env_crossroad.png"), pad=0.16)
caption(s, 0.55, 4.54, 5.55,
        "Năm làn xe; tốc độ mỗi xe bốc ngẫu nhiên lại sau mỗi lượt chơi nên không học vẹt được.")
callout(s, 0.55, 4.96, 5.55, 1.74)
_, need = head_body(s, 0.80, 5.14, 5.05,
                    "Vì sao phạt va chạm chỉ 0,025",
                    "Lượt chơi không giới hạn số bước, nên đứng yên vĩnh viễn luôn có giá trị kỳ vọng "
                    "bằng 0. Nếu phạt cân bằng với thưởng, ngưỡng đáng đi tiếp vọt lên 50% và chính sách "
                    "tự đóng băng. Với 0,025 thì ngưỡng chỉ còn 2,4%.",
                    hsz=15, bsz=13, hcolor=ORANGE)
check("S9 callout", 1.38, need)

_ctr = [
    ("Không gian quan sát", "132 giá trị",
     "Tọa độ tác nhân và đích cho biết đi về đâu; 21 tia cảm biến × 6 giá trị cho biết lúc nào an toàn."),
    ("Không gian hành động", "Rời rạc, 4 hành động",
     "Đứng yên, sang trái, sang phải, tiến lên. Đứng yên ở đây là một nước đi chiến thuật, không phải lựa chọn thừa."),
    ("Hàm phần thưởng", "+1  ·  −0,025",
     "Cộng 1 khi tới đích, trừ 0,025 khi va chạm. Răn đe thật nằm ở chỗ va chạm kết thúc lượt chơi ngay, tức mất trắng cơ hội nhận 1 điểm."),
    ("Tín hiệu tò mò", "cường độ 0,02",
     "Bằng 1/50 trọng số tín hiệu ngoại vi. Tạo động lực khám phá mà không cần phạt thời gian trong lượt chơi không giới hạn."),
]
for i, (lab, val, body) in enumerate(_ctr):
    spec_row(s, 6.42, 1.18 + i * 1.39, 6.38, 1.30, lab, val, body, bsz=12.5)
notes(s, "Cross The Road đơn giản về luật nhưng khó về tín hiệu học. Quan sát 132 giá trị: tọa độ cho "
         "biết đi về đâu, 21 tia cho biết lúc nào an toàn. Bốn hành động rời rạc, trong đó đứng yên là "
         "một nước đi chiến thuật. Điều đáng nói là mức phạt va chạm: môi trường không giới hạn số bước "
         "nên đứng yên mãi mãi có giá trị đúng bằng không. Nếu phạt bằng 1 thì ngưỡng đáng đi tiếp là "
         "50%, tác nhân sẽ tự đóng băng. Đặt 0,025 thì ngưỡng còn 2,4%. Thêm tín hiệu tò mò cường độ "
         "0,02 để khuyến khích khám phá.")

# =============================================== 10. CASE STUDY CAPTURE THE FLAG
s = new_slide_t("Case study — vòng hiệu chỉnh phần thưởng của Capture The Flag")
chip(s, 0.55, 1.16, "Môi trường duy nhất phải thiết kế lại sau khi phiên bản đầu thất bại")

round_rect(s, 0.55, 1.76, 12.25, 0.62, fill=CARD2, adj=0.16)
simple(s, 0.75, 1.76, 11.85, 0.62,
       "Phần thưởng nhóm mắc kẹt đúng ở mức sàn  =  tổng phạt thời gian trọn một lượt chơi",
       sz=15.5, b=True, c=NAVY, align="c", anchor="c", wrap=False)

_case = [
    ("①", "Triệu chứng", "đường cong phẳng, không một dòng báo lỗi",
     "Huấn luyện bằng MA-POCA, phần thưởng nhóm đứng im ở mức sàn suốt hàng triệu bước. "
     "Mã nguồn vẫn chạy đúng, đường cong vẫn được vẽ ra. Mắc kẹt ở đúng giá trị của riêng "
     "khoản phạt thời gian, nghĩa là không lượt chơi nào chạm đích."),
    ("②", "Chẩn đoán", "phạt đúng vào trạng thái phải đi qua",
     "Hai khoản phạt nhóm giáng đúng vào trạng thái hai tác nhân đứng khác phía cửa — đúng "
     "trạng thái mà lời giải bắt buộc phải đi qua để bàn giao. Thêm nữa, thưởng cộng dồn theo "
     "bước chưa chuẩn hóa, và cửa sập tức thì khiến màn bàn giao gần như không khám phá nổi."),
    ("③", "Bốn thay đổi", "chuyển từ phạt sang thưởng",
     "Gỡ toàn bộ phạt nhóm, thay bằng thưởng bàn giao một lần +0,5. Chuyển tín hiệu dẫn đường "
     "sang định hình theo thế năng. Thêm khoảng ân hạn cửa một giây. Bổ sung hai cờ vượt cổng "
     "vào quan sát để tác nhân biết khi nào nên rời bàn đạp."),
]
for i, (num, h, sub, body) in enumerate(_case):
    x = 0.55 + i * 4.15
    card(s, x, 2.56, 3.95, 3.04)
    textbox(s, x + 0.24, 2.74, 3.47, 0.66, [
        {"runs": [(num + "  ", {"sz": 15.5, "b": True, "c": ORANGE}),
                  (h, {"sz": 15.5, "b": True, "c": NAVY})], "line": 1.0, "space_after": 2},
        {"runs": [(sub, {"sz": 12, "i": True, "c": ORANGE})], "line": 1.0}])
    simple(s, x + 0.24, 3.44, 3.47, 1.94, body, sz=13, c=INK, line=1.10, anchor="c")

callout(s, 0.55, 5.74, 12.25, 1.08)
textbox(s, 0.82, 5.90, 11.71, 0.78, [
    {"runs": [("Trước:  ", {"sz": 14, "b": True, "c": ORANGE}),
              ("phần thưởng nhóm phẳng ở mức sàn suốt hàng triệu bước.    ", {"sz": 14}),
              ("Sau:  ", {"sz": 14, "b": True, "c": ORANGE}),
              ("thoát mức sàn và leo tới 0,840 — giá trị của một lời giải trọn vẹn.", {"sz": 14})],
     "line": 1.10, "space_after": 3},
    {"runs": [("Bài học dùng lại được: một hàm phần thưởng hỏng thường để lại dấu vết định lượng "
               "rất rõ ngay trên chỉ số huấn luyện, nếu biết đọc đúng chỗ.",
               {"sz": 13.5, "i": True, "c": MUTED})], "line": 1.06}])
notes(s, "Đây là ví dụ cụ thể nhất cho luận điểm môi trường sai không báo lỗi. Phiên bản phần thưởng đầu "
         "tiên của Capture The Flag làm phần thưởng nhóm phẳng lì ở mức sàn suốt hàng triệu bước, mà "
         "không có bất kỳ dòng báo lỗi nào. Khi chẩn đoán, em phát hiện hai khoản phạt nhóm đang giáng "
         "đúng vào trạng thái hai tác nhân đứng khác phía cửa — mà đó chính là trạng thái bắt buộc để "
         "bàn giao. Nói cách khác, hàm phần thưởng đang phạt đúng lời giải. Bốn thay đổi sau đó đưa "
         "phần thưởng nhóm lên 0,840.")

# ======================================================= 11. THIẾT KẾ THỰC NGHIỆM
s = new_slide_t("Thiết kế thực nghiệm — lưới đầy đủ 5 × 3")
chip(s, 0.55, 1.16, "Thuật toán là phép thử để kiểm chứng môi trường, không phải đối tượng chính")

for i, (num, lab) in enumerate([("15", "lần huấn luyện đầy đủ"), ("5", "thuật toán làm phép thử"),
                                ("3", "môi trường game 3D"), ("×8", "khu vực chạy song song")]):
    stat_tile(s, 0.55 + i * 3.11, 1.76, 2.92, 1.14, num, lab, nsz=28, lsz=12)

chip(s, 0.55, 3.12, "Ma trận thực nghiệm 3 × 5", sz=13.5, h=0.36)
table(s, 0.55, 3.62, 7.15, 1.70, [
    ["Môi trường", "PPO", "SAC", "MA-POCA", "MAPPO", "DQN"],
    ["Football Table", "✓", "✓", "✓", "✓", "✓ *"],
    ["Capture The Flag", "✓", "✓", "✓", "✓", "✓"],
    ["Cross The Road", "✓", "✓", "✓", "✓", "✓"],
], col_w=[2.3, 1, 1, 1.3, 1.1, 1.1], hsz=12.5, bsz=13, row_h=0.40, align_first="l")
caption(s, 0.55, 5.38, 7.15,
        "* DQN chỉ nhận hành động rời rạc nên Football Table cần một bản dựng 8 nhánh × 3 mức riêng, chạy không có tự chơi.")

chip(s, 7.95, 3.12, "Ngân sách bước và phần cứng", sz=13.5, h=0.36)
card(s, 7.95, 3.62, 4.85, 2.16)
_rows = [("Cross The Road", "2.000.000 bước"), ("Capture The Flag", "1.700.000 bước"),
         ("Football Table", "1.600.000 bước"),
         ("Phần cứng", "i5-14600KF · RTX 3050 · 32 GB"),
         ("Nền tảng", "Unity 6000.3 · ML-Agents 4.0.2")]
_ry = 3.78
for k, v in _rows:
    textbox(s, 8.20, _ry, 4.35, 0.36, [
        {"runs": [(k, {"sz": 13, "b": True, "c": NAVY}),
                  ("   " + v, {"sz": 13, "c": INK})], "line": 1.0}])
    _ry += 0.39

callout(s, 0.55, 5.94, 12.25, 0.92)
textbox(s, 0.82, 6.08, 11.71, 0.66, [
    {"runs": [("Trong từng môi trường, cả năm thuật toán dùng chung một ngân sách bước và cùng phần cứng. ",
               {"sz": 14, "b": True, "c": NAVY}),
              ("Một môi trường chỉ được coi là kiểm chứng chắc chắn khi nó phản ứng nhất quán trước nhiều "
               "hướng tiếp cận khác nguyên lý.", {"sz": 14})], "line": 1.12}])
notes(s, "Thiết kế thực nghiệm là một lưới đầy đủ: năm thuật toán nhân ba môi trường, tổng cộng mười lăm "
         "lần huấn luyện. Trong từng môi trường, cả năm dùng chung một ngân sách bước và cùng phần cứng. "
         "Mỗi lần chạy có tám khu vực song song. Em xin nhấn mạnh lại: năm thuật toán ở đây đóng vai phép "
         "thử để dò đặc tính môi trường, chứ không phải đối tượng đánh giá. Một môi trường chỉ đáng tin "
         "khi nó phản ứng nhất quán trước nhiều hướng tiếp cận khác nguyên lý.")

# ================================================ 12. TIÊU CHÍ NGHIỆM THU
s = new_slide_t("Tiêu chí nghiệm thu môi trường")
chip(s, 0.55, 1.16, "Ba tiêu chí bắt buộc và bốn chỉ số đo đi kèm")

_crit = [("①", "HỌC ĐƯỢC", "Ít nhất 4 trên 5 thuật toán phải tiến bộ rõ rệt so với lúc khởi tạo. "
          "Nếu không thuật toán nào học được, lỗi nằm ở đặc tả chứ không ở thuật toán."),
         ("②", "PHÂN BIỆT ĐƯỢC", "Các hướng tiếp cận khác nguyên lý phải tách được nhau trên chỉ số đo. "
          "Một môi trường cho mọi thuật toán cùng một điểm thì không dùng để so sánh được."),
         ("③", "KHÔNG CÓ LỐI TẮT", "Không lần chạy nào được đạt điểm sát trần mà chưa thật sự giải "
          "được nhiệm vụ. Đây là tiêu chí bắt lỗi lợi dụng phần thưởng.")]
for i, (num, h, b) in enumerate(_crit):
    x = 0.55 + i * 4.15
    card(s, x, 1.76, 3.95, 2.32)
    oval(s, x + 0.26, 1.98, 0.42, fill=ORANGE, label=num, sz=15)
    simple(s, x + 0.80, 2.02, 2.90, 0.36, h, sz=16, b=True, c=NAVY, wrap=False)
    simple(s, x + 0.26, 2.52, 3.43, 1.40, b, sz=13.5, c=INK, line=1.10, anchor="c")

chip(s, 0.55, 4.24, "Bốn chỉ số đo định lượng", sz=13.5, h=0.36)
_met = [("Mức năng lực", "phần thưởng trung bình trên 10% cuối"),
        ("Tốc độ hội tụ", "bước mà từ đó đường cong không tụt dưới 90% mức ổn định"),
        ("Độ ổn định", "độ lệch chuẩn của đường cong trên 10% cuối"),
        ("Độ dài lượt chơi", "giải nhanh hay chạm trần thời gian")]
for i, (h, b) in enumerate(_met):
    x = 0.55 + i * 3.11
    card(s, x, 4.72, 2.92, 1.14)
    textbox(s, x + 0.22, 4.86, 2.48, 0.88, [
        {"runs": [(h, {"sz": 13.5, "b": True, "c": NAVY})], "line": 1.0, "space_after": 3},
        {"runs": [(b, {"sz": 11.5, "c": MUTED})], "line": 1.06}])

callout(s, 0.55, 6.02, 12.25, 0.90)
textbox(s, 0.82, 6.16, 11.71, 0.64, [
    {"runs": [("Football Table dùng thêm chỉ số ELO vì trong tự chơi phần thưởng không so trực tiếp được. ",
               {"sz": 14, "b": True, "c": NAVY}),
              ("Kết quả nghiệm thu: Cross The Road và Capture The Flag đạt cả ba tiêu chí; Football Table "
               "đạt 2 trên 3 do dải ELO quá hẹp.", {"sz": 14})], "line": 1.12}])
notes(s, "Để nói một môi trường là dùng được, em đặt ra ba tiêu chí. Học được: ít nhất bốn trên năm thuật "
         "toán phải tiến bộ rõ. Phân biệt được: các hướng tiếp cận khác nguyên lý phải tách được nhau. "
         "Và không có lối tắt: không lần chạy nào được điểm cao mà chưa thật sự giải được nhiệm vụ. "
         "Bốn chỉ số đo kèm theo là mức năng lực, tốc độ hội tụ, độ ổn định và độ dài lượt chơi. Riêng "
         "Football Table dùng thêm ELO vì trong tự chơi phần thưởng không so trực tiếp được.")

# ======================================================== 13. KẾT QUẢ NỔI BẬT ==
s = new_slide_t("Kết quả nổi bật")
chip(s, 0.55, 1.16, "Phần thưởng trung bình 10% cuối, cùng ngân sách bước trong từng môi trường")

card(s, 0.55, 1.76, 7.15, 4.06)
cd = CategoryChartData()
cd.categories = ["PPO", "SAC", "MA-POCA", "MAPPO", "DQN"]
# giá trị nhân 1000 để mã định dạng in ra dấu phẩy thập phân kiểu Việt Nam
cd.add_series("Cross The Road", (690, 846, 556, 835, 336))
cd.add_series("Capture The Flag", (834, 183, 838, 840, 800))
gf = s.shapes.add_chart(XL_CHART_TYPE.COLUMN_CLUSTERED, Inches(0.63), Inches(1.84),
                        Inches(6.99), Inches(3.90), cd)
ch = gf.chart
ch.has_title = False
ch.has_legend = True
ch.legend.position = XL_LEGEND_POSITION.TOP
ch.legend.include_in_layout = False
ch.legend.font.size = Pt(11.5)
ch.legend.font.name = FONT
ch.legend.font.color.rgb = INK
pl = ch.plots[0]
pl.gap_width = 60
pl.overlap = -10
pl.has_data_labels = True
dl = pl.data_labels
dl.number_format = '0","000'
dl.number_format_is_linked = False
dl.position = XL_LABEL_POSITION.OUTSIDE_END
dl.font.size = Pt(9.5)
dl.font.name = FONT
dl.font.bold = True
dl.font.color.rgb = INK
for srs, col in zip(ch.series, (ORANGE, NAVY)):
    srs.format.fill.solid()
    srs.format.fill.fore_color.rgb = col
    srs.format.line.fill.background()
va = ch.value_axis
va.maximum_scale = 1000
va.minimum_scale = 0
va.major_unit = 200
va.tick_labels.number_format = '0","000'
va.tick_labels.number_format_is_linked = False
va.has_major_gridlines = True
va.major_gridlines.format.line.color.rgb = ICE
va.major_gridlines.format.line.width = Pt(0.75)
va.tick_labels.font.size = Pt(10.5)
va.tick_labels.font.name = FONT
va.tick_labels.font.color.rgb = MUTED
va.format.line.color.rgb = LINE
ca = ch.category_axis
ca.has_major_gridlines = False
ca.tick_labels.font.size = Pt(12)
ca.tick_labels.font.bold = True
ca.tick_labels.font.name = FONT
ca.tick_labels.font.color.rgb = NAVY
ca.format.line.color.rgb = LINE

caption(s, 0.55, 5.88, 7.15,
        "Football Table không có mặt ở đây vì tự chơi được đo bằng ELO — đường cong của cả ba môi trường ở ba slide sau.")

_find = [
    ("Football Table", "ELO tăng 36 – 64 điểm",
     "MAPPO +64, PPO +60, SAC +57, MA-POCA +36 so với mốc khởi tạo 1200. Không lần nào kết thúc dưới "
     "điểm xuất phát, nhưng dải 1237–1260 quá hẹp để xếp hạng."),
    ("Cross The Road", "0,846 cao nhất  ·  0,336 thấp nhất",
     "SAC dẫn đầu, DQN cuối bảng. Phổ kết quả trải rộng nhất trong ba môi trường, chín trên mười cặp "
     "thuật toán tách được nhau."),
    ("Capture The Flag", "bốn thuật toán 0,800 – 0,840",
     "PPO, MA-POCA, MAPPO và DQN đều giải được câu đố. Riêng SAC dừng ở 0,183 với độ dài lượt chơi "
     "chạm trần 4999 gần như suốt quá trình."),
]
for i, (h, val, b) in enumerate(_find):
    y = 1.76 + i * 1.72
    card(s, 7.95, y, 4.85, 1.56)
    textbox(s, 8.19, y + 0.16, 4.37, 1.26, [
        {"runs": [(h, {"sz": 14.5, "b": True, "c": NAVY})], "line": 1.0, "space_after": 2},
        {"runs": [(val, {"sz": 13.5, "b": True, "c": ORANGE})], "line": 1.0, "space_after": 4},
        {"runs": [(b, {"sz": 12.5, "c": INK})], "line": 1.06}])
notes(s, "Đây là kết quả cô đọng nhất. Trên Cross The Road, SAC cao nhất với 0,846 còn DQN chỉ 0,336 — "
         "phổ trải rộng, môi trường phân biệt tốt. Trên Capture The Flag, bốn thuật toán đều giải được "
         "câu đố và nằm gọn trong dải 0,800 đến 0,840, riêng SAC dừng ở 0,183. Còn Football Table không "
         "có trong biểu đồ vì tự chơi đo bằng ELO: cả bốn thuật toán tự chơi đều tăng, từ 36 tới 64 điểm, "
         "nhưng khoảng cách giữa chúng còn quá hẹp để xếp hạng.")

# ============================== 14. ĐƯỜNG CONG FOOTBALL TABLE (REWARD + ELO) ==
s = new_slide_t("Football Table — phần thưởng và chỉ số ELO")
chip(s, 0.55, 1.16, "Phần thưởng tích lũy", sz=13.5, h=0.36)
chip(s, 6.70, 1.16, "Chỉ số xếp hạng ELO trong tự chơi", sz=13.5, h=0.36)

card(s, 0.55, 1.64, 6.10, 3.42)
line_chart(s, 0.62, 1.70, 5.96, 3.30, series_for("Football Table", smooth=9),
           0, 3000, 500, 1.6, 0.2, "Số bước huấn luyện (triệu)", "Phần thưởng tích lũy")
card(s, 6.70, 1.64, 6.10, 3.42)
line_chart(s, 6.77, 1.70, 5.96, 3.30,
           series_for("Football Table", metric="elo", scale=1.0),
           1180, 1280, 20, 1.6, 0.2, "Số bước huấn luyện (triệu)", "Chỉ số xếp hạng ELO",
           numfmt="0")

caption(s, 0.55, 5.12, 6.10,
        "Trung bình trượt 9 điểm — phần thưởng thô trong tự chơi dao động quá mạnh để đọc.")
caption(s, 6.70, 5.12, 6.10,
        "Số liệu thô, không làm mượt. DQN chạy không có tự chơi nên không có ELO.")

for i, (h, b) in enumerate([
    ("Phần thưởng và ELO không xếp cùng một thứ hạng",
     "MAPPO 2,117 · SAC 1,842 · DQN 1,825 · MA-POCA 1,752 · PPO 1,691. Trong tự chơi, phần thưởng phụ "
     "thuộc vào việc gặp phiên bản đối thủ nào, nên chỉ ELO mới đo được tiến bộ thật."),
    ("Cả bốn đường ELO đều đi lên, nhưng dải quá hẹp",
     "MAPPO +64 · PPO +60 · SAC +57 · MA-POCA +36 so với mốc 1200, nên môi trường học được. Song dải "
     "1237–1260 hẹp hơn dao động của chính đường cong, nên không xếp hạng được nhóm dẫn đầu."),
]):
    x = 0.55 + i * 6.15
    need = card_text(s, x, 5.54, 6.10, 1.34, h, b, hsz=14.5, bsz=12.5)
    check(f"S14 note {i}", 1.10, need)
notes(s, "Đây là hai đường cong của Football Table. Bên trái là phần thưởng tích lũy: MAPPO cao nhất với "
         "2,117, rồi SAC, DQN, MA-POCA và PPO. Nhưng trong cơ chế tự chơi thì phần thưởng không phải "
         "thước đo đáng tin, vì nó phụ thuộc vào việc tác nhân đang gặp phiên bản đối thủ mạnh hay yếu. "
         "Bên phải mới là thước đo đúng: chỉ số ELO. Cả bốn thuật toán tự chơi đều tăng so với mốc khởi "
         "tạo 1200, từ 36 tới 64 điểm, nên môi trường học được. Nhưng dải 1237 đến 1260 quá hẹp so với "
         "dao động của chính đường cong, nên em không xếp hạng nhóm dẫn đầu. DQN không ghép được với tự "
         "chơi nên không có ELO.")

# ============================ 15. ĐƯỜNG CONG CAPTURE THE FLAG =================
s = new_slide_t("Capture The Flag — đường cong phần thưởng")
chip(s, 0.55, 1.16, "Phần thưởng tích lũy trên ngân sách 1.700.000 bước", sz=13.5, h=0.36)
card(s, 0.55, 1.64, 6.40, 3.42)
line_chart(s, 0.62, 1.70, 6.26, 3.30, series_for("Capture The Flag"),
           -200, 1000, 200, 1.7, 0.2, "Số bước huấn luyện (triệu)", "Phần thưởng tích lũy")
caption(s, 0.55, 5.12, 6.40,
        "Số liệu thô. Bốn đường leo lên dải 0,80–0,84 rồi nằm yên; riêng SAC nhảy loạn suốt quá trình.")
simple(s, 0.55, 5.52, 6.40, 1.34,
       "SAC không phải không học được gì: nó học được rồi đánh mất, lặp đi lặp lại. Con số 0,183 chỉ là "
       "trung bình của một chuỗi dao động như thế, chứ không phải một chính sách ổn định ở mức thấp.",
       sz=13.5, c=NAVY, b=True, line=1.14)

chip(s, 7.28, 1.16, "Kết quả năm thuật toán", sz=13.5, h=0.36)
table(s, 7.28, 1.64, 5.52, 1.98, [
    ["Thuật toán", "Reward TB", "Bước hội tụ", "Độ dài lượt"],
    ["PPO", "0,834", "~180K", "292,9"],
    ["SAC", "0,183", "Không đạt", "4999,0"],
    ["MA-POCA", "0,838", "~540K", "174,3"],
    ["MAPPO", "0,840", "~260K", "153,3"],
    ["DQN", "0,800", "~1,04M", "2017,9"],
], col_w=[1.5, 1.1, 1.1, 1.1], hsz=12, bsz=12.5, row_h=0.33,
    first_col_color=alg_color)

for i, (h, b) in enumerate([
    ("Độ dài lượt chơi là bằng chứng chắc hơn phần thưởng",
     "Bốn thuật toán dẫn đầu đều kéo lượt chơi xuống, từ 153 bước của MAPPO tới 2018 của DQN. "
     "SAC nằm ở trần 4999 gần như suốt."),
    ("Phê bình tập trung không tạo nổi khác biệt đo được",
     "PPO 0,834 so với MAPPO 0,840 và MA-POCA 0,838. Trên bài toán hợp tác có hai tác nhân đồng nhất, "
     "chênh lệch nằm dưới 1%."),
]):
    y = 3.86 + i * 1.54
    card(s, 7.28, y, 5.52, 1.44)
    oval(s, 7.50, y + 0.18, 0.30, fill=NAVY, label=str(i + 1), sz=11)
    textbox(s, 7.92, y + 0.14, 4.64, 1.16, [
        {"runs": [(h, {"sz": 13.5, "b": True, "c": NAVY})], "line": 1.02, "space_after": 3},
        {"runs": [(b, {"sz": 12.5, "c": INK})], "line": 1.06}])
notes(s, "Đường cong Capture The Flag tách rất rõ giữa giải được và thất bại. Bốn đường leo lên dải 0,80 "
         "đến 0,84 rồi nằm yên, cho thấy chúng đã tìm ra trình tự bàn giao. Riêng SAC nhảy loạn suốt quá "
         "trình: nó học được rồi đánh mất, lặp đi lặp lại, nên con số 0,183 chỉ là trung bình của chuỗi "
         "dao động đó. Em muốn lưu ý thêm rằng độ dài lượt chơi là bằng chứng chắc hơn cả phần thưởng: "
         "bốn thuật toán dẫn đầu đều kéo lượt chơi xuống, còn SAC nằm ở trần 4999 gần như suốt.")

# ============================== 16. ĐƯỜNG CONG CROSS THE ROAD =================
s = new_slide_t("Cross The Road — đường cong phần thưởng")
chip(s, 0.55, 1.16, "Phần thưởng tích lũy trên ngân sách 2.000.000 bước", sz=13.5, h=0.36)
card(s, 0.55, 1.64, 6.40, 3.42)
line_chart(s, 0.62, 1.70, 6.26, 3.30, series_for("Cross The Road"),
           -200, 1000, 200, 2.0, 0.2, "Số bước huấn luyện (triệu)", "Phần thưởng tích lũy")
caption(s, 0.55, 5.12, 6.40,
        "Số liệu thô. Cả năm đường đều tiến bộ rõ so với lúc khởi tạo.")
simple(s, 0.55, 5.52, 6.40, 1.34,
       "Chín trên mười cặp thuật toán tách được nhau ở đây. Đó là lý do Cross The Road là môi trường cho "
       "phép so sánh sạch nhất trong ba môi trường của đồ án.",
       sz=13.5, c=NAVY, b=True, line=1.14)

chip(s, 7.28, 1.16, "Kết quả năm thuật toán", sz=13.5, h=0.36)
table(s, 7.28, 1.64, 5.52, 1.98, [
    ["Thuật toán", "Reward TB", "Bước hội tụ", "Độ dài lượt"],
    ["PPO", "0,690", "~1,97M", "811,6"],
    ["SAC", "0,846", "~1,79M", "61,8"],
    ["MA-POCA", "0,556", "~450K", "42,2"],
    ["MAPPO", "0,835", "~1,72M", "52,0"],
    ["DQN", "0,336", "Không đạt", "124,7"],
], col_w=[1.5, 1.1, 1.1, 1.1], hsz=12, bsz=12.5, row_h=0.33,
    first_col_color=alg_color)

for i, (h, b) in enumerate([
    ("Hội tụ sớm không đồng nghĩa với học nhanh",
     "MA-POCA ổn định sớm nhất, khoảng 450.000 bước, nhưng chốt ở 0,556 rồi nằm im. Đó là sự ổn định "
     "của một chính sách tầm thường."),
    ("MAPPO vượt PPO ngay ở môi trường ĐƠN tác nhân",
     "0,835 so với 0,690, dù phê bình tập trung lẽ ra vô hiệu khi nhóm chỉ có một thành viên. "
     "Đồ án chưa giải thích được cơ chế."),
]):
    y = 3.86 + i * 1.54
    card(s, 7.28, y, 5.52, 1.44)
    oval(s, 7.50, y + 0.18, 0.30, fill=NAVY, label=str(i + 1), sz=11)
    textbox(s, 7.92, y + 0.14, 4.64, 1.16, [
        {"runs": [(h, {"sz": 13.5, "b": True, "c": NAVY})], "line": 1.02, "space_after": 3},
        {"runs": [(b, {"sz": 12.5, "c": INK})], "line": 1.06}])
notes(s, "Cross The Road là môi trường phân biệt tốt nhất. Cả năm đường đều tiến bộ rõ so với lúc khởi "
         "tạo, nên môi trường học được, và phổ kết quả trải từ 0,846 của SAC xuống 0,336 của DQN. Chín "
         "trên mười cặp thuật toán tách được nhau. Hai điểm em muốn nêu: MA-POCA hội tụ sớm nhất, khoảng "
         "450.000 bước, nhưng chốt ở 0,556 rồi nằm im — đó là sự ổn định của một chính sách tầm thường, "
         "không phải học nhanh. Và MAPPO vượt PPO ngay ở môi trường đơn tác nhân, điều mà đồ án chưa "
         "giải thích được cơ chế.")

# ================================================== 17. LUẬN ĐIỂM RÚT RA =======
s = new_slide_t("Luận điểm rút ra từ kết quả")
chip(s, 0.55, 1.16, "Điều mà dữ liệu ủng hộ chắc chắn nhất")

card(s, 0.55, 1.76, 6.05, 2.72)
simple(s, 0.81, 1.96, 5.53, 0.32, "CÙNG MỘT THUẬT TOÁN, HAI MÔI TRƯỜNG",
       sz=12.5, b=True, c=ORANGE, wrap=False)
simple(s, 0.81, 2.34, 5.53, 0.30, "SAC trên Cross The Road và Capture The Flag",
       sz=13, c=MUTED, wrap=False)
textbox(s, 0.81, 2.70, 5.53, 0.80, [
    {"runs": [("0,846", {"sz": 40, "b": True, "c": NAVY}),
              ("     →     ", {"sz": 26, "c": MUTED}),
              ("0,183", {"sz": 40, "b": True, "c": RGBColor(0xC0, 0x39, 0x2B)})],
     "align": "c", "line": 1.0}])
simple(s, 0.81, 3.56, 5.53, 0.72,
       "Cùng một thuật toán, cùng phần cứng, cùng đường ống đo. Chênh lệch 0,663 sinh ra hoàn toàn "
       "từ đặc tính bài toán mà thiết kế môi trường quyết định.", sz=13, c=INK, line=1.08)

card(s, 6.75, 1.76, 6.05, 2.72)
simple(s, 7.01, 1.96, 5.53, 0.32, "BỐN THUẬT TOÁN, CÙNG MỘT MÔI TRƯỜNG",
       sz=12.5, b=True, c=ORANGE, wrap=False)
simple(s, 7.01, 2.34, 5.53, 0.30, "Nhóm giải được câu đố Capture The Flag",
       sz=13, c=MUTED, wrap=False)
textbox(s, 7.01, 2.70, 5.53, 0.80, [
    {"runs": [("0,800", {"sz": 40, "b": True, "c": NAVY}),
              ("     –     ", {"sz": 26, "c": MUTED}),
              ("0,840", {"sz": 40, "b": True, "c": NAVY})],
     "align": "c", "line": 1.0}])
simple(s, 7.01, 3.56, 5.53, 0.72,
       "PPO, MA-POCA, MAPPO và DQN nằm gọn trong dải rộng 0,040 — nhỏ hơn khoảng cách giữa hai môi "
       "trường tới mười sáu lần.", sz=13, c=INK, line=1.08)

round_rect(s, 0.55, 4.62, 12.25, 0.76, fill=CARD2, adj=0.16)
textbox(s, 0.75, 4.62, 11.85, 0.76, [
    {"runs": [("0,663", {"sz": 21, "b": True, "c": ORANGE}),
              ("   chênh lệch do môi trường     so với     ", {"sz": 15, "c": INK}),
              ("0,040", {"sz": 21, "b": True, "c": NAVY}),
              ("   chênh lệch do thuật toán", {"sz": 15, "c": INK})],
     "align": "c", "line": 1.0}], anchor="c")

callout(s, 0.55, 5.54, 12.25, 1.30)
textbox(s, 0.82, 5.70, 11.71, 1.00, [
    {"runs": [("Hàm ý cho người làm game:  ", {"sz": 14, "b": True, "c": ORANGE}),
              ("cơ chế game trước, thuật toán sau. Chọn sai thuật toán cho một cơ chế game thiệt hại "
               "lớn hơn nhiều so với cái lợi của việc chọn đúng thuật toán tốt nhất trong nhóm khả dụng.",
               {"sz": 14})], "line": 1.10, "space_after": 4},
    {"runs": [("Ba phân tách vững:  ", {"sz": 13, "b": True, "c": NAVY}),
              ("SAC thất bại ở Capture The Flag  ·  DQN cuối bảng ở Cross The Road  ·  nhóm dẫn đầu "
               "tách khỏi nhóm sau ở Cross The Road. Thứ tự trong nội bộ nhóm dẫn đầu chưa phải kết luận.",
               {"sz": 13, "c": MUTED})], "line": 1.06}])
notes(s, "Đây là luận điểm trung tâm của đồ án. Nhìn vào cùng một thuật toán là SAC: nó dẫn đầu Cross The "
         "Road với 0,846 rồi sụp xuống 0,183 ở Capture The Flag, chênh lệch 0,663. Còn bốn thuật toán "
         "cùng giải được Capture The Flag thì nằm gọn trong dải 0,040. Chênh lệch do môi trường lớn gấp "
         "mười sáu lần chênh lệch do thuật toán. Hàm ý thực tiễn: khi làm game, hãy lo cơ chế và đặc tả "
         "trước, chọn thuật toán sau. Em cũng xin nói rõ chỉ ba phân tách là thực sự vững, thứ tự trong "
         "nội bộ nhóm dẫn đầu thì chưa.")

# ============================================== 15. SẢN PHẨM TRIỂN KHAI & DEMO =
s = new_slide_t("Sản phẩm triển khai và ứng dụng demo")
chip(s, 0.55, 1.16, "Gói môi trường dùng lại được và ứng dụng trình diễn 15 mô hình")

picture_plate(s, 0.55, 1.76, 6.55, 3.76, os.path.join(IMG, "app_menu_main.png"), pad=0.14)
caption(s, 0.55, 5.58, 6.55,
        "Tab CHƠI: khung xem trước 3D, lưới chọn chế độ và danh mục mô hình nạp từ thư mục Resources.")

card(s, 0.55, 6.02, 6.55, 0.84)
textbox(s, 0.79, 6.02, 6.07, 0.84, [
    {"runs": [("Danh mục mô hình và dữ liệu biểu đồ trong ứng dụng sinh ra từ cùng một kịch bản với "
               "phần kết quả, nên số liệu trên slide và trong demo luôn khớp nhau.",
               {"sz": 12.5, "c": INK})], "line": 1.08}], anchor="c")

_prod = [
    ("Gói Unity Package Manager",
     "Ba môi trường, 15 cấu hình đã chạy thật, bộ công cụ Editor và trình hướng dẫn cài đặt bảy bước."),
    ("Ứng dụng demo nạp ONNX",
     "15 mô hình đã huấn luyện được nạp tại thời gian chạy, chọn trực tiếp từ menu, không cần dựng lại."),
    ("Ba chế độ chơi",
     "Người chơi tự điều khiển · agent tự chơi · người và agent trong cùng một phiên."),
    ("Hai tab số liệu",
     "THÔNG SỐ và SO SÁNH đọc thẳng kết quả huấn luyện, vẽ lại đường cong của cả 15 lần chạy."),
]
for i, (h, b) in enumerate(_prod):
    y = 1.76 + i * 1.24
    card(s, 7.32, y, 5.48, 1.12)
    textbox(s, 7.56, y, 5.00, 1.12, [
        {"runs": [(h, {"sz": 14.5, "b": True, "c": NAVY})], "line": 1.0, "space_after": 3},
        {"runs": [(b, {"sz": 12.5, "c": INK})], "line": 1.06}], anchor="c")

simple(s, 7.32, 6.58, 5.48, 0.30,
       "Quan sát hành vi thật phát hiện lỗi đặc tả mà đường cong phần thưởng che giấu.",
       sz=12, i=True, c=MUTED, line=1.05, wrap=False)
notes(s, "Sản phẩm bàn giao gồm hai phần. Phần một là gói Unity Package Manager: ba môi trường, mười lăm "
         "cấu hình đã chạy thật, bộ công cụ Editor và trình hướng dẫn cài đặt bảy bước — người dùng lại "
         "không phải dựng lại gì. Phần hai là ứng dụng demo, nạp trực tiếp mười lăm mô hình ONNX, có ba "
         "chế độ chơi và hai tab số liệu. Em muốn nhấn mạnh giá trị của việc xem hành vi thật: có những "
         "lỗi đặc tả mà đường cong phần thưởng không lộ ra, nhưng nhìn tác nhân chạy thì thấy ngay.")

# ============================== 16. KẾT LUẬN, HẠN CHẾ, HƯỚNG PHÁT TRIỂN ========
s = new_slide_t("Kết luận, hạn chế và hướng phát triển")
chip(s, 0.55, 1.16, "Ba kết quả  ·  ba hạn chế  ·  ba hướng phát triển")

_cols = [
    ("KẾT QUẢ ĐẠT ĐƯỢC", NAVY, "✓", [
        ("Ba môi trường đã qua kiểm chứng",
         "Football Table, Capture The Flag và Cross The Road, mỗi môi trường chịu năm thuật toán khác nguyên lý."),
        ("Quy trình thiết kế và nghiệm thu",
         "Bốn nguyên tắc phần thưởng cùng ba lập luận định lượng: tỉ lệ 5 trên 1, ngưỡng 2,4%, ân hạn một giây."),
        ("Sản phẩm hoàn chỉnh",
         "Gói UPM kèm 15 cấu hình, trainer mở rộng cho MAPPO và DQN, và ứng dụng demo."),
    ]),
    ("HẠN CHẾ", RGBColor(0xC0, 0x39, 0x2B), "!", [
        ("Mỗi cấu hình chỉ chạy một seed",
         "Chưa tách được phần do bản chất thuật toán khỏi phần do may rủi của một lần khởi tạo. Nếu chỉ được sửa một điều, em sửa điều này."),
        ("Hai môi trường thiếu độ phân giải",
         "Football Table 1237–1260 và Capture The Flag 0,800–0,840 đều hẹp hơn dao động của chính đường cong."),
        ("Một ô nằm ngoài phép so sánh",
         "DQN trên Football Table chạy không có tự chơi nên không có chỉ số ELO."),
    ]),
    ("HƯỚNG PHÁT TRIỂN", RGBColor(0x27, 0x92, 0x4F), "→", [
        ("Chạy lại 15 tổ hợp trên nhiều seed",
         "Việc cần làm trước tiên, vì nó quyết định mọi kết luận về chênh lệch nhỏ."),
        ("Làm hai môi trường khó lên",
         "Thêm bài trong chương trình học hoặc buộc phối hợp chặt hơn, thay vì kéo dài thời lượng huấn luyện."),
        ("Kiểm chứng hai hiện tượng còn bỏ ngỏ",
         "Vì sao SAC sụp ở Capture The Flag, và vì sao MAPPO vượt PPO ngay ở môi trường đơn tác nhân."),
    ]),
]
for i, (h, c, mark, items) in enumerate(_cols):
    x = 0.55 + i * 4.15
    card(s, x, 1.76, 3.95, 4.30)
    simple(s, x + 0.26, 1.94, 3.43, 0.34, h, sz=15, b=True, c=c, wrap=False)
    _iy = 2.38
    for j, (ih, ib) in enumerate(items):
        oval(s, x + 0.26, _iy + 0.02, 0.30, fill=c, label=mark, sz=11)
        textbox(s, x + 0.66, _iy, 3.03, 1.16, [
            {"runs": [(ih, {"sz": 13, "b": True, "c": NAVY})], "line": 1.02, "space_after": 3},
            {"runs": [(ib, {"sz": 12, "c": INK})], "line": 1.06}])
        _iy += 1.20

callout(s, 0.55, 6.20, 12.25, 0.70)
simple(s, 0.82, 6.20, 11.71, 0.70,
       "Đóng góp chính không phải là một thuật toán mới, mà là ba môi trường kèm bằng chứng nghiệm thu "
       "và quy trình để dựng lại chúng.", sz=14, b=True, c=NAVY, align="c", anchor="c", wrap=False)
notes(s, "Tổng kết lại. Đồ án bàn giao ba môi trường đã qua kiểm chứng, một quy trình thiết kế và nghiệm "
         "thu, cùng sản phẩm demo hoàn chỉnh. Hạn chế lớn nhất em xin nêu trung thực: mỗi cấu hình mới chỉ "
         "chạy một seed, nên những chênh lệch sát nhau chưa đủ cơ sở thống kê. Hai môi trường Football "
         "Table và Capture The Flag cũng chưa đủ độ phân giải. Hướng phát triển ưu tiên là chạy lại trên "
         "nhiều seed, làm hai môi trường đó khó lên, và giải thích hai hiện tượng còn bỏ ngỏ.")

# ================================================================ 17. KẾT THÚC =
s = blank_title_slide()
round_rect(s, 1.80, 2.62, 9.73, 1.10, fill=None, line=RGBColor(0xF2, 0x9F, 0x5B), lw=1.25, adj=0.14)
simple(s, 2.05, 2.62, 9.23, 1.10,
       "Muốn học tăng cường trong game đáng tin cậy, cần đầu tư vào đặc tả và kiểm chứng "
       "môi trường trước khi tối ưu thuật toán.",
       sz=17, b=True, c=WHITE, align="c", anchor="c", line=1.16)
simple(s, 1.50, 4.06, 10.33, 0.62, "EM XIN CHÂN THÀNH CẢM ƠN",
       sz=32, b=True, c=WHITE, align="c", wrap=False)
simple(s, 2.00, 4.76, 9.33, 0.36, "sự lắng nghe của quý thầy cô trong hội đồng",
       sz=16, c=RGBColor(0xCF, 0xD8, 0xEC), align="c", wrap=False)
rect(s, 5.67, 5.34, 2.00, 0.02, fill=RGBColor(0xF2, 0x9F, 0x5B))
simple(s, 2.00, 5.58, 9.33, 0.36, "Kính mong nhận được góp ý của thầy cô để đồ án được hoàn thiện hơn.",
       sz=14, c=RGBColor(0xCF, 0xD8, 0xEC), align="c", wrap=False)
simple(s, 2.00, 6.16, 9.33, 0.36, "Văn Thị Minh Huyền  ·  22010329  ·  K16  ·  Khoa học máy tính",
       sz=14, b=True, c=WHITE, align="c", wrap=False)
notes(s, "Phần trình bày của em đến đây là hết. Thông điệp em muốn để lại: muốn học tăng cường trong game "
         "đáng tin cậy thì phải đầu tư vào đặc tả và kiểm chứng môi trường trước khi nghĩ tới việc tối ưu "
         "thuật toán. Em xin chân thành cảm ơn quý thầy cô đã lắng nghe và rất mong nhận được góp ý.")

# ------------------------------------------------------------------------ lưu
prs.save(OUT)
print("Đã ghi:", OUT, "-", len(prs.slides.__iter__.__self__._sldIdLst), "slide")
if OVERFLOW:
    print("\n[CẢNH BÁO TRÀN CHỮ]")
    for w in OVERFLOW:
        print(" -", w)
else:
    print("Không phát hiện tràn chữ theo ước lượng.")
