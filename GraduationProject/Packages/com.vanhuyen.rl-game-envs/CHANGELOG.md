# Changelog

## [1.0.0] — 2026-08-02

Phát hành lần đầu.

### Có gì
- Ba môi trường: Cross The Road (điều hướng, đơn tác nhân), Capture The Flag (hợp tác
  hai tác nhân, group reward), Football Table (đối kháng 1v1, self-play).
- Mười lăm cấu hình huấn luyện: PPO, SAC, MA-POCA, MAPPO, DQN trên cả ba môi trường.
- Setup Wizard bảy bước trong Editor, tự kiểm tra trạng thái từng bước.
- Công cụ nhân khu vực huấn luyện, build headless và sinh bản scene hành động rời rạc
  cho Football (dùng cho DQN).
- Giao diện `IManualActionSource` để gắn nguồn điều khiển thủ công mà không phải sửa
  mã môi trường.

### Lưu ý
- Art của Cross The Road không đi kèm vì giấy phép Asset Store; môi trường vẫn chạy
  và huấn luyện bình thường khi thiếu.
- MAPPO và DQN cần trainer plugin ngoài ML-Agents.
