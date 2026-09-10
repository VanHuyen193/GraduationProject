# -*- coding: utf-8 -*-
import pathlib
p = pathlib.Path("build_v6.py")
s = p.read_text(encoding="utf-8")

old4 = """Bảng ở giữa là điểm cần nói thêm về mặt kỹ thuật. Bản phát hành ML-Agents 4.0.2 chỉ đăng ký sẵn ba
trainer là ppo, poca và sac."""
new4 = """Bảng ở giữa là điểm cần nói thêm về mặt kỹ thuật. Gói Unity ML-Agents bản 4.0.2, cùng với phía
Python đi kèm, chỉ đăng ký sẵn ba trainer là ppo, poca và sac."""
assert old4 in s
s = s.replace(old4, new4)

# slide 2: bổ sung ngoại lệ GT Sophy và nguồn vào kịch bản nói
old2 = """Trong phần lớn dự án game, hành vi của NPC được lập trình bằng tay."""
new2 = """Trong phần lớn dự án game, hành vi của NPC được lập trình bằng tay."""
assert old2 in s

anchor = """chưa xuất hiện trong quy trình sản xuất thông thường."""
add = """chưa xuất hiện trong quy trình sản xuất thông thường. Em xin nói ngay là có ngoại lệ đáng kể:
GT Sophy của Sony AI, công bố trên tạp chí Nature năm 2022, được huấn luyện bằng học tăng cường sâu
và nay đã thành tính năng chính thức trong Gran Turismo 7. Nhưng đó là dự án của một phòng nghiên
cứu lớn, chưa phải quy trình phổ biến."""
assert anchor in s
s = s.replace(anchor, add, 1)

# ghi rõ nguồn ở cuối phần kịch bản slide 2
tail = """Đó cũng
là lý do đồ án của em đặt trọng tâm vào khâu xây dựng và kiểm chứng môi trường."""
new_tail = """Đó cũng
là lý do đồ án của em đặt trọng tâm vào khâu xây dựng và kiểm chứng môi trường.

[Nguồn ghi ở chân slide, phòng khi hội đồng hỏi: cây hành vi do Damian Isla trình bày tại GDC 2005
cho hệ thống AI của Halo 2; giáo trình Artificial Intelligence and Games của Yannakakis và Togelius,
Springer 2018, xếp máy trạng thái và cây hành vi vào nhóm "soạn hành vi thủ công"; GT Sophy công bố
trên Nature tập 602, trang 223–228, năm 2022.]"""
assert tail in s
s = s.replace(tail, new_tail)

p.write_text(s, encoding="utf-8")
print("xong")
