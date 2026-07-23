# BÁO CÁO TIẾN ĐỘ ĐỒ ÁN TỐT NGHIỆP

- **Đề tài:** Học tăng cường để tối ưu hóa khả năng tương tác của AI trong game
- **Sinh viên:** Văn Thị Minh Huyền — MSSV 22010329 — K16, Khoa học máy tính (Tài năng)
- **GVHD:** Th.S. Nguyễn Văn Sơn
- **Ngày báo cáo:** 16/07/2026

## 1. Những nội dung đã hoàn thành

**Về môi trường thực nghiệm:**
- Xây dựng xong 3 môi trường game 3D trên Unity ML-Agents, đại diện cho 3 dạng bài toán RL: Football Table (đối kháng 1v1), Cooperative Puzzle (hợp tác đa tác nhân), Cross The Road (điều hướng tránh vật cản).
- Thiết kế đầy đủ không gian quan sát, không gian hành động và hàm phần thưởng phù hợp với từng môi trường.

**Về huấn luyện và so sánh thuật toán:**
- Huấn luyện và so sánh 3 thuật toán PPO, SAC, MA-POCA theo 4 tiêu chí định lượng; kết quả cho thấy mỗi thuật toán phù hợp với một dạng bài toán (PPO + self-play cho đối kháng, SAC cho điều hướng đơn tác nhân, MA-POCA cho hợp tác).
- Tích hợp thành công SAC ra ngoài trainer có sẵn của ML-Agents thông qua Python Low-Level API (mlagents_envs) kết hợp Stable-Baselines3.
- Toàn bộ số liệu huấn luyện được ghi qua TensorBoard; đã tổng hợp vào báo cáo.

**Về ứng dụng trình diễn:**
- Hoàn thành ứng dụng trình diễn tương tác: menu chọn môi trường / chế độ chơi / mô hình; 3 chế độ chơi (Người chơi, Agent tự chơi, Chơi với Agent); nạp mô hình ONNX tại thời gian chạy; HUD trong game.
- Đã kiểm thử đầy đủ các luồng chức năng trong Unity Editor (tất cả các luồng đều Đạt); đóng gói sẵn 8 mô hình cho 3 môi trường.

**Về báo cáo viết:**
- Hoàn thành bản thảo đầy đủ: Mở đầu, Cơ sở lý thuyết, Thiết kế môi trường và phương pháp thực nghiệm, Kết quả thực nghiệm và đánh giá, Xây dựng ứng dụng trình diễn, Kết luận, Phụ lục A–E, Tài liệu tham khảo.
- Đã chỉnh sửa định dạng theo yêu cầu: bìa theo đúng mẫu của trường (khung viền, chữ dọc hai bên); sửa lỗi hiển thị sơ đồ Hình 5.1; gộp các phụ lục vào một mục PHỤ LỤC chung (chia Phụ lục A, B, C… bên trong); thay gạch ngang dài bằng gạch ngắn; bỏ in nghiêng các từ trong đoạn văn; đánh số mục Kết luận; thống nhất cỡ chữ danh mục từ viết tắt (13pt).

## 2. Những nội dung còn thiếu / cần hoàn thiện

1. **Thực nghiệm bổ sung:** một số tổ hợp thuật toán – môi trường chưa được huấn luyện đến số bước tối đa; các thực nghiệm mới chạy với 1 seed nên chưa đánh giá được phương sai giữa các lần chạy.
2. **Môi trường Cooperative Puzzle:** kết quả huấn luyện còn thấp so với hai môi trường còn lại; nếu còn thời gian sẽ tinh chỉnh thêm hàm phần thưởng hoặc áp dụng curriculum learning.
3. **Đóng gói ứng dụng:** ứng dụng trình diễn mới chạy trong Unity Editor, chưa đóng gói bản chạy độc lập (desktop/WebGL) để demo không cần cài Unity.
4. **Hoàn thiện báo cáo:** rà soát chính tả và trích dẫn toàn văn lần cuối; kiểm tra lại danh mục hình/bảng và mục lục sau các chỉnh sửa định dạng; in thử để kiểm tra bìa và lề.
5. **Chuẩn bị bảo vệ:** làm slide thuyết trình và kịch bản demo trực tiếp ứng dụng.

## 3. Kế hoạch dự kiến

- Tuần 3–4 tháng 7/2026: hoàn thiện các mục 1–3 ở trên (ưu tiên đóng gói bản demo độc lập).
- Đầu tháng 8/2026: hoàn thiện báo cáo, nộp bản chính thức và chuẩn bị slide bảo vệ.

Kính mong thầy góp ý về mức độ ưu tiên của các hạng mục còn thiếu để em tập trung hoàn thiện đúng hướng. Em cảm ơn thầy!
