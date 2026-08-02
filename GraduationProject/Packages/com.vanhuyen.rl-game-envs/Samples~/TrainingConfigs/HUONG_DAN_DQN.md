# Hướng dẫn training DQN (thuật toán ngoài ML-Agents)

ML-Agents chỉ hỗ trợ sẵn PPO, SAC, MA-POCA. DQN được thêm vào qua cơ chế
**trainer plugin** chính thức của ML-Agents — plugin nằm ở
`ml-agents/ml-agents-trainer-plugin/mlagents_trainer_plugin/dqn/` và đăng ký
trainer type `dqn` với `mlagents-learn` qua entry point trong `setup.py`.

Plugin gốc của Unity chỉ là bản mẫu (1 nhánh action, có lỗi). Đã nâng cấp:

| Thay đổi | Lý do |
|---|---|
| Hỗ trợ **nhiều nhánh discrete** (branching DQN) | Football cần 8 nhánh × 3 mức |
| **Double DQN** (chọn action bằng online net trên `next_obs`, đánh giá bằng target net) | Bản gốc dùng argmax trên obs hiện tại — sai công thức |
| Sửa batch size trong `get_random_action` | Bản gốc lấy `len(inputs)` = số sensor, không phải batch |
| ONNX export: output deterministic = greedy | Bản gốc xuất `torch.randint` vào graph |
| Thêm `exploration_decay_steps` | Bản gốc hardcode 20000 bước |

## 0. Cài đặt (đã làm, chỉ cần khi tạo máy/env mới)

```powershell
conda activate mlagents
pip install --no-build-isolation -e C:\Users\Admin\Documents\GitHub\GraduationProject\ml-agents\ml-agents-trainer-plugin
```

Kiểm tra: `mlagents-learn` chấp nhận `trainer_type: dqn` (nếu chưa cài sẽ báo
`Invalid trainer type dqn`). Lưu ý: sau khi **sửa code plugin** không cần cài
lại (bản cài là editable `-e`).

## 1. Cross The Road

Action sẵn là discrete (1 nhánh × 4) — không cần đổi gì trong Unity.

```powershell
conda activate mlagents
cd C:\Users\Admin\Documents\GitHub\GraduationProject\GraduationProject
mlagents-learn config\ctr_dqn.yaml --run-id=ctr_dqn_v1
```

Khi hiện `Listening on port 5004`, mở scene
`Assets/CrossTheRoad/Scenes/CrossTheRoad.unity` và bấm **Play**.

## 2. Capture The Flag

Action sẵn là discrete (1 nhánh × 7) — không cần đổi gì trong Unity.

```powershell
mlagents-learn config\ctf_dqn.yaml --run-id=ctf_dqn_v1
```

Mở scene `Assets/Collaboration/Scenes/CaptureTheFlag.unity` và bấm **Play**.

Ghi chú cho báo cáo: DQN (cũng như SAC) là thuật toán single-agent, chỉ học từ
reward cá nhân (`AddReward` trong `EnvController`); group reward của
`SimpleMultiAgentGroup` chỉ POCA dùng được. Đây là một điểm so sánh hay giữa
các thuật toán trên môi trường hợp tác.

## 3. Football Table (cần 1 bước đổi trong Unity)

DQN không chạy được action liên tục, nên `FootballAgent.OnActionReceived` đã
được thêm chế độ rời rạc: mỗi nhánh 3 mức `{0,1,2}` → `{-1, 0, +1}` cho từng
kênh `[trượt, xoay] × 4 thanh`.

**Trước khi train DQN**, trong scene `Assets/Football/Football.unity`, với **cả
hai** agent (2 team) sửa `Behavior Parameters > Actions`:

- `Continuous Actions`: `8` → `0`
- `Discrete Branches`: `0` → `8`, mỗi branch size = `3`

```powershell
mlagents-learn config\football_dqn.yaml --run-id=football_dqn_v1
```

Mở `Football.unity` và bấm **Play**. Config đã bật self-play giống bản SAC.

**Sau khi train xong, đổi Behavior Parameters về lại 8 continuous** để các
model PPO/SAC cũ và chế độ người chơi trong GameHub hoạt động bình thường.
(Nếu quên đổi mà chạy nhầm config liên tục, trainer sẽ báo lỗi rõ ràng —
plugin có kiểm tra action space.)

## 4. Theo dõi và kết quả

```powershell
tensorboard --logdir results
```

- Model ONNX: `results\<run-id>\<BehaviorName>.onnx` (xuất khi dừng training
  bằng Ctrl+C hoặc đạt `max_steps`).
- Train tiếp: thêm `--resume`. Train lại từ đầu cùng run-id: `--force`.
- Epsilon (mức khám phá) xem ở TensorBoard: `Policy/epsilon`.

Model DQN của Football khi đưa vào GameHub cần agent ở chế độ Behavior
Parameters rời rạc (8 nhánh × 3) thì mới chạy inference đúng.

## 5. Tinh chỉnh nếu cần

- Học chậm/không hội tụ: tăng `exploration_decay_steps` (khám phá lâu hơn),
  hoặc giảm `learning_rate` xuống `1.0e-4`.
- Loss dao động mạnh: giảm `tau` xuống `0.001` (target net cập nhật chậm hơn).
- Máy yếu/replay chiếm RAM: giảm `buffer_size`.
