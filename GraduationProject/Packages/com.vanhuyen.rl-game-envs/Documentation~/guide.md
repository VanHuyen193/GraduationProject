# Hướng dẫn sử dụng

Tài liệu này đi sâu hơn `README.md`. Nếu chỉ muốn chạy thử thì mở
**Tools ▸ RL Game Environments ▸ Setup Wizard** và làm theo bảy bước ở đó.

## 0. Yêu cầu trước khi bắt đầu

- Unity 6 (`6000.0+`); dự án đã kiểm chứng dùng `6000.3.14f1`.
- Unity ML-Agents 4.0.2 và Unity Inference Engine 2.6.1.
- Khi huấn luyện: Python cùng bộ ML-Agents tương thích, PyTorch; GPU CUDA được khuyến
  nghị nhưng không bắt buộc.
- Cấu hình tham chiếu: Windows 11, Core i5-14600KF, RTX 3050, RAM 32 GB.

Gói không đặt một ngưỡng phần cứng tối thiểu tuyệt đối vì thông lượng phụ thuộc số khu vực,
độ phức tạp model và `time_scale`. Nếu RAM hoặc VRAM hạn chế, bắt đầu với 1–2 khu vực,
không bật nhiều tiến trình và theo dõi bộ nhớ trước khi tăng lên 8 khu vực.

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

Mỗi tổ hợp nên chạy nhiều seed độc lập. Không dùng các điểm liên tiếp trong một đường
TensorBoard như các mẫu độc lập; độ lệch chuẩn theo thời gian không thay thế phương sai
giữa seed. Riêng Football Table, ELO của các run self-play khác nhau dựa trên kho đối thủ
khác nhau. Hãy lưu checkpoint và cho mọi model đấu cùng một bộ đối thủ mốc, có đổi bên sân,
rồi báo cáo tỷ lệ thắng/hòa và chênh lệch bàn.

### Thời gian dự kiến trên cấu hình tham chiếu

| Môi trường | Ngân sách | On-policy (PPO/MA-POCA/MAPPO) | SAC | DQN |
|---|---:|---:|---:|---:|
| Cross The Road | 2,00M | 48–59 phút | 139 phút | 148 phút |
| Capture The Flag | 1,70M | 50–53 phút | ít nhất 152 phút* | 258 phút |
| Football Table | 1,60M | 47–50 phút | 165 phút | 147 phút |

\* Phiên SAC được khôi phục từ checkpoint; 152 phút chỉ là đoạn 1,0M–1,7M bước. Thời gian
không phải cam kết hiệu năng. Chạy trong Editor, bật đồ họa hoặc giảm số khu vực sẽ lâu hơn.

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

## 6. Kiểm tra trước khi đưa vào dự án khác

1. Tạo một dự án Unity 6 sạch và cài package từ disk hoặc Git URL.
2. Mở Setup Wizard, xác nhận hai dependency và import từng sample.
3. Build một môi trường headless, chạy một smoke test ngắn và kiểm tra có tệp TensorBoard.
4. Nạp một ONNX hành động liên tục và một ONNX rời rạc; xác nhận số quan sát/hành động khớp.
5. Xuất `training_data.json`, kiểm tra menu đọc đủ thuật toán và xử lý được mục thiếu.
6. Build player độc lập, chạy luồng vào scene, quay lại menu và theo dõi log ngoài Editor.

Hiện các bước này là checklist thủ công; package chưa kèm pipeline CI hay bộ PlayMode test
ngoài Editor. Không nên xem việc scene chạy trong dự án gốc là bảo đảm tự động cho nền tảng
hoặc phiên bản Unity khác.

## 7. Giới hạn tái sử dụng

- Các cấu hình và model đi kèm là mốc tham khảo một seed, không phải chứng nhận thuật toán
  tốt nhất cho môi trường.
- DQN trên Football Table phải dùng `FootballDiscrete` và không so trực tiếp với bốn run
  self-play liên tục.
- MAPPO/DQN cần trainer plugin Python riêng; UPM package chỉ cung cấp phía Unity và YAML.
- Thay đổi `Behavior Name`, kích thước quan sát, nhánh hành động hoặc kiến trúc mạng làm
  model ONNX cũ không tương thích.
- Capture The Flag có model lớn do kiến trúc điều kiện hóa mục tiêu; cần dự trù dung lượng
  phát hành hoặc huấn luyện lại với kiến trúc khác.
- Cross The Road cần tải art Asset Store bằng tài khoản của người dùng nếu muốn đủ hình ảnh.
- Tính tương thích hiện mới được kiểm chứng trên Windows với phiên bản nêu trên; cần chạy
  lại checklist ở Mục 6 cho macOS, Linux, mobile hoặc console.
