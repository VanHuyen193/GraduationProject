# -*- coding: utf-8 -*-
import io, pathlib, sys

p = pathlib.Path("build_v6.py")
s = p.read_text(encoding="utf-8")
orig = s

# 1. tiêu đề slide
s = s.replace('s = new_slide_t("Bối cảnh — phần khó không nằm ở thuật toán")',
              's = new_slide_t("Bối cảnh — từ logic viết tay tới học tăng cường")')

# 2. ba thẻ nội dung bên trái
old_cards = '''_cards = [("Thuật toán là tài sản dùng chung", "có sẵn trong thư viện, đổi bằng một tệp YAML"),
          ("Môi trường là tài sản riêng", "đổi cơ chế game thì gần như không kế thừa được gì"),
          ("Đặc tả sai không báo lỗi", "chương trình vẫn chạy, đường cong vẫn được vẽ ra")]'''
new_cards = '''_cards = [("Hiện nay NPC chạy bằng logic viết tay",
           "máy trạng thái, cây hành vi, luật if – else"),
          ("Được việc, nhưng hành vi cứng nhắc",
           "NPC lặp đúng kịch bản đã lường trước; người chơi đoán ra rồi khai thác"),
          ("Học tăng cường sinh hành vi từ tương tác",
           "đổi lại, phần khó chuyển sang khâu đặc tả môi trường")]'''
assert old_cards in s
s = s.replace(old_cards, new_cards)

# 3. nhãn hai ô số liệu
s = s.replace('("30+", "trang thiết kế ba môi trường")',
              '("30+", "trang đặc tả ba môi trường")')

# 4. dòng chốt dưới sơ đồ vòng lặp
old_line = '''       "Người thiết kế môi trường quyết định cả ba ô, và chỉ ô dưới cùng định nghĩa mục tiêu.",'''
new_line = '''       "Người phát triển vẫn phải đặc tả cả ba ô — và đặc tả sai thì không có báo lỗi nào.",'''
assert old_line in s
s = s.replace(old_line, new_line)

# 5. kịch bản nói
i = s.index('notes(s, """Học tăng cường cho game thường được kể')
j = s.index('""")', i) + len('""")')
body = pathlib.Path("_newnotes2.txt").read_text(encoding="utf-8").strip()
s = s[:i] + 'notes(s, """' + body + '""")' + s[j:]

assert s != orig
p.write_text(s, encoding="utf-8")
print("đã vá slide 2")
