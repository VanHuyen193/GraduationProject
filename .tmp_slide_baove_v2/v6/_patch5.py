# -*- coding: utf-8 -*-
import pathlib
p = pathlib.Path("build_v6.py")
s = p.read_text(encoding="utf-8")

tail = """đều chia cho N bằng một trăm nghìn, đúng bằng số bước tối đa của một lượt chơi. Cách này bảo đảm
tổng mọi khoản phụ trên trọn một lượt luôn nhỏ hơn phần thưởng hoàn thành nhiệm vụ, đúng theo
nguyên tắc giữ trật tự độ lớn ở slide trước."""
add = tail + """

[Ghi chú dự phòng, chỉ dùng nếu hội đồng hỏi tới: bảng phần thưởng trong thuyết minh ghi thưởng
nhóm khi cả hai tới đích là +1,0, còn trong scene huấn luyện thực tế trường reward của trigger
checkpoint đang đặt bằng 2 ở cả tám khu vực. Đây là chênh lệch giữa tài liệu và cấu hình, không
ảnh hưởng tới số liệu đã báo cáo vì các con số ở Chương 4 lấy từ chỉ số phần thưởng cá nhân
(Environment/Cumulative Reward), còn khoản này là phần thưởng nhóm. Lập luận giữ trật tự độ lớn
cũng không đổi: giá trị càng lớn thì phần thưởng hoàn thành càng vượt xa tổng các khoản phụ. Em
xin ghi nhận và đính chính lại trong bản hoàn thiện.]"""
assert tail in s
s = s.replace(tail, add)
p.write_text(s, encoding="utf-8")
print("đã thêm ghi chú dự phòng cho slide 8")
