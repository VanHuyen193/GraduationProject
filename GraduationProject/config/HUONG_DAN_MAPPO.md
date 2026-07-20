# Hướng dẫn training MAPPO (thuật toán ngoài ML-Agents)

MAPPO (Multi-Agent PPO — Yu et al. 2022, "The Surprising Effectiveness of PPO
in Cooperative Multi-Agent Games") được thêm qua **trainer plugin** giống DQN,
tại `ml-agents/ml-agents-trainer-plugin/mlagents_trainer_plugin/mappo/`.

## MAPPO khác gì PPO và MA-POCA?

| | PPO | **MAPPO** | MA-POCA |
|---|---|---|---|
| Critic | V(obs riêng từng agent) | **V(obs CẢ NHÓM)** — centralized | V(obs cả nhóm) — centralized |
| Advantage | GAE so với V riêng | **GAE so với V tập trung** | λ-return − counterfactual baseline |
| Credit assignment | không | mức nhóm | mức từng agent (marginalize action) |
| Group reward | không dùng | **có** | có |

Triển khai: kế thừa POCA (dùng lại `MultiAgentNetworkBody` — critic tập trung
với self-attention trên obs của cả nhóm, hỗ trợ group reward +
groupmate reward), nhưng **bỏ counterfactual baseline**: advantage =
λ-return − centralized value, loss chỉ còn policy + value + entropy.
Đây chính là điểm khác biệt thuật toán giữa MAPPO và MA-POCA — một phép
so sánh ablation đẹp cho đồ án.

Giới hạn: plugin không hỗ trợ memory/LSTM (sẽ báo lỗi rõ nếu config có
`network_settings.memory`).

## Training

Chỉ áp dụng cho **Capture The Flag** — môi trường multi-agent duy nhất có
`SimpleMultiAgentGroup`. (Trên CrossTheRoad/Football, MAPPO suy biến thành
PPO thường vì nhóm chỉ có 1 agent.)

```powershell
conda activate mlagents
cd C:\Users\Admin\Documents\GitHub\GraduationProject\GraduationProject
mlagents-learn config\ctf_mappo.yaml --run-id=ctf_mappo_v1
```

Mở scene `Assets/Collaboration/Scenes/CaptureTheFlag.unity` và bấm **Play**.
Không cần đổi gì trong Unity — action space giữ nguyên discrete 7.

Hyperparameter trong `ctf_mappo.yaml` giữ **giống hệt** `ctf_poca.yaml`
(batch, buffer, lr, epsilon, lambd...) để khác biệt kết quả chỉ đến từ
thuật toán, không phải từ tinh chỉnh.

- TensorBoard: `tensorboard --logdir results` — so sánh
  `Environment/Group Cumulative Reward` giữa run poca / mappo / sac / ppo.
- Model ONNX xuất ra `results\ctf_mappo_v1\PuzzleBehavior.onnx` — dùng được
  ngay trong GameHub (actor giống hệt POCA, chỉ khác cách train critic).

## Lưu ý khi cài lại môi trường

Plugin cài một lần bằng:

```powershell
pip install --no-build-isolation -e ml-agents\ml-agents-trainer-plugin
```

Sau khi **sửa code** plugin thì không cần cài lại (editable install), nhưng
sau khi **thêm trainer mới vào setup.py** thì phải chạy lại lệnh trên để
đăng ký entry point.
