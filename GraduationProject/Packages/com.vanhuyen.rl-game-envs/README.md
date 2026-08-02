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

## MAPPO và DQN

Hai thuật toán này **không có sẵn** trong ML-Agents; chúng được đăng ký qua cơ chế
trainer plugin. Nếu chỉ dùng PPO / SAC / MA-POCA thì bỏ qua mục này. Hướng dẫn cài
plugin nằm trong Sample *Training Configs*.

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
