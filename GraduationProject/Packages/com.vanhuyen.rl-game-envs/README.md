# RL Game Environments

Ba môi trường game 3D dựng sẵn cho Unity ML-Agents, kèm cấu hình huấn luyện cho năm
thuật toán và bộ công cụ cài đặt trong Editor.

| Môi trường | Dạng bài toán | Số tác nhân | Không gian hành động |
|---|---|---|---|
| Cross The Road | Điều hướng, phần thưởng thưa | 1 | Rời rạc, 4 hành động |
| Capture The Flag | Hợp tác, group reward | 2 | Rời rạc, 7 hành động |
| Football Table | Đối kháng 1v1, self-play | 1 mỗi đội | Liên tục 8 kênh (có bản rời rạc 8×3) |

Mỗi môi trường đi kèm cấu hình cho **PPO, SAC, MA-POCA, MAPPO và DQN** — tổng cộng 15
tệp YAML đã chạy thật, không phải mẫu để trống.

## Yêu cầu

- Unity 6 (`6000.0` trở lên; dự án gốc dùng `6000.3.14f1`).
- `com.unity.ml-agents` 4.0.2 và `com.unity.ai.inference` 2.6.1. Package Manager cài
  hai gói này theo `package.json`.
- Python, ML-Agents Python package và PyTorch tương thích với ML-Agents 4.0.2 nếu cần
  huấn luyện. Kết quả của đồ án dùng PyTorch 2.2.2 và CUDA 12.1 trên Windows 11.
- Dung lượng trống phụ thuộc model và kết quả huấn luyện. Năm model Capture The Flag của
  dự án gốc chiếm khoảng 325 MB; thư mục `results/` có thể lớn hơn đáng kể.

Chạy suy luận không bắt buộc có GPU NVIDIA. Huấn luyện có thể chạy bằng CPU nhưng sẽ chậm;
các mốc thời gian bên dưới được đo trên Core i5-14600KF, RTX 3050 và 32 GB RAM, với 8 khu
vực huấn luyện song song và mô phỏng nhanh 20 lần thời gian thực.

## Cài đặt

Package Manager ▸ **+** ▸ *Add package from git URL…* hoặc *Add package from disk…* rồi
trỏ vào `package.json` của gói.

Sau đó mở **Tools ▸ RL Game Environments ▸ Setup Wizard**. Cửa sổ này đi qua bảy bước
và tự kiểm tra xem bước nào đã xong:

1. **Gói phụ thuộc** — `com.unity.ml-agents`, `com.unity.ai.inference`
2. **Import môi trường** — mỗi môi trường là một Sample trong Package Manager
3. **Art bên thứ ba** *(tuỳ chọn)* — xem mục [Giấy phép](#giấy-phép) bên dưới
4. **Cấu hình huấn luyện** — chép 15 tệp YAML ra `config/`
5. **Nhân khu vực huấn luyện** — đòn bẩy tốc độ 4–8×
6. **Build headless** — cần thiết nếu muốn chạy `--num-envs`
7. **Chạy huấn luyện** — lệnh mẫu, bấm nút để chép

## Bắt đầu nhanh

```bash
mlagents-learn config/ctr_ppo.yaml --run-id=ctr_ppo_01 \
    --env=Builds/CrossTheRoad/CrossTheRoad.exe --no-graphics
tensorboard --logdir results
```

Không có build thì bỏ `--env` và bấm Play trong Editor khi dòng
*"Start training by pressing the Play button"* hiện ra.

## Thời gian huấn luyện tham khảo

| Môi trường | Ngân sách | PPO / MA-POCA / MAPPO | SAC | DQN |
|---|---:|---:|---:|---:|
| Cross The Road | 2,00M bước | 48–59 phút | 139 phút | 148 phút |
| Capture The Flag | 1,70M bước | 50–53 phút | ít nhất 152 phút* | 258 phút |
| Football Table | 1,60M bước | 47–50 phút | 165 phút | 147 phút |

\* Số đo SAC chỉ bao gồm đoạn 1,0M–1,7M bước sau khi khôi phục checkpoint, nên không phải
thời gian đầy đủ từ đầu. Các số trên chỉ để lập kế hoạch; CPU/GPU, số training area,
`time_scale`, tần suất cập nhật và chế độ có đồ họa có thể làm thời gian thay đổi mạnh.

## MAPPO và DQN

Hai thuật toán này **không có sẵn** trong ML-Agents; chúng được đăng ký qua cơ chế
trainer plugin. Nếu chỉ dùng PPO / SAC / MA-POCA thì bỏ qua mục này. Hướng dẫn cài
plugin nằm trong Sample *Training Configs*.

## Giới hạn và phạm vi tái sử dụng

- Mỗi cấu hình trong đồ án mới được chạy với một seed. Các giá trị reward/ELO là kết quả
  tham khảo, không phải bảng xếp hạng thuật toán có ý nghĩa thống kê. Khi so sánh, hãy chạy
  nhiều seed và báo cáo phương sai giữa seed.
- ELO self-play của hai lần huấn luyện Football Table dùng hai kho đối thủ khác nhau, nên
  không so trực tiếp giá trị cuối. Nên đánh giá mọi model trước cùng một tập đối thủ mốc.
- DQN trên Football Table dùng scene rời rạc và không có self-play; luôn trình bày riêng.
- Sample Cross The Road không kèm art Asset Store. Thiếu art không đổi vật lý nhưng làm
  scene không có mesh hiển thị.
- MAPPO và DQN cần trainer plugin Python ngoài package Unity; cài đúng môi trường đang chạy
  `mlagents-learn`.
- Quy trình hiện được xác nhận thủ công trong Unity Editor trên Windows. Chưa có cam kết
  tương thích cho macOS/Linux, bản build headless của mọi Unity minor version, hoặc mọi
  model ONNX do người dùng tự cung cấp.
- Khi đổi quan sát, hành động, `Behavior Name` hoặc kiến trúc mạng, model cũ có thể không
  còn nạp được. Cần huấn luyện và xuất ONNX lại.

Trước khi phát hành sản phẩm, nên thử cài package vào một dự án sạch, import từng sample,
build player độc lập, nạp ít nhất một model liên tục và một model rời rạc, rồi kiểm tra dữ
liệu TensorBoard/JSON trên đúng nền tảng đích.

## Gắn cách điều khiển của riêng bạn

Ba môi trường không biết gì về ứng dụng đang nhúng chúng. Muốn thêm một nguồn điều
khiển thủ công (bàn phím, gamepad, kịch bản kiểm thử, LLM…) thì viết một
`MonoBehaviour` hiện thực `IManualActionSource` rồi gắn vào cùng GameObject với Agent:

```csharp
using Unity.MLAgents.Actuators;
using UnityEngine;
using VanHuyen.RLGameEnvs;

public class MyController : MonoBehaviour, IManualActionSource
{
    public void WriteActions(in ActionBuffers actionsOut)
    {
        var discrete = actionsOut.DiscreteActions;
        discrete[0] = Input.GetKey(KeyCode.W) ? 3 : 0;
    }
}
```

Hàm `Heuristic` của môi trường sẽ tự tìm thành phần này. Không có thành phần nào thì
môi trường quay về sơ đồ phím mặc định của nó. Với Football Table, dùng
`ManualActionSource.Write(actionsOut, values)` để khỏi phải tự xử lý việc brain đang ở
chế độ liên tục hay rời rạc.

## Giấy phép

Mã nguồn và cấu hình trong gói này phát hành theo giấy phép MIT (xem `LICENSE.md`).

Riêng môi trường Cross The Road **hiển thị** bằng vài gói art miễn phí trên Unity Asset
Store. Giấy phép Asset Store không cho phép phát hành lại nên gói này không kèm chúng.
Thiếu art thì môi trường vẫn chạy và huấn luyện hoàn toàn bình thường, chỉ là xe và
nhân vật không có hình. Setup Wizard (bước 3) kiểm tra và chỉ đúng trang tải.
