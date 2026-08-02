# Hướng dẫn sử dụng

Tài liệu này đi sâu hơn `README.md`. Nếu chỉ muốn chạy thử thì mở
**Tools ▸ RL Game Environments ▸ Setup Wizard** và làm theo bảy bước ở đó.

## 1. Ba môi trường

### Cross The Road — điều hướng, đơn tác nhân
Tác nhân băng qua nhiều làn xe để tới đích. Bốn hành động rời rạc: đứng yên, trái,
phải, tiến. Phần thưởng thưa (chỉ khi tới đích hoặc bị đâm) nên môi trường này phân
biệt tốt khả năng khám phá của thuật toán.

Behavior name: `CrossTheRoad`.

### Capture The Flag — hợp tác, hai tác nhân
Hai tác nhân phải thay nhau đứng lên bàn đạp để mở cửa cho nhau đi qua, rồi cùng tới
checkpoint. Dùng `SimpleMultiAgentGroup` và group reward. Quan sát của mỗi tác nhân có
kèm trạng thái của đồng đội, nên bài toán gần Markov và không cần bộ nhớ hồi quy.

Behavior name: `PuzzleBehavior`.

### Football Table — đối kháng 1v1
Bi lắc bốn thanh gạt mỗi đội. Hành động liên tục tám kênh (trượt và xoay cho từng
thanh). Huấn luyện bằng self-play; hai đội dùng chung một behavior name nên ML-Agents
tự ghép cặp đối kháng.

Behavior name: `Football`. Có thêm bản `FootballDiscrete` với tám nhánh ba mức, dùng
cho DQN — sinh bằng **Tools ▸ Training ▸ Make FootballDiscrete Scene**.

## 2. Quy trình huấn luyện

```bash
# 1. Cài cấu hình (hoặc bấm nút ở bước 4 trong Setup Wizard)
#    -> config/*.yaml

# 2. Nhân khu vực huấn luyện: Tools ▸ Training ▸ Multiply Areas…
#    8 khu vực là điểm cân bằng tốt giữa tốc độ và bộ nhớ.

# 3. Build headless: Tools ▸ Training ▸ Build Training Envs
#    -> Builds/<Env>/<Env>.exe

# 4. Chạy
mlagents-learn config/ctr_ppo.yaml --run-id=ctr_ppo_01 \
    --env=Builds/CrossTheRoad/CrossTheRoad.exe --no-graphics

# 5. Theo dõi
tensorboard --logdir results
```

Muốn chạy nhiều tiến trình song song thì thêm `--num-envs=4`; việc này **bắt buộc**
phải có bản build ở bước 3.

### So sánh công bằng

Nếu mục đích là so sánh các thuật toán với nhau thì mọi lần chạy trên cùng một môi
trường phải dùng **cùng số khu vực huấn luyện** và cùng ngân sách bước. Số khu vực đổi
tức là số mẩu kinh nghiệm trên mỗi bước mô phỏng đổi theo.

## 3. Thêm cách điều khiển của riêng bạn

Xem `IManualActionSource` trong `README.md`. Ba điểm cần nhớ:

- Thành phần phải nằm **cùng GameObject** với `Agent`.
- Behavior Type phải là `HeuristicOnly` thì `Heuristic` mới được gọi.
- Nếu tác nhân chỉ ra quyết định sau mỗi vài bước vật lý (`DecisionRequester`) thì
  hãy đệm phím trong `Update` rồi tiêu thụ trong `WriteActions`, nếu không sẽ mất phím
  ở những khung hình không trùng bước quyết định.

Với Football Table, dùng `ManualActionSource.Write(actionsOut, values)` thay vì tự ghi:
hàm này lo giúp việc quy đổi khi brain đang ở chế độ rời rạc.

## 4. MAPPO và DQN

Hai thuật toán này không có trong ML-Agents. Chúng được cài qua cơ chế trainer plugin
(`mlagents.trainer_type` entry point). Cài plugin vào đúng môi trường Python đang chạy
`mlagents-learn`:

```bash
pip install --no-build-isolation -e <đường dẫn plugin>
```

Cần `--no-build-isolation` vì `setup.py` của plugin import `mlagents`.

Hai lưu ý từ thực nghiệm của đề tài:

- **MAPPO không hỗ trợ mạng hồi quy.** Khai báo `network_settings.memory` sẽ ném
  `UnityTrainerException` ngay lúc khởi tạo.
- **DQN không chạy được self-play.** Bật `self_play` sẽ làm `mlagents-learn` chết ở
  khâu khởi tạo ghost trainer. Cấu hình `football_dqn.yaml` vì thế đã tắt sẵn self-play,
  và điều đó có nghĩa là lần chạy DQN trên Football không so trực tiếp được bằng ELO
  với bốn thuật toán còn lại.

## 5. Art bên thứ ba

Cross The Road hiển thị bằng vài gói art miễn phí trên Unity Asset Store. Gói này
không kèm chúng (giấy phép Asset Store không cho phép phát hành lại). Thiếu art thì
scene vẫn chạy, vật lý và huấn luyện không đổi, chỉ là mesh không hiện.

Setup Wizard bước 3 liệt kê đúng những gói còn thiếu và mở thẳng trang tải.
