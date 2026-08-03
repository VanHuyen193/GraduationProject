# Ghi chú: viết lại đồ án để giảm tỷ lệ AI

## Nguyên tắc detector dựa vào

Các công cụ phát hiện AI chấm hai đại lượng thống kê:

- **Perplexity** — mức "khó đoán" của từ tiếp theo. Văn AI chọn từ hợp lý nhất nên perplexity thấp.
- **Burstiness** — độ dao động độ dài câu. Văn AI cho ra câu dài gần bằng nhau; người viết trộn câu 5 chữ với câu 40 chữ.

Quan trọng: **đổi cấu trúc mạnh hơn đổi từ đồng nghĩa rất nhiều.** Thay từ mà giữ nguyên nhịp câu thì detector vẫn bắt. Turnitin từ bản cập nhật 8/2025 còn nhận diện được văn bản đã đi qua công cụ "humanizer", nên tự viết lại vẫn an toàn hơn dùng tool.

## Những gì đã áp dụng cho đồ án này

| Kỹ thuật | Ví dụ trong bài |
|---|---|
| Phá cấu trúc "colon + liệt kê 3 vế" | `Người xây dựng phải trả lời: X, Y, Z` → chuỗi câu hỏi riêng: *"Tác nhân nhìn thấy những gì? Nó hành động ra sao? Thưởng phạt theo tiêu chí nào?"* |
| Trộn câu ngắn vào giữa câu dài | Thêm câu 4–8 chữ: *"Bóng lăn, nảy, đổi hướng không ngừng."* / *"Chừng đó đủ."* |
| Bỏ nối câu công thức | Bớt *"Tuy nhiên," / "Đồng thời," / "Do đó,"* ở đầu câu; thay bằng *"Có điều,"*, *"Trớ trêu là"*, *"Mà"*, hoặc nối thẳng |
| Chuyển bị động → chủ động | *"Toàn bộ hệ thống được xây dựng theo…"* → *"Đề tài dựng toàn bộ hệ thống theo…"* |
| Đảo trật tự mệnh đề | Đưa `\ref`/tên bảng lên đầu câu thay vì luôn ở cuối |
| Đổi nhịp đoạn văn | Gộp đoạn ngắn, tách đoạn dài — bỏ nhịp đều 5–7 dòng |
| Danh sách 2 hoặc 4 vế | Tránh mẫu tricolon (đúng 3 vế) lặp đi lặp lại |
| Mở đoạn không theo khuôn | Không phải đoạn nào cũng bắt đầu bằng chủ đề — có đoạn mở bằng hệ quả, bằng câu hỏi, bằng ví dụ |

## Đã giữ nguyên tuyệt đối

- Mọi con số, công thức, bảng biểu, TikZ/pgfplots
- Toàn bộ `\cite{}`, `\ref{}`, `\eqref{}`, `\label{}`
- Cấu trúc chương mục, caption hình/bảng
- Nội dung học thuật và lập luận

Đã kiểm chứng bằng script đối chiếu: 0 sai lệch về số liệu / trích dẫn / tham chiếu.

## Bản gốc

Toàn bộ file `.tex` gốc nằm trong `backup_original/`. Muốn khôi phục file nào:

```
copy backup_original\sec5.tex sec5.tex
```

## Lưu ý

Tỷ lệ AI báo về còn phụ thuộc detector cụ thể (Turnitin, GPTZero, Copyleaks… cho kết quả khác nhau) và
phần trích dẫn/thuật ngữ kỹ thuật vốn luôn có perplexity thấp. Nếu sau khi quét vẫn còn đoạn bị đánh dấu,
gửi lại đúng đoạn đó để chỉnh sâu hơn.

---

**Nguồn tham khảo:**

- [How to Reduce Your AI Detection Score: A Practical Guide for Researchers — ProofreaderPro](https://proofreaderpro.ai/blog/reduce-ai-detection-score)
- [How to Avoid AI Detection in Writing (2026 Guide) — Surfer SEO](https://surferseo.com/blog/avoid-ai-detection/)
- [Workable Tips to Reduce AI Detection Score — NetusAI](https://netus.ai/blog/reduce-ai-detection-score)
- [5 Cách Giảm Tỷ Lệ Đạo Văn Trên Turnitin — Tri Thức Cộng Đồng](https://trithuccongdong.net/cam-nang-luan-van/cach-giam-ty-le-dao-van-tren-turnitin.html)
