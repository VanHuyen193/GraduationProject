# -*- coding: utf-8 -*-
"""Sửa các lỗi phát hiện khi soát lại nội dung, và thêm trích dẫn cho phần bối cảnh."""
import pathlib, re

p = pathlib.Path("build_v6.py")
s = p.read_text(encoding="utf-8")


def span(a, b, new, label):
    """Thay đoạn từ mốc a tới mốc b (kể cả b) bằng new."""
    global s
    i = s.index(a)
    j = s.index(b, i) + len(b)
    s = s[:i] + new + s[j:]
    print("  đã sửa:", label)


# ---------------------------------------------------------------- slide 2: chỗ cho dòng trích dẫn
s = s.replace("stat_tile(s, L_X + i * 3.24, 5.44, 3.06, 1.44, num, lab, nsz=34, lsz=12.5)",
              "stat_tile(s, L_X + i * 3.24, 5.44, 3.06, 1.30, num, lab, nsz=34, lsz=12.5)")
s = s.replace("R_X, R_W = 7.15, 5.65\ncard(s, R_X, 1.30, R_W, 5.58)",
              "R_X, R_W = 7.15, 5.65\ncard(s, R_X, 1.30, R_W, 5.44)")
span('simple(s, R_X + 0.24, 6.16, R_W - 0.48, 0.56,',
     'sz=12.5, b=True, c=NAVY, align="c", line=1.08)',
     '''simple(s, R_X + 0.24, 6.10, R_W - 0.48, 0.56,
       "Người phát triển vẫn phải đặc tả cả ba ô — và đặc tả sai thì không có báo lỗi nào.",
       sz=12.5, b=True, c=NAVY, align="c", line=1.08)
caption(s, 0.55, 6.80, 12.25,
        "Nguồn: D. Isla, GDC 2005 (cây hành vi trong Halo 2)  ·  Yannakakis & Togelius, "
        "Artificial Intelligence and Games, Springer 2018  ·  Wurman et al., Nature 602:223–228, 2022",
        sz=10.5)''',
     "slide 2 — dòng trích dẫn")

# ---------------------------------------------------------------- slide 6: dẫn nguồn định lý shaping
s = s.replace('("F · định hình thế năng", "F = γΦ(s′) − Φ(s), không đổi lời giải tối ưu")',
              '("F · định hình thế năng", "F = γΦ(s′) − Φ(s) — bất biến chính sách (Ng và cs., 1999)")')

# ---------------------------------------------------------------- slide 7: lập luận tỉ lệ 5 trên 1
span("Bây giờ là phần em muốn giải thích kỹ, vì trên slide chỉ ghi con số.",
     "ngưỡng đó tụt xuống đúng bằng không, nghĩa là tấn công luôn đáng thử.",
     """Bây giờ là phần em muốn giải thích kỹ, vì trên slide chỉ ghi con số. Vì sao thưởng ghi bàn
là cộng năm còn phạt thủng lưới chỉ trừ một, thay vì để hai giá trị bằng nhau? Hãy xét tình huống
tác nhân phải chọn giữa cầm cự — giữ bóng cho tới hết lượt chơi — và dứt điểm, tức tổ chức một pha
tấn công thành công với xác suất p và bị phản công thủng lưới với xác suất một trừ p. Cầm cự tới
hết ba nghìn bước thì gánh trọn khoản phạt thời gian, nên giá trị của nó bằng âm một. Dứt điểm có
giá trị kỳ vọng bằng p nhân phần thưởng ghi bàn, trừ đi một trừ p nhân hình phạt thủng lưới. So
sánh hai vế, tấn công chỉ đáng hơn cầm cự khi p vượt một ngưỡng bằng hình phạt thủng lưới trừ một,
chia cho tổng của thưởng và phạt. Với cấu hình đối xứng cộng năm trừ năm, ngưỡng ấy bằng không phẩy
bốn: tác nhân chỉ chịu tấn công khi tự tin thắng ít nhất bốn mươi phần trăm số pha bóng — điều gần
như không bao giờ đúng ở đầu huấn luyện — nên chính sách hội tụ về phòng ngự tuyệt đối và tín hiệu
học biến mất. Đổi sang cộng năm trừ một, ngưỡng tụt xuống đúng bằng không, nghĩa là mọi cơ hội ghi
bàn dù nhỏ đến mấy cũng đáng thử. Phép tính này còn cho thấy khoản phạt thời gian chẳng phải chi
tiết phụ, mà chính là thứ quyết định dấu của ngưỡng.""",
     "slide 7 — lập luận 5:1")

# ---------------------------------------------------------------- slide 8: nguồn gốc vận tốc 17,5
s = s.replace("Vận tốc tối đa của tác nhân là mười bảy phẩy năm đơn vị mỗi giây.",
              """Vận tốc tối đa của tác nhân là mười bảy phẩy năm đơn vị mỗi
giây, suy ra từ thế cân bằng giữa lượng vận tốc cộng thêm mỗi bước vật lý là một phẩy bốn và hệ số
cản tuyến tính bằng bốn — lấy một phẩy bốn chia cho tích của bốn với hai phần trăm giây.""")

# ---------------------------------------------------------------- slide 16: DQN là off-policy
s = s.replace("DQN là học giá trị ngoại tuyến",
              "DQN học hàm giá trị theo hướng off-policy với bộ nhớ phát lại")

# ---------------------------------------------------------------- slide 4: nói rõ 4.0.2 là bản gói Unity
s = s.replace("Bản phát hành ML-Agents 4.0.2 chỉ đăng ký sẵn ba trainer là ppo, poca và sac.",
              """Gói Unity ML-Agents bản 4.0.2 đi kèm phía Python chỉ đăng ký sẵn
ba trainer là ppo, poca và sac.""")

p.write_text(s, encoding="utf-8")
print("xong")
