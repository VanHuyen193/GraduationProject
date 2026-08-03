# HỆ THỐNG HÓA ĐỒ ÁN TỐT NGHIỆP

**Đề tài:** Học tăng cường để tối ưu hóa khả năng tương tác của AI trong game
**Sinh viên:** Văn Thị Minh Huyền — MSSV 22010329 — K16 — Khoa học máy tính (Tài năng)
**GVHD:** ThS. Nguyễn Văn Sơn — Trường Công nghệ Thông tin Phenikaa

> Tài liệu này hệ thống lại toàn bộ kiến thức nền, phương pháp và kết quả của đồ án, kèm phần chuẩn bị bảo vệ ở cuối. Mọi con số đều trích từ chính các file `.tex` của đồ án.

---

## MỤC LỤC

- [PHẦN 0 — Bản đồ tổng thể: đồ án này nói gì?](#phần-0--bản-đồ-tổng-thể-đồ-án-này-nói-gì)
- [PHẦN 1 — Nền tảng lý thuyết học tăng cường](#phần-1--nền-tảng-lý-thuyết-học-tăng-cường)
- [PHẦN 2 — Năm thuật toán](#phần-2--năm-thuật-toán)
- [PHẦN 3 — Unity ML-Agents](#phần-3--unity-ml-agents)
- [PHẦN 4 — Phương pháp luận thiết kế môi trường (phần lõi)](#phần-4--phương-pháp-luận-thiết-kế-môi-trường-phần-lõi)
- [PHẦN 5 — Ba môi trường: thiết kế chi tiết](#phần-5--ba-môi-trường-thiết-kế-chi-tiết)
- [PHẦN 6 — Triển khai kỹ thuật & thiết lập thực nghiệm](#phần-6--triển-khai-kỹ-thuật--thiết-lập-thực-nghiệm)
- [PHẦN 7 — Kết quả 15 lần chạy & cách đọc số liệu](#phần-7--kết-quả-15-lần-chạy--cách-đọc-số-liệu)
- [PHẦN 8 — Ứng dụng trình diễn & đóng gói UPM](#phần-8--ứng-dụng-trình-diễn--đóng-gói-upm)
- [PHẦN 9 — Kết luận, đóng góp, hạn chế](#phần-9--kết-luận-đóng-góp-hạn-chế)
- [PHẦN 10 — Chuẩn bị bảo vệ](#phần-10--chuẩn-bị-bảo-vệ)

---

# PHẦN 0 — Bản đồ tổng thể: đồ án này nói gì?

## 0.1. Luận điểm trung tâm (thuộc lòng câu này)

> **Trong một dự án RL cho game, phần khó không nằm ở thuật toán mà ở môi trường. Thuật toán đã có sẵn trong thư viện; môi trường thì phải tự dựng, tự đặc tả, tự hiệu chỉnh. Đồ án lấy chính khâu đó làm đối tượng nghiên cứu.**

Hệ quả trực tiếp của luận điểm này lên cách bố trí đồ án:

| Nếu đề tài là "so sánh thuật toán" | Nhưng đề tài thật sự là "xây môi trường" |
|---|---|
| Môi trường là công cụ, thuật toán là đối tượng | **Thuật toán là công cụ, môi trường là đối tượng** |
| Cần nhiều seed để xếp hạng thuật toán | Cần nhiều thuật toán khác nguyên lý để dò đặc tính môi trường |
| Sản phẩm là bảng xếp hạng | Sản phẩm là **gói UPM ba môi trường đã kiểm chứng** |

Câu chốt để trả lời khi bị hỏi "sao chỉ chạy 1 seed?": *5 thuật toán ở đây là **phép thử**, không phải **đối tượng** đánh giá.*

## 0.2. Ba tiêu chí nghiệm thu một môi trường

Đây là đóng góp phương pháp luận của đồ án. Không thể nghiệm thu môi trường bằng cách đọc mã nguồn — cách duy nhất là thả nhiều thuật toán khác nhau vào rồi xem chúng cư xử thế nào:

1. **Học được** — nếu *mọi* thuật toán đều thất bại → lỗi nằm ở đặc tả (quan sát thiếu / phần thưởng không dẫn đường), không phải ở thuật toán.
2. **Phân biệt được** — nếu *mọi* thuật toán đều đạt điểm tối đa → hoặc môi trường quá dễ, hoặc đang có **lối tắt**. Thứ hạng phải *giải thích được* bằng cơ chế bài toán.
3. **Không có lối tắt** — không lần chạy nào đạt phần thưởng sát trần mà lại không giải được nhiệm vụ khi quan sát trực tiếp.

**Kết quả nghiệm thu:** Cross The Road đạt cả 3. Capture The Flag đạt 3 (nhưng độ phân giải kém ở nhóm dẫn đầu). Football Table **chỉ đạt 2/3** — biên độ ELO quá hẹp để phân biệt các thuật toán. Đồ án thừa nhận thẳng điều này.

## 0.3. Phát hiện quan trọng nhất

> **Cùng một thuật toán, khoảng cách giữa hai môi trường luôn lớn hơn khoảng cách giữa các thuật toán trong cùng một môi trường.**

Bằng chứng số: SAC dẫn đầu Cross The Road với **0,846** rồi sụp xuống **0,183** ở Capture The Flag (chênh 0,663). Trong khi đó, chênh lệch giữa 4 thuật toán dẫn đầu ở Capture The Flag chỉ **0,04**, và ở Cross The Road nhóm dẫn đầu cách nhau **0,011**.

→ **Đặc tính bài toán (do thiết kế môi trường quyết định) chi phối kết quả mạnh hơn lựa chọn thuật toán.** Đó chính là lý do khâu xây môi trường đáng được đầu tư nhiều hơn mức thường thấy.

## 0.4. Cấu trúc 6 chương

| Chương | Tên | Vai trò |
|---|---|---|
| 1 | MỞ ĐẦU | Lý do, mục tiêu, khoảng trống nghiên cứu |
| 2 | CƠ SỞ LÝ THUYẾT | RL → Deep RL → 5 thuật toán → ML-Agents + **giới hạn của nó** |
| 3 | **THIẾT KẾ MÔI TRƯỜNG** | ⭐ Chương trọng tâm — 4 định nghĩa hình thức, 4 nguyên tắc reward, 3 môi trường |
| 4 | KIỂM CHỨNG QUA THỰC NGHIỆM | 15 lần chạy, đọc số liệu theo 3 tiêu chí nghiệm thu |
| 5 | ỨNG DỤNG TRÌNH DIỄN | Demo + đóng gói UPM — công cụ soi lỗi đặc tả |
| 6 | KẾT LUẬN | Đạt được, đóng góp, hạn chế, hướng phát triển |

Lưu ý bố cục: Chương 2 dành dung lượng lớn cho **giới hạn tích hợp** của ML-Agents — vì chính các giới hạn ấy (chứ không phải lựa chọn học thuật) quy định cách bố trí thực nghiệm ở Chương 3.

## 0.5. Năm mục tiêu nghiên cứu

1. ⭐ **Xây bộ môi trường** — 3 môi trường 3D phủ 3 dạng bài toán RL
2. ⭐ **Nghiên cứu quy trình thiết kế obs–action–reward** — *phần lõi học thuật*, gồm cả những phương án đã thất bại
3. ⭐ **Đóng gói thành sản phẩm dùng lại được** — gói UPM
4. Kiểm chứng bằng thực nghiệm đa thuật toán — lưới đầy đủ 5×3 = 15 lần chạy
5. Xây ứng dụng trình diễn để quan sát hành vi

(Ba mục tiêu đầu là trọng tâm.)

## 0.6. Khoảng trống nghiên cứu — hai mặt

Điểm chung của mọi công trình RL kinh điển (DQN/Atari, AlphaGo, OpenAI Five, AlphaStar): chúng **tiêu thụ** môi trường chứ không bàn tới việc **tạo ra** môi trường. Benchmark đã có người đặc tả sẵn, đóng góp khoa học nằm hết ở phía thuật toán.

- **Mặt 1 — Tri thức thiết kế.** Quá trình đi từ ý tưởng trò chơi tới đặc tả mà tác nhân học được rất hiếm khi được ghi lại, nhất là các phương án thất bại — vốn lại là phần dạy được nhiều nhất.
- **Mặt 2 — Hiện vật dùng lại được.** Môi trường 3D kèm tài liệu, cấu hình huấn luyện, công cụ cài đặt gần như không tồn tại; mỗi dự án lại dựng lại từ đầu.

---

# PHẦN 1 — Nền tảng lý thuyết học tăng cường

## 1.1. Vòng lặp RL và năm khái niệm

```
        hành động a_t
   ┌──────────────────────┐
   │                      ▼
[Agent]                [Environment]
   ▲                      │
   └──────────────────────┘
   trạng thái s_{t+1}, phần thưởng r_{t+1}
```

| Khái niệm | Ký hiệu | Trong đồ án này |
|---|---|---|
| **Agent** | — | Tác nhân điều khiển thanh gạt / nhân vật |
| **Environment** | — | Scene 3D dựng trong Unity |
| **State** | s ∈ 𝒮 | Vị trí, vận tốc, khoảng cách tới mục tiêu |
| **Action** | a ∈ 𝒜 | Rời rạc (lên/xuống/trái/phải) hoặc liên tục (lực theo x, y, z) |
| **Reward** | r_t ∈ ℝ | Thước đo **duy nhất** để agent biết quyết định tốt hay dở |

Quỹ đạo tương tác: τ = (s₀, a₀, r₀, s₁, a₁, r₁, …)

**Điểm cần nhấn:** hàm phần thưởng đặt sai sẽ dẫn tới hành vi ngoài ý muốn *ngay cả khi thuật toán hoạt động hoàn toàn đúng về mặt lý thuyết*. Đây là mấu chốt của cả đồ án.

## 1.2. Markov Decision Process (MDP)

MDP là bộ năm: **ℳ = (𝒮, 𝒜, 𝒫, ℛ, γ)**

- 𝒫(s′ | s, a): hàm chuyển trạng thái
- γ ∈ [0, 1): hệ số chiết khấu — γ càng gần 1, agent càng thiên về kế hoạch dài hạn

**Tính chất Markov (tính không nhớ):**

```
𝒫(s_{t+1} | s_t, a_t, s_{t-1}, a_{t-1}, …) = 𝒫(s_{t+1} | s_t, a_t)
```

**Tổng phần thưởng chiết khấu:**

```
G_t = Σ_{k=0}^{∞} γ^k · r_{t+k+1}
```

Ý nghĩa: giả thiết Markov là thứ giữ cho bài toán còn giải được — agent chỉ cần nhìn trạng thái hiện tại là ra được quyết định tối ưu, không phải lưu toàn bộ lịch sử.

## 1.3. Policy và Value Function

**Policy π** — chiến lược hành động:
- Tất định: π: 𝒮 → 𝒜
- Ngẫu nhiên: π(a | s) = P(A_t = a | S_t = s)

**Hàm giá trị trạng thái:**
```
V^π(s) = 𝔼_π[G_t | S_t = s] = 𝔼_π[Σ γ^k r_{t+k+1} | S_t = s]
```

**Hàm giá trị hành động (Q-function):**
```
Q^π(s, a) = 𝔼_π[G_t | S_t = s, A_t = a]
```

**Phương trình Bellman** (nền tảng của hầu hết thuật toán RL hiện đại):
```
V^π(s) = Σ_a π(a | s) · Q^π(s, a)
```

**Phương trình tối ưu Bellman:**
```
Q*(s, a) = 𝔼[ r_{t+1} + γ · max_{a′} Q*(s_{t+1}, a′) | S_t = s, A_t = a ]
```

Với không gian trạng thái lớn và liên tục (game 3D), không thể biểu diễn chính xác V^π hay Q^π dưới dạng bảng tra cứu → **động lực khai sinh Deep RL**.

## 1.4. Deep RL và ba nhóm thuật toán

Mạng nơ-ron đóng vai bộ xấp xỉ hàm tổng quát:
- f_θ: 𝒮 → ℝ (nếu là value function)
- f_θ: 𝒮 → Δ(𝒜) (nếu là policy)

| Nhóm | Mạng học gì | Ưu | Nhược | Đại diện |
|---|---|---|---|---|
| **Value-Based** | Q(s,a); policy suy ra bằng argmax | Tốt với hành động rời rạc | Bí khi hành động liên tục (không tối ưu max_a Q hiệu quả được) | DQN |
| **Policy-Based** | Trực tiếp π_θ(a\|s) | Xử lý cả rời rạc lẫn liên tục | Phương sai gradient cao → kém ổn định | PPO, MAPPO |
| **Actor-Critic** | Song song 2 mạng: actor học π, critic học V hoặc Q | Critic cấp tín hiệu học ổn định hơn | Phức tạp, nhiều mạng | SAC, MA-POCA |

**Kiến trúc mạng theo dạng dữ liệu:** vector số thực → MLP (đồ án dùng cái này); ảnh/dữ liệu không gian → CNN.

## 1.5. Phần thưởng tò mò nội tại — ICM

**Vấn đề:** trong môi trường phần thưởng thưa (Capture The Flag, Cross The Road), tác nhân tiêu hết giai đoạn đầu vào khám phá ngẫu nhiên mà chẳng nhận về tín hiệu hữu ích nào.

**Ý tưởng ICM** (Pathak và cộng sự, 2017): lấy **sai số dự đoán** làm phần thưởng nội tại — thưởng cao khi agent tới trạng thái mà mô hình nội tại của chính nó không dự đoán nổi.

**Cạm bẫy phải tránh:** *noisy TV problem* — agent bị hút vào yếu tố ngẫu nhiên vốn không thể dự đoán được. Vì thế ICM **không dự đoán trạng thái thô s_t** mà dự đoán **đặc trưng ẩn φ(s_t)** qua một mạng Encoder.

**Hai mạng con:**

*Inverse Model* — từ φ(s_t), φ(s_{t+1}) dự đoán hành động â_t:
```
L_inv = 𝔼[ −log P(â_t = a_t | φ(s_t), φ(s_{t+1})) ]
```
→ Tác dụng: ép Encoder φ **chỉ giữ lại phần thông tin liên quan tới hành động**, gạt bỏ nhiễu.

*Forward Model* — từ φ(s_t), a_t dự đoán φ̂(s_{t+1}):
```
L_fwd = ½ · ‖ φ̂(s_{t+1}) − φ(s_{t+1}) ‖²₂
```

**Phần thưởng tò mò:**
```
r_t^i = η · ½ · ‖ φ̂(s_{t+1}) − φ(s_{t+1}) ‖²₂
```

**Tổng hợp:** r_t = r_t^e + β · r_t^i, với **β = 0,02** trong đồ án — đủ nhỏ để tác nhân không quên mục tiêu chính.

---

# PHẦN 2 — Năm thuật toán

## 2.0. Bảng tổng hợp (học thuộc bảng này)

| Thuật toán | Loại policy | On/Off-policy | Đa tác nhân | Replay buffer | Entropy | Chia sẻ tham số | Độ phức tạp |
|---|---|---|---|---|---|---|---|
| **PPO** | Policy gradient | On-policy | Không native | Không | Không | Không | Thấp |
| **SAC** | Actor-Critic | Off-policy | Không native | **Có** | **Có (max entropy)** | Không | Trung bình |
| **MA-POCA** | Actor-Critic | On-policy | **Có (attention)** | Không | Không | Có | **Cao** |
| **MAPPO** | Policy gradient | On-policy | **Có (CTDE)** | Không | Không | **Có (bắt buộc)** | Trung bình |
| **DQN** | Hàm giá trị | Off-policy | Không native | **Có** | Không (ε-tham lam) | Không | Thấp |

**Năm thuật toán không xếp được thành thang bậc yếu→mạnh.** Chúng phân hóa theo **bốn trục độc lập**: (1) học cái gì, (2) lấy dữ liệu ra sao, (3) xử lý nhiều tác nhân thế nào, (4) mỗi bước cập nhật tốn bao nhiêu tính toán.

---

## 2.1. PPO — Proximal Policy Optimization

**Một câu:** *Chặn độ lớn thay đổi của policy trong từng bước cập nhật, để policy không nhảy quá đột ngột rồi suy giảm hiệu năng không phục hồi được.*

Schulman và cộng sự (2017), cải tiến của TRPO. Là **trainer on-policy mặc định** của Unity ML-Agents.

**Hàm mục tiêu clipped surrogate:**
```
L^CLIP(θ) = 𝔼_t[ min( r_t(θ)·Â_t ,  clip(r_t(θ), 1−ε, 1+ε)·Â_t ) ]
```
với r_t(θ) = π_θ(a_t|s_t) / π_θ_old(a_t|s_t) là tỷ lệ xác suất, ε ∈ [0.1, 0.2] (đồ án dùng **ε = 0,2**).

- `clip` ép r_t(θ) nằm trong [1−ε, 1+ε] → policy mới không lệch quá xa policy cũ
- `min` bảo đảm mục tiêu luôn là **cận dưới thận trọng** (pessimistic lower bound)

**GAE — Generalized Advantage Estimation:**
```
Â_t = Σ_{l=0}^{∞} (γλ)^l · δ_{t+l},    δ_t = r_t + γ·V(s_{t+1}) − V(s_t)
```
λ cân bằng bias–variance (đồ án dùng **λ = 0,95**).

Mỗi iteration: gom một batch → chạy nhiều epoch gradient trên chính batch đó (3–10, đồ án dùng **5**) → lấy batch mới.

| ✅ Ưu | ❌ Nhược |
|---|---|
| **Hiếm khi hỏng** — đặt sai learning rate chỉ làm chậm, không phá sập chính sách | **Hiệu quả mẫu thấp** — vứt sạch dữ liệu sau mỗi lần cập nhật |
| Chạy được cả rời rạc lẫn liên tục | Trong Unity, 1 bước tương tác đắt hơn nhiều 1 bước lan truyền ngược → đây là hạn chế nặng nhất |
| Có sẵn cơ chế self-play trong ML-Agents | |

**Vai trò trong đồ án:** mốc so sánh — mọi thuật toán khác đều đối chiếu với PPO.

---

## 2.2. SAC — Soft Actor-Critic

**Một câu:** *Tối đa hóa đồng thời cả tổng phần thưởng lẫn entropy của policy, để agent chịu thử nhiều hành động thay vì chốt sớm vào lựa chọn tham lam.*

Haarnoja và cộng sự (2018). Actor-critic **off-policy**, nguyên lý maximum entropy.

**Hàm mục tiêu:**
```
J(π) = 𝔼_{τ~π}[ Σ_t γ^t ( r(s_t, a_t) + α·ℋ(π(·|s_t)) ) ]
```
với ℋ(π(·|s_t)) = −𝔼_{a~π}[log π(a|s_t)] là entropy, α > 0 là **hệ số nhiệt độ**.

**Ba mạng nơ-ron:** 1 actor π_θ + 2 critic Q_φ1, Q_φ2 huấn luyện độc lập.

**Clipped double-Q** — chống overestimation:
```
Q_target(s_t, a_t) = r_t + γ · 𝔼_{a′~π}[ min_{i=1,2} Q_φi(s_{t+1}, a′) − α·log π_θ(a′|s_{t+1}) ]
```

| ✅ Ưu | ❌ Nhược |
|---|---|
| Replay buffer → hiệu quả mẫu cao hơn PPO **một bậc độ lớn** (trên môi trường điều hướng) | Phải nuôi **3 mạng** + buffer hàng trăm nghìn phần tử → lợi thế về số mẫu bị thu hẹp khi tính theo thời gian đồng hồ |
| Max-entropy chặn hội tụ sớm vào cực trị cục bộ | ⚠️ **Không đi cùng được với self-play** — đối thủ liên tục thay mới thì kinh nghiệm cũ trong buffer phản ánh những đối thủ không còn tồn tại, trở thành nhiễu |
| Chịu learning rate sai tốt hơn PPO | |

---

## 2.3. MA-POCA — Multi-Agent POsthumous Credit Assignment

**Một câu:** *Dùng critic tập trung + attention để trả lời câu hỏi "cả nhóm cùng nhận một phần thưởng thì agent nào thật sự làm nên kết quả đó", kể cả khi số agent thay đổi giữa lượt chơi.*

Cohen và cộng sự (2021). **Thuật toán đa tác nhân mặc định** của Unity ML-Agents.

**Hai thách thức nó nhắm tới:**
1. **Credit assignment** — xác định từng agent đóng góp bao nhiêu vào phần thưởng chung
2. **Posthumous credit** — gán công lao cho agent đã ngừng hoạt động *trước khi* phần thưởng nhóm được trao

**Kiến trúc:** CTDE — Centralized Training with Decentralized Execution.
- Lúc huấn luyện: critic tập trung nhìn trạng thái + hành động của **toàn bộ** agent
- Lúc triển khai: mỗi agent chỉ dựa vào **quan sát cục bộ** của riêng mình

**Cải tiến cốt lõi:** cơ chế **attention** xử lý số lượng agent thay đổi động — các phương pháp trước (MADDPG, COMA) cố định số agent.

Phần cập nhật policy kế thừa gần như nguyên vẹn từ PPO (cùng clipped surrogate, cùng cách ước lượng advantage). Khác biệt: V(s) đơn tác nhân được thay bằng **hàm giá trị nhóm dựa trên baseline tập trung**. Phần thưởng nhóm đến từ cơ chế `SimpleMultiAgentGroup` của ML-Agents.

| ✅ Ưu | ❌ Nhược |
|---|---|
| Trả lời được câu hỏi mà PPO độc lập không trả lời nổi | On-policy → thừa hưởng trọn vẹn vấn đề hiệu quả mẫu của PPO |
| Attention vững kể cả khi nhóm đổi quân số giữa chừng | ⚠️ **Với đội hình 2 tác nhân giống hệt nhau, attention là công sức đổ vào một bài toán không tồn tại** |
| Ăn khớp sẵn với group reward trong ML-Agents | Bài toán đơn tác nhân → suy biến gần về PPO mà vẫn gánh kiến trúc thừa |

---

## 2.4. MAPPO — Multi-Agent PPO

**Một câu:** *Mở rộng PPO sang đa tác nhân bằng cách đơn giản nhất có thể — chia sẻ tham số + một hàm giá trị tập trung.*

Yu và cộng sự (2022). Trong khi MA-POCA chọn con đường phức tạp (critic tập trung + attention), MAPPO đi lối đơn giản hơn nhiều.

**Hàm giá trị tập trung:**
```
V_φ(s) = V_φ(o₁, o₂, …, o_n, s_global)
```

**Hàm mục tiêu cho agent i:**
```
L_i^MAPPO(θ) = 𝔼̂_t[ min( r_t(θ)·Â_t^i , clip(r_t(θ), 1−ε, 1+ε)·Â_t^i ) ]
```
với r_t(θ) = π_θ(a_t^i | o_t^i) / π_θ_old(a_t^i | o_t^i)

**Parameter sharing:** θ₁ = θ₂ = … = θ_n = θ. Nếu cần phân biệt agent, mã hóa danh tính thành vector one-hot rồi ghép vào observation.

| ✅ Ưu | ❌ Nhược |
|---|---|
| **Nghịch lý: sức mạnh đến từ chính chỗ nó chẳng thêm gì mới.** Với n tác nhân, cùng ngân sách mô phỏng cho ra **gấp n lần** dữ liệu huấn luyện hữu ích | Chia sẻ tham số chỉ hợp lý khi các agent **thật sự giống nhau** — vai trò bất đối xứng thì một mạng phải học lẫn lộn hành vi mâu thuẫn |
| Chạy trên nguyên bộ hạ tầng vốn đã tối ưu cho PPO | V_φ(s) phình lên theo quân số |
| Yu et al. ghi nhận bám sát/vượt MADDPG, QMIX | Không có cách gọn gàng xử lý số agent thay đổi giữa lượt chơi |

**So sánh trực quan MAPPO vs MA-POCA:**

```
MAPPO:                              MA-POCA:
  Shared Policy π_θ                   Policy 1 π_θ1 → Agent 1
    ├→ Agent 1                        Policy 2 π_θ2 → Agent 2
    └→ Agent 2                              ↓
  Centralized V_φ(s)                  Group Critic w/ Attention
```

---

## 2.5. DQN — Deep Q-Network

**Một câu:** *Không tham số hóa chính sách — mạng học Q_θ(s,a), policy suy ra gián tiếp bằng argmax.*

Mnih và cộng sự (2015). Thuật toán đầu tiên cho thấy mạng nơ-ron sâu học chơi game ở trình độ con người chỉ từ điểm ảnh thô (49 game Atari).

**Hàm mất mát TD:**
```
L(θ) = 𝔼_{(s,a,r,s′)~𝒟}[ ( r + γ·max_{a′} Q_{θ⁻}(s′,a′) − Q_θ(s,a) )² ]
```
- 𝒟: bộ đệm phát lại (replay buffer) — dùng lại mỗi mẫu nhiều lần **và** phá vỡ tương quan thời gian
- θ⁻: mạng mục tiêu (target network), cập nhật chậm hơn → giữ mục tiêu tương đối cố định. **Thiếu nó, mạng đuổi theo chính mục tiêu do mình sinh ra và rất dễ phân kỳ.**

**Khám phá:** quy tắc **ε-tham lam** (không phải entropy) — ε giảm dần theo số bước. Đồ án dùng lịch tuyến tính 1,0 → 0,05 trong 500.000 bước.

> ⚠️ **Hệ quả trực tiếp cho đồ án:** DQN **không sinh ra chỉ số entropy của chính sách**, nên nó vắng mặt trong mọi so sánh dựa trên entropy ở Chương 4.

| ✅ Ưu | ❌ Nhược |
|---|---|
| Off-policy → tận dụng lại kinh nghiệm đã lưu | ⚠️ **max_a Q(s,a) không dùng thẳng được cho hành động liên tục** → rào cản trên Football Table |
| Chỉ 1 mạng giá trị, nhẹ hơn actor-critic | Toán tử max gây **overestimation bias** |
| Rời rạc + nhỏ → chọn hành động vừa chính xác vừa rẻ | Không có cơ chế giữ tính ngẫu nhiên sau khi ε giảm → dễ chốt sớm vào phương án dưới tối ưu |

---

## 2.6. Khuyến nghị chọn thuật toán (rút từ bảng so sánh)

```
Chưa nắm rõ đặc thù bài toán?
  └→ Bắt đầu bằng PPO (chịu được siêu tham số sai, cho mốc so sánh đáng tin)

Mỗi bước tương tác môi trường đắt hơn hẳn mỗi bước cập nhật mạng?
  └→ Chuyển sang SAC (replay buffer trả lại đủ giá trị bù chi phí 3 mạng)

Nhiều tác nhân?
  ├→ Đồng nhất + số lượng cố định → MAPPO (chia sẻ tham số khai thác dữ liệu triệt để nhất)
  └→ Vai trò bất đối xứng / agent rời nhóm giữa chừng → MA-POCA (attention mới thật sự cần)

DQN: chỉ dùng được với hành động rời rạc — trong đồ án là mốc tham chiếu
     cho nhóm value-based, không phải ứng viên cạnh tranh.
```

---

# PHẦN 3 — Unity ML-Agents

## 3.1. Kiến trúc client-server

```
   UNITY (mô phỏng)                          PYTHON (huấn luyện)
┌──────────────────────┐                  ┌─────────────────────────┐
│  Agent               │                  │  mlagents-learn         │
│   ├ CollectObserv..  │   ←── gRPC ──→   │   ├ đọc YAML            │
│   ├ OnActionReceived │                  │   ├ PPOTrainer          │
│   └ tính reward      │                  │   ├ POCATrainer         │
│  BehaviorParameters  │                  │   └ SACTrainer          │
│  Academy (singleton) │                  │  mlagents_envs (LL-API) │
└──────────────────────┘                  └─────────────────────────┘
```

- **Agent**: MonoBehaviour gắn vào GameObject — thu quan sát, nhận hành động, tính phần thưởng
- **BehaviorParameters**: định nghĩa không gian quan sát/hành động + loại hành vi
- **Academy**: singleton quản lý vòng lặp huấn luyện, đồng bộ bước thời gian giữa mọi agent

Có thể chạy đồng thời **nhiều instance môi trường** để thu dữ liệu nhanh hơn.

## 3.2. Vật lý và tính xác định — chi tiết quan trọng

**Vấn đề:** Unity kết xuất khung hình qua `Update()`, tần số **biến thiên** tùy hiệu năng máy. Nếu Agent ra quyết định theo tần số trồi sụt ấy, môi trường **mất tính xác định** — cùng một chuỗi hành động cho ra kết quả vật lý khác nhau ở các lần chạy khác nhau.

**Cách xử lý:** ML-Agents dồn toàn bộ quy trình RL vào `FixedUpdate()` — chu kỳ cập nhật vật lý tần số **cố định 0,02 giây/bước = 50 lần/giây**. PhysX tính động lực học, cập nhật `Rigidbody`, xử lý `Collider` hoàn toàn theo bước thời gian cố định này.

→ Chỉ cần cùng một seed ngẫu nhiên là môi trường hành xử **xác định**. Thiếu tính chất đó thì mọi so sánh giữa hai lần chạy đều mất căn cứ.

## 3.3. Hệ thống cảm biến

| Loại | Cách hoạt động | Đặc điểm |
|---|---|---|
| **Cảm biến tia (Raycast)** | Bắn tia quanh Agent theo góc quét; tia chạm vật thể → ghi one-hot loại vật thể + khoảng cách chuẩn hóa [0,1] | Hiệu quả, nhẹ. **Cảm biến chủ đạo của đồ án** |
| **Grid Sensor** | Phủ lưới 2D, đếm vật thể mỗi ô | Hợp bài toán cần cái nhìn toàn cảnh (cờ bàn) |
| **Camera Sensor** | Lấy pixel RGB thô | Toàn diện nhưng chi phí lớn, hội tụ chậm; buộc phải dùng CNN |

**Công thức số chiều do cảm biến tia đóng góp:**
```
dim = k × (m + 2)
```
với k = số tia, m = số nhãn cần phát hiện. Mỗi tia sinh m+2 giá trị: **m** one-hot cho nhãn + **1** cờ báo có chạm gì không + **1** khoảng cách.

## 3.4. Action Masking & Decision Period

- **Action Masking**: chặn hành động không hợp lệ bằng cách ép xác suất chọn về 0 (ví dụ agent đứng sát tường → "đeo mặt nạ" lên hành động tiến lên). Không gian tìm kiếm hẹp lại, hội tụ nhanh hơn, thay vì bắt agent tự học rằng đâm đầu vào tường thì bị phạt.
- **DecisionRequester / Decision Period**: gom nhóm bước mô phỏng. Thay vì ra quyết định ở từng bước `FixedUpdate` (0,02s), Agent giữ nguyên hành động cũ suốt k bước. Vừa cho Agent đủ thời gian hoàn thành một quỹ đạo vật lý, vừa cắt số lần gọi mạng nơ-ron.
- **Heuristic Policy**: người dùng điều khiển Agent bằng bàn phím để gỡ lỗi và tự cảm nhận độ khó.

## 3.5. ⚠️ Ba giới hạn tích hợp — quy định cách bố trí toàn bộ thực nghiệm

ML-Agents **4.0.2** chỉ tích hợp sẵn **đúng 3 trainer**: `ppo`, `poca` (MA-POCA), `sac`.

| # | Giới hạn | Hệ quả cho đồ án | Cách xử lý |
|---|---|---|---|
| **1** | **MAPPO và DQN không có mặt** | 2/5 thuật toán phải tự thêm | **Trainer mở rộng** — đăng ký vào `ML_AGENTS_TRAINER_TYPE`, dùng chung toàn bộ hạ tầng gRPC, TensorBoard, ONNX |
| **2** | **DQN không ghép được với self-play** — bộ điều phối đối kháng báo lỗi tra cứu chính sách ngay lúc khởi tạo | Lần chạy DQN trên Football Table **phải tắt self-play → không có ELO** | Đọc như tham chiếu rời, không xếp hạng |
| **3** | **Group reward vốn tối ưu cho POCA** — áp cho PPO/SAC/DQN thì phải phân bổ thủ công về từng agent | Khả năng gán công lao của 3 thuật toán này suy giảm | Chấp nhận, ghi nhận rõ trong báo cáo |

**Điểm mấu chốt của lựa chọn "trainer mở rộng" thay vì "thư viện ngoài":**
> Chỉ khi cả 5 thuật toán chạy trên **cùng một đường ống** thu thập quỹ đạo, cùng một cách ghi nhật ký, cùng một định dạng mô hình xuất ra, thì chênh lệch đo được giữa chúng mới nói lên **đặc tính của môi trường** — chứ không phải nói lên sự khác biệt của hạ tầng đo.

Đây là câu trả lời chuẩn nếu hội đồng hỏi "sao không dùng Stable-Baselines3 cho tiện?".

---

# PHẦN 4 — Phương pháp luận thiết kế môi trường (phần lõi)

> **Đây là phần đóng góp học thuật chính. Nếu chỉ có thời gian ôn một phần, ôn phần này.**

## 4.1. Bốn định nghĩa hình thức

### Định nghĩa 1 — Không gian quan sát

> Cho môi trường có không gian trạng thái S. **Không gian quan sát Ω** là tập hợp mọi quan sát khả dĩ. **Hàm quan sát O: S → Ω** ánh xạ mỗi trạng thái s ∈ S sang quan sát o = O(s) mà tác nhân dùng làm **căn cứ duy nhất** để ra quyết định.

**Ranh giới then chốt: trạng thái ≠ quan sát.**
- **Trạng thái**: toàn bộ thông tin mô tả đầy đủ thế giới mô phỏng, kể cả những gì agent không cảm nhận được
- **Quan sát**: chỉ phần agent thực sự với tới qua cảm biến

**Hệ quả:**
- O song ánh → agent "nhìn thấy" trọn vẹn trạng thái → bài toán là **MDP đầy đủ**
- O không song ánh (nhiều trạng thái cùng cho một quan sát) → **POMDP**

**Cả ba môi trường của đồ án đều là POMDP về bản chất** — agent đâu biết chính xác vận tốc tương lai của một phương tiện, cũng chẳng nhìn xuyên tường được.

### Định nghĩa 2 — Tính chất Markov của quan sát

> Một biểu diễn quan sát thỏa mãn tính chất Markov nếu:
> ```
> Pr(o_{t+1}, r_{t+1} | o_t, a_t, o_{t-1}, a_{t-1}, …) = Pr(o_{t+1}, r_{t+1} | o_t, a_t)
> ```

Tính chất Markov tuyệt đối gần như không bao giờ đạt được. Mục tiêu thiết kế chỉ là **tiệm cận nó với chi phí quan sát thấp nhất**.

**Hai kỹ thuật bổ trợ khi quan sát tức thời chưa đủ Markov:**
1. **Chồng khung (frame stacking)** — ghép vài quan sát liên tiếp thành một vector, thông tin xu hướng chuyển động hiện lên tường minh
2. **Mạng hồi tiếp (recurrent)** — để agent tự tổng hợp lịch sử

→ **Đồ án thiên về cách 1**, kết hợp bổ sung thẳng các đại lượng động (vận tốc) vào vector quan sát, cốt giữ mạng chính sách đơn giản và ổn định.

**Nguyên tắc xuyên suốt: TỐI THIỂU NHƯNG ĐỦ.**
- Phần tử thừa → đẩy số chiều đầu vào lên, việc học chậm lại
- Phần tử thiếu → phá vỡ tính chất Markov, bài toán thành **bất khả học**

**Chuẩn hóa:** giá trị quan sát liên tục được đưa về lân cận [−1, 1] bằng x̂ = (x − μ)/σ với μ, σ ước lượng trực tuyến. Riêng Football Table bắt buộc phải chuẩn hóa: vận tốc bóng và góc xoay thanh gạt chênh nhau nhiều bậc, để nguyên thì đại lượng lớn sinh gradient lấn át.

### Định nghĩa 3 — Không gian hành động

> **Không gian hành động A** là tập mọi hành động agent được phép thực hiện. Gọi là **rời rạc** nếu A hữu hạn; gọi là **liên tục** nếu A ⊂ ℝⁿ, mỗi hành động là vector thực bị chặn.

**Hai dạng → hai cách mạng biểu diễn đầu ra:**
- Rời rạc: mạng xuất phân phối xác suất trên tập hành động (nhiều nhóm độc lập → dạng **đa rời rạc**, mỗi nhóm một nhánh)
- Liên tục: mạng xuất tham số của phân phối chuẩn nhiều chiều (kỳ vọng + độ lệch chuẩn từng chiều), hành động được lấy mẫu rồi cắt về khoảng hợp lệ

→ Giải thích vì sao **SAC phát huy thế mạnh nhiều nhất ở không gian liên tục** — nó vốn được thiết kế cho điều khiển liên tục.

### Định nghĩa 4 — Hàm phần thưởng

> **R: S × A × S → ℝ** gán cho mỗi phép chuyển (s, a, s′) một số thực r. Mục tiêu của agent là tối đa hóa 𝔼[G_t] = 𝔼[Σ γ^k r_{t+k+1}].

## 4.2. Phân rã hàm phần thưởng thành ba lớp

**Cả ba môi trường đều theo cùng khuôn dạng:**

```
R(s, a, s′) =  R_mt(s′)      +      F(s, s′)         +      R_b(s)
              ──────────           ──────────              ──────────
              thưa, tại           định hình theo           dày, mỗi bước
              cột mốc             thế năng
```

| Thành phần | Vai trò | Ưu | Rủi ro |
|---|---|---|---|
| **R_mt — mục tiêu** | Chỉ khác 0 ở vài trạng thái đánh dấu kết quả (bóng vào lưới, cả nhóm tới đích) | **Định nghĩa bài toán** — giữ mình nó thì chính sách tối ưu vẫn đúng | Tín hiệu quá thưa → giai đoạn đầu gradient ≈ 0, học đứng im |
| **F — định hình** | Cho điểm liên tục theo mức tiến bộ hướng về mục tiêu | Lấp khoảng trống tín hiệu | Nơi ẩn chứa **rủi ro lớn nhất** |
| **R_b — theo bước** | Cộng trừ nhỏ mỗi bước (phạt thời gian, thưởng duy trì trạng thái có ích) | Tín hiệu dày đặc | Tương tự |

## 4.3. Lợi dụng phần thưởng (Reward Hacking)

> Agent mò ra hành vi tối đa hóa tổng phần thưởng mà **chẳng hề làm cái nhiệm vụ người thiết kế nhắm tới**.

**Ví dụ kinh điển** — thí nghiệm điều khiển xe đạp của Randløv & Alstrøm (1998): agent được thưởng mỗi lần tiến lại gần đích đã học cách **chạy vòng tròn quanh điểm xuất phát** để liên tục gặt phần thưởng tiến gần, mà không bao giờ tới nơi.

Amodei và cộng sự (2016) xếp hiện tượng này vào nhóm vấn đề an toàn cốt lõi của học máy, và chỉ ra nó phát sinh **gần như tất yếu** mỗi khi hàm phần thưởng chỉ là đại lượng **thay thế** cho mục tiêu thật.

> ⚠️ **Đồ án đã gặp đúng hiện tượng này** ở phiên bản phần thưởng đầu tiên của Capture The Flag (xem §5.2.6).

## 4.4. ⭐ PBRS — Định hình phần thưởng theo thế năng

**Đây là cơ sở lý thuyết chính của đồ án.** Ng và cộng sự (1999).

### Định nghĩa

> Cho hàm thế năng **Φ: S → ℝ**. Phần thưởng định hình cộng thêm vào phép chuyển s → s′:
> ```
> F(s, s′) = γ·Φ(s′) − Φ(s)
> ```
> **Khi đó chính sách tối ưu của bài toán R + F trùng đúng với chính sách tối ưu của bài toán gốc R.**

### Bảo đảm chống lợi dụng — chứng minh

Với mọi chu trình khép kín s₀ → s₁ → … → s_n = s₀, tổng phần thưởng định hình khi γ → 1:

```
Σ_{i=0}^{n-1} [ Φ(s_{i+1}) − Φ(s_i) ]  =  Φ(s_n) − Φ(s₀)  =  0
```

> **Mọi hành vi lặp đi lặp lại đều cho lợi ích ròng bằng không.** Đẳng thức này loại bỏ kiểu lợi dụng của thí nghiệm xe đạp **ngay từ trong thiết kế**, không phải bằng cách mò mẫm dò hệ số.

### Hàm thế năng tự nhiên cho bài toán điều hướng

```
Φ(s) = −d(s)      (d = khoảng cách từ agent tới mục tiêu)
```
→ F thưởng mỗi bước làm giảm khoảng cách, phạt mỗi bước làm tăng khoảng cách.

**Tính chất khớp nối (telescoping):** tổng định hình trọn một lượt chơi chỉ phụ thuộc khoảng cách đầu và cuối:
```
Σ_{t=1}^{T} F(s_{t-1}, s_t) = κ·[ d(s₀) − d(s_T) ] ≤ κ·d(s₀)
```
→ **Không dính dáng gì tới độ dài lượt chơi hay quỹ đạo agent chọn.** Đây là cơ sở để chọn hệ số κ.

## 4.5. ⭐ Bốn nguyên tắc thiết kế hàm phần thưởng

> **Mọi giá trị số trong các bảng phần thưởng của đồ án đều phải giải thích được bằng chính bốn nguyên tắc này.**

### Nguyên tắc 1 — Bám theo lời giải mẫu

> Trước khi đặt bất kỳ hệ số nào, phải **mô tả được một quỹ đạo mẫu hoàn thành nhiệm vụ**, rồi kiểm tra rằng **không thành phần phần thưởng nào phạt một trạng thái nằm trên quỹ đạo đó**.

*Nguồn:* Amodei et al. — phần lớn lỗi thiết kế phần thưởng đến từ việc **mô tả sai mục tiêu**, chứ không từ việc chọn sai hệ số.

*Đây là nguyên tắc mà phiên bản CTF đầu tiên đã vi phạm.*

### Nguyên tắc 2 — Ưu tiên sự kiện một lần hoặc thế năng, thay vì cộng dồn theo bước

> Một khoản thưởng cộng dồn mỗi bước cho một trạng thái luôn tạo ra **động cơ nấn ná** tại trạng thái ấy.

- Cần thưởng cột mốc → **phần thưởng sự kiện, trao đúng một lần** mỗi lượt chơi
- Cần tín hiệu dẫn đường liên tục → **dạng thế năng PBRS** với bảo đảm chống chu trình

### Nguyên tắc 3 — Giữ trật tự độ lớn

> Ký hiệu |R_mt| = độ lớn phần thưởng mục tiêu, Σ_b = tổng tuyệt đối tối đa các khoản theo bước có thể tích lũy trong trọn một lượt chơi. **Luôn giữ Σ_b < |R_mt|.**

**Bảo đảm:** một lượt chơi hoàn thành nhiệm vụ **luôn** có tổng phần thưởng cao hơn mọi lượt chơi không hoàn thành, bất kể agent xoay xở thế nào với các khoản phụ.

**Cách cụ thể hóa rất gọn:** chia các khoản theo bước cho số bước tối đa N.
```
Khoản c/N mỗi bước  →  bám lấy trạng thái đó cả lượt cũng chỉ thu về đúng c
```
Chọn c < |R_mt| là lập tức thỏa mãn bất đẳng thức, đồng thời **hệ số không còn lệ thuộc vào độ dài lượt chơi**.

### Nguyên tắc 4 — Sửa cơ chế môi trường trước khi tăng hệ số phần thưởng

> Khi một hành vi mục tiêu quá khó để khám phá bằng thử–sai, **tăng hệ số thưởng cho nó không giúp ích** — vì agent chưa từng chạm tới hành vi ấy để mà nhận thưởng.

→ Thay vào đó: **điều chỉnh chính cơ chế môi trường**, hoặc dùng **học theo chương trình (curriculum learning)** để hạ độ khó khám phá ban đầu.

*Ví dụ áp dụng:* thêm khoảng ân hạn 1 giây cho cửa trong Capture The Flag.

---

# PHẦN 5 — Ba môi trường: thiết kế chi tiết

## 5.0. Bảng đối chiếu tổng hợp

| Đặc trưng | **Football Table** | **Capture The Flag** | **Cross The Road** |
|---|---|---|---|
| Dạng bài toán | Đối kháng 1v1 | Hợp tác đa tác nhân | Điều hướng đơn tác nhân |
| Số tác nhân | Hai, đối kháng | Hai, hợp tác | Một |
| **Không gian quan sát** | **60** | **61** | **132** |
| **Không gian hành động** | **Liên tục, 8 chiều** | **Rời rạc, 7 hành động** | **Rời rạc, 4 hành động** |
| Cảm biến tia | Không | 7 tia, 6 nhãn | 21 tia, 4 nhãn |
| Nhịp ra quyết định | 2 bước vật lý (25 qđ/s) | 20 bước vật lý (2,5 qđ/s) | 5 bước vật lý (10 qđ/s) |
| Phần thưởng nhóm | Không | **Có** | Không |
| Kết thúc lượt chơi | Bàn thắng hoặc 3.000 bước | Cả hai tới đích hoặc 100.000 bước | Tới đích hoặc va chạm (**không giới hạn bước**) |
| Cơ chế đặc thù | **Tự chơi (self-play)** | **Bàn giao + học theo chương trình** | **Vật cản động** |
| Ngân sách bước | 1,60 triệu | 1,70 triệu | 2,00 triệu |
| Kiến trúc mạng | 2 lớp × 256 | 3 lớp × 256 | 2 lớp × 128 |
| Thuật toán **kỳ vọng** tốt nhất | PPO self-play | MA-POCA hoặc MAPPO | SAC |

> ⚠️ Dòng cuối là **kỳ vọng trước khi chạy**, không phải kết quả. Chỉ một phần được xác nhận — và **chính những chỗ lệch mới là phần đáng đọc nhất**.

**Lý do lệch nhau trên nhiều trục cùng lúc là CỐ Ý:** một bộ môi trường chỉ khác nhau ở đúng một trục sẽ không đủ sức cho biết thuật toán nào thắng nhờ đâu.

### Tốc độ huấn luyện thực đo (mỗi môi trường lấy lần chạy PPO đại diện)

| Môi trường | Số bước | Thời gian | Bước/giây |
|---|---|---|---|
| Football Table | 1.600.000 | 47 phút 0 giây | **567** |
| Capture The Flag | 1.700.000 | 50 phút 8 giây | **565** |
| Cross The Road | 2.000.000 | 47 phút 52 giây | **697** |

**Vì sao ba con số sát nhau dù khối lượng vật lý chênh rất xa?** Hai yếu tố tác động ngược chiều gần như triệt tiêu nhau:
- Cross The Road nhanh nhất: chỉ mô phỏng 1 khối trượt theo ô lưới + 5 xe chạy thẳng, **dù** mỗi quyết định trải 5 bước vật lý
- Football Table: phải giải khớp vật lý 8 thanh gạt + va chạm bóng liên tục, **nhưng** chỉ cách 2 bước vật lý giữa hai quyết định
- Capture The Flag: vật lý nhẹ nhất, **lại chậm nhất** — vì mỗi quyết định trải tới 20 bước vật lý và mỗi lượt chơi kéo dài tối đa 100.000 bước

→ **Hệ quả:** chênh lệch thời gian thực ở Chương 4 là do **bản thân thuật toán** (chi phí cập nhật mạng của nhóm off-policy), không phải do môi trường.

### Quy ước dùng chung cho cả ba môi trường

- Mỗi môi trường = 1 scene Unity, bên trong có 1 khu vực huấn luyện đóng thành **prefab** → nhân bản được
- **Cả ba scene dùng cho thực nghiệm đều chạy song song 8 khu vực** — tăng lượng kinh nghiệm/bước mô phỏng, giảm tương quan giữa các mẫu trong cùng lô
- ⚠️ **Hệ quả phải nhớ:** cùng một số bước môi trường ở đây **không tương đương** với cùng số bước ở cấu hình 1 khu vực — chi tiết quan trọng khi đối chiếu với công bố khác
- Hệ số tăng tốc mô phỏng: **×20 thời gian thực**
- Bước vật lý cố định **0,02s** = 50 bước/giây mô phỏng
- Quan sát hoàn toàn bằng vector số thực, **không dùng quan sát hình ảnh**
- Mỗi môi trường gắn với đúng 1 behavior: `Football`, `PuzzleBehavior`, `CrossTheRoad`
- Ba lớp agent: `FootballAgent`, `PuzzleAgent`, `CrossTheRoadAgent` (kế thừa lớp `Agent`)
- Nền tảng: **ML-Agents 4.0.2 trên Unity 6000.3**
- Toàn bộ 15 lần huấn luyện do **một chương trình Python điều phối tự động**

---

## 5.1. FOOTBALL TABLE — Đối kháng 1v1, hành động liên tục

### 5.1.1. Mô tả bài toán

Bàn bi lắc 3D, vật lý va chạm đầy đủ giữa bóng và cầu thủ gắn trên thanh gạt. Hai đội, mỗi đội **4 thanh gạt**, vừa phải ghi bàn vừa phải giữ khung thành.

**Hai đặc trưng:**
1. **Tính đối kháng** → trường hợp điển hình để kiểm chứng cơ chế **tự chơi**
2. **Động lực học liên tục** — bóng lăn, nảy, đổi hướng không ngừng → agent phải phản ứng nhanh, nắm cả tấn công lẫn phòng thủ

### 5.1.2. Không gian quan sát — 60 giá trị

| Nhóm | Số giá trị | Nội dung |
|---|---|---|
| Quả bóng | **12** | 3 vận tốc (nén về [−1,1]) + 9 mã hóa vị trí |
| Đội nhà | **32** | 4 thanh × 4 đại lượng (vận tốc trượt, vận tốc xoay, vị trí trượt, góc xoay) |
| Đội đối phương | **16** | 4 thanh × 4 đại lượng tương tự |

**Hai kỹ thuật mã hóa đáng dừng lại:**

**a) Tách chữ số thập phân.** Thay vì đưa vào mạng một giá trị duy nhất cho vị trí bóng / góc xoay, giá trị đó được **tách thành nhiều thành phần ứng với các hàng thập phân liên tiếp**.
→ Một thay đổi rất nhỏ ở hàng thập phân sâu vẫn tạo biến thiên rõ rệt ở một thành phần đầu vào → mạng nhạy hơn hẳn với sai lệch tinh vi về vị trí — thứ **quyết định thành bại của một cú chạm bóng**.

**b) Đối xứng hóa quan sát.** Mọi vị trí và vận tốc được đưa về hệ tọa độ địa phương rồi **nhân với hệ số dấu tùy theo phía của đội**.
→ Cả hai phía đều thấy khung thành đối phương ở cùng một hướng quy ước → **một chính sách duy nhất vận hành được cho cả hai phía**, và cơ chế tự chơi trở nên nhất quán vì hai đội thực sự dùng chung một mạng nơ-ron.

**Chuẩn hóa quan sát: BẬT** (các đại lượng vật lý chênh nhau nhiều bậc).

### 5.1.3. Không gian hành động — 8 chiều liên tục

```
a = ( f_trượt_1, f_xoay_1, …, f_trượt_4, f_xoay_4 ) ∈ [−1, 1]⁸
```

**Mỗi đội chỉ có MỘT tác nhân duy nhất, quản đồng thời cả 4 thanh gạt.** Hai cái lợi:
1. Bài toán phối hợp 4 thanh trở thành **điều khiển tập trung** mà một chính sách học được — khỏi xoay xở với đồng bộ nhiều tác nhân độc lập
2. Khớp thẳng với cơ chế tự chơi — mỗi phía bàn chỉ cần đúng một chính sách

**Cơ chế vật lý:** giá trị hành động **không dịch thanh gạt tức thời**. Nó được diễn giải thành mức thay đổi vận tốc, đặt lên thân vật lý với **hệ số 1 (trượt)** và **25 (xoay)**. Chuyển động cuối cùng do PhysX quyết định.

**Nhịp quyết định:** mỗi **2 bước vật lý** = **25 quyết định/giây** mô phỏng.

### 5.1.4. ⭐ Hàm phần thưởng — và lập luận toán học đằng sau tỉ lệ 5:1

| Sự kiện | Giá trị | Loại |
|---|---|---|
| Ghi bàn vào khung thành đối phương | **+5,0** | Thưởng mục tiêu |
| Bị thủng lưới | **−1,0** | Phạt mục tiêu |
| Mỗi bước trôi qua | **−1/3000** | Phạt thời gian |

Chiếu vào khuôn dạng 3 lớp: **chỉ dùng 2 lớp** (mục tiêu + theo bước). **Không dùng định hình thế năng** — lý do ở §5.1.5.

#### Vì sao +5 chứ không phải +1? — Bài toán đánh đổi cầm cự vs dứt điểm

Với hàm phần thưởng **đối xứng**, chính sách an toàn nhất là **ôm bóng ở phần sân nhà và không bao giờ dâng lên** — vì mọi pha tấn công đều mở ra nguy cơ bị phản công. Nhận định này **lượng hóa được**:

Xét agent chọn giữa:
- **Cầm cự** — giữ bóng tới hết lượt chơi
- **Dứt điểm** — tấn công thành công với xác suất p, bị phản công với xác suất 1−p

```
V_cầm cự  = −T · (1/3000) = −1          (T = 3000 bước)
V_dứt điểm = p·R₊ − (1−p)·R₋
```

Lối chơi tấn công chỉ được ưa chuộng khi V_dứt điểm > V_cầm cự, tức:

```
        R₋ − 1
p  >  ───────────
       R₊ + R₋
```

| Cấu hình | Ngưỡng p | Diễn giải |
|---|---|---|
| **Đối xứng R₊ = R₋ = 5** | **0,4** | Agent chỉ chịu tấn công khi tự tin thắng ≥ 40% số pha bóng. Giai đoạn đầu huấn luyện điều đó gần như không bao giờ đúng → **chính sách hội tụ về phòng ngự tuyệt đối** |
| **Được chọn: R₊ = 5, R₋ = 1** | **0** | **Mọi cơ hội ghi bàn dù nhỏ đến mấy cũng đáng thử** |

> 💡 Phép tính này còn cho thấy **hình phạt thời gian chẳng phải chi tiết phụ, mà là thành phần quyết định dấu của vế phải**.

#### Vì sao −1/3000?

Nguyên tắc **giữ trật tự độ lớn**: nhân với T = 3000 bước → tổng phạt tích lũy trọn lượt chơi **vừa đúng 1 điểm = bằng đúng hình phạt thủng lưới**.

**Hệ quả có chủ đích:** một lượt chơi **hòa không bàn thắng bị đánh giá ngang với việc để thủng lưới một bàn** → agent không thể xem thế trận bế tắc là kết quả chấp nhận được. Trong khi đó tổng phạt vẫn nhỏ hơn phần thưởng ghi bàn rất nhiều → chẳng bao giờ lấn át mục tiêu chính.

### 5.1.5. ⚠️ Hai thành phần định hướng bị TẮT — và ba căn cứ

Mã nguồn cài sẵn hai thành phần tùy chọn, nhưng **hệ số đều bằng 0** ở mọi lần chạy báo cáo:
1. Phần thưởng tỉ lệ với vận tốc bóng chiếu lên hướng khung thành đối phương (khi đang kiểm soát bóng)
2. Hình phạt khi thanh gạt xoay quá mạnh

**Căn cứ 1 — Vi phạm PBRS.** Phần thưởng theo vận tốc **không mang dạng thế năng**: nó phụ thuộc vào vận tốc — đại lượng của phép chuyển, chứ không phải hàm của riêng trạng thái — nên **không viết được thành γΦ(s′) − Φ(s)**. Bảo đảm chống chu trình mất hiệu lực ngay → agent dư sức đẩy bóng tới lui theo hướng khung thành để gặt phần thưởng vô hạn mà chẳng bao giờ dứt điểm. *Đúng cơ chế của thí nghiệm xe đạp.*

**Căn cứ 2 — Vi phạm nguyên tắc bám theo lời giải mẫu.** Một cú sút mạnh **nhất thiết** phải đi kèm vận tốc xoay lớn → khoản phạt này giáng thẳng vào hành động **nằm trên quỹ đạo hoàn thành nhiệm vụ**. Để nó khác 0 thì agent sẽ trôi về lối rê bóng chậm chạp.

**Căn cứ 3 — Tự chơi tự nó đã là một chương trình học.** Đối thủ luôn mạnh tương đương agent hiện tại → tỉ lệ thắng thua giữ mức cân bằng, tín hiệu thưa vẫn xuất hiện đủ thường xuyên. *Lập luận này đã được kiểm chứng ở quy mô lớn hơn nhiều trong AlphaGo Zero — chính sách mạnh hơn con người học chỉ từ tín hiệu thắng thua cuối ván, không hề có phần thưởng trung gian.*

### 5.1.6. Cấu hình huấn luyện

```yaml
behaviors:
  Football:
    trainer_type: ppo
    hyperparameters:
      batch_size: 2048        buffer_size: 40960
      learning_rate: 3.0e-4   beta: 0.005
      epsilon: 0.2            lambd: 0.95
      num_epoch: 5            learning_rate_schedule: linear
    network_settings:
      normalize: true         hidden_units: 256    num_layers: 2
    reward_signals:
      extrinsic: { gamma: 0.99, strength: 1.0 }
    self_play:
      save_steps: 50000                      # lưu 1 phiên bản đối thủ mỗi 50K bước
      team_change: 100000                    # đổi phía mỗi 100K bước
      swap_steps: 200000
      window: 10                             # giữ cửa sổ 10 đối thủ gần nhất
      play_against_latest_model_ratio: 0.5   # 50% đấu phiên bản mới nhất
      initial_elo: 1200.0
    max_steps: 1600000       time_horizon: 1000     summary_freq: 10000
```

**Kết thúc lượt chơi:** bàn thắng, hoặc chạm mốc **3.000 bước** (~1 phút mô phỏng) — chặn thế trận bế tắc vô hạn và giữ dữ liệu huấn luyện luôn được làm mới.

**Riêng DQN** không ghép nổi với self-play → phải chạy trên bản dựng `FootballDiscrete` với **8 nhánh 3 mức** thay cho 8 kênh liên tục.

---

## 5.2. CAPTURE THE FLAG — Hợp tác đa tác nhân

### 5.2.1. Mô tả bài toán

Câu đố không gian mang tính hợp tác: **hai tác nhân phải phối hợp chặt chẽ mới cùng về đích được**. Mấu chốt: **không tác nhân nào tự mình hoàn thành nổi**.

**Bố cục:** hành lang dài chia thành **3 khoang** bởi 2 bức tường ngăn có khe hở lệch nhau.

```
┌─────────────┬──────────────┬──────────────┐
│  KHOANG 1   │   KHOANG 2   │   KHOANG 3   │
│  xuất phát  │              │              │
│  ⯀⯀ 2 agent │   ● Bàn đạp 1│   ● Bàn đạp 2│ ██ ĐÍCH
│  ▣ vật cản  │              │              │
└──────khe hở─┴═══CỔNG═══════┴──────────────┘
              (2 cánh, hạ xuống mở / nâng lên chặn)
```

**Điểm thiết kế cốt lõi:** hai bàn đạp cùng điều khiển **một cổng cửa duy nhất**, nhưng nằm ở **hai phía đối diện** của cổng đó — bàn đạp 1 ở phía trong (cùng khoang xuất phát), bàn đạp 2 ở phía ngoài (đã qua cổng). Chính cách bố trí đối xứng ấy **sinh ra cấu trúc bàn giao mà lời giải buộc phải tuân theo**.

### 5.2.2. Không gian quan sát — 61 giá trị

| Nguồn | Số giá trị | Nội dung |
|---|---|---|
| **Cờ logic** | **5** | (1) bàn đạp 1 đã nhấn? (2) bàn đạp 2 đã nhấn? (3) **bản thân đã vượt cổng?** (4) **đồng đội đã vượt cổng?** (5) đã chạm đích? |
| **Cảm biến tia** | **56** | 7 tia × 8 giá trị |

**Cấu hình cảm biến tia:** 7 tia, góc quạt **70°** phía trước, tầm xa **20 đơn vị**, **6 nhãn** (đồng đội, tường, khối vật cản, bàn đạp, cửa, đích).
Mỗi tia → 8 giá trị = 6 one-hot + 1 cờ chạm + 1 khoảng cách. Kiểm chứng: 7 × (6+2) = **56** ✓

> ⭐ **Hai cờ "đã vượt cổng" là mấu chốt.** Chúng cho agent biết **khi nào nên rời bàn đạp** — chỉ khi đồng đội đã sang bên kia thì nhả bàn đạp mới hợp lý. **Thiếu cờ trạng thái của đồng đội, chính sách phi tập trung mất hẳn căn cứ trực tiếp để định thời điểm bàn giao, và bài toán khó học hơn hẳn.**

### 5.2.3. Không gian hành động — 7 rời rạc + động lực học

**7 hành động:** đứng yên, tiến, lùi, xoay trái, xoay phải, đi ngang trái, đi ngang phải.

**Cơ chế:** lệnh di chuyển **không dịch agent tức thời** — nó cộng **1,4 đơn vị/giây** vào thân vật lý mỗi bước vật lý; **hệ số cản tuyến tính = 4** liên tục hãm vận tốc lại. Hai lệnh xoay quay agent quanh trục đứng **200°/giây**.

**Nhịp quyết định:** mỗi **20 bước vật lý** = **2,5 quyết định/giây**.

#### Vận tốc tối đa

```
        Δv           1,4
v_max = ────── = ──────────── = 17,5 đơn vị/giây
        c · Δt    4 × 0,02
```

### 5.2.4. ⭐ Cơ chế cửa và lập luận loại trừ lối tắt

**Vấn đề:** nếu cửa sập xuống **ngay khoảnh khắc** agent rời bàn đạp, màn bàn giao gần như không thể khám phá nổi bằng thử–sai (đòi hỏi đồng bộ thời gian hoàn hảo).

**Giải pháp — khoảng ân hạn 1 giây mô phỏng.** Agent rời bàn đạp rồi thì cửa vẫn mở thêm 1 giây mới đóng. Cửa sổ ấy đủ để đồng đội kịp lên giữ bàn đạp còn lại. *Đây là áp dụng trực tiếp Nguyên tắc 4: sửa cơ chế môi trường thay vì tăng hệ số phần thưởng.*

#### ⚠️ Câu hỏi thiết kế: khoảng ân hạn có mở đường cho lối tắt cá nhân không?

Tức: agent bước lên bàn đạp 1 rồi **phóng thật nhanh qua cổng** trước khi cửa kịp đóng, khiến hợp tác thành thừa thãi?

**Lập luận định lượng loại trừ:**

| Đại lượng | Giá trị |
|---|---|
| Khoảng cách bàn đạp 1 → cổng | **19 đơn vị** |
| Khoảng ân hạn | **1 giây** |
| Quãng đường tối đa (giả định rộng rãi: đã chạy sẵn ở v_max) | **17,5 đơn vị** < 19 ❌ |
| Quãng đường **thực tế** (xuất phát từ đứng yên trên bàn đạp, phải tăng tốc) | **≈ 13,2 đơn vị** — chưa nổi **70%** khoảng cách cần vượt ❌ |

> **Kết luận: không tồn tại quỹ đạo nào cho phép một tác nhân đơn độc vượt cổng.** Mọi lần vượt cổng thành công đều là **bằng chứng của hợp tác thật**.

Đây cũng là cơ sở để đọc đúng các chỉ số phần thưởng ở Chương 4 — và là bằng chứng cho tiêu chí nghiệm thu **"không có lối tắt"**.

### 5.2.5. ⭐ Hàm phần thưởng (phức tạp nhất trong ba môi trường)

**Lời giải mẫu** (bám theo Nguyên tắc 1) — chuỗi trạng thái bắt buộc:
```
1. Hai agent rời phòng xuất phát
2. Agent A bước lên bàn đạp phía TRONG, đứng yên giữ cửa
3. Agent B vượt cổng
4. Agent B bước lên bàn đạp phía NGOÀI, giữ cửa ngược lại
5. Agent A rời bàn đạp, vượt cổng
6. Cả hai cùng tiến tới vạch đích
```
**Yêu cầu bắt buộc: không thành phần nào được phạt một trạng thái nằm trên chuỗi này.**

| Sự kiện | Giá trị | Phạm vi |
|---|---|---|
| Cả hai tác nhân đến đích | **+1,0** | **Nhóm** |
| Vượt được cổng đang khóa (1 lần/tác nhân) | **+0,5** | **Nhóm** |
| Giảm khoảng cách tới đích (định hình thế năng) | **0,01 × Δd** | Cá nhân |
| Đứng trên bàn đạp áp lực | **+0,5/N** mỗi bước | Cá nhân |
| Đẩy khối vật cản | **+0,25/N** mỗi bước | Cá nhân |
| Phạt thời gian mỗi bước | **−0,1/N** | **Nhóm** |

với **N = 100.000** = số bước tối đa một lượt chơi.

#### Vì sao phần thưởng mục tiêu trao cho NHÓM chứ không cho cá nhân?

Quyết định có hệ quả sâu xa: hàm giá trị mà critic phải học trở thành **giá trị của cả đội** → **một agent đứng yên giữ bàn đạp vẫn được ghi công khi đồng đội về đích**.

Ngược lại, nếu trao theo cá nhân, agent giữ cửa chẳng nhận được gì cho hành vi hy sinh của mình → chính sách nhanh chóng học cách **bỏ mặc đồng đội**.

→ Cấu hình group reward này chính là **điều kiện để MA-POCA phát huy tác dụng** (critic tập trung vốn sinh ra để phân rã một phần thưởng chung thành đóng góp từng agent).

#### Định hình theo thế năng — ba hệ quả

```
F(s_{t-1}, s_t) = κ · [ d(s_{t-1}) − d(s_t) ],    κ = 0,01
```

*Ghi chú kỹ thuật:* cài đặt dùng **hiệu thế năng thuần túy**, không dùng dạng chiết khấu γΦ(s′) − Φ(s). Với γ = 0,99, sai khác giữa hai dạng là (1−γ)Φ — **nhỏ hơn hai bậc** so với chính tín hiệu dẫn đường → tính bất biến chính sách vẫn giữ được ở mức xấp xỉ chấp nhận được (Devlin & Kudenko, 2012).

1. **Tín hiệu dẫn đường phủ kín cả hành lang**, kể cả đoạn chẳng có cột mốc nào → agent không bao giờ lọt vào vùng trống gradient
2. **Miễn nhiễm với lợi dụng** — mọi hành vi đi tới đi lui cho lợi ích ròng bằng 0
3. ⭐ **Quan trọng nhất với bài toán hợp tác:** agent đứng yên giữ bàn đạp có d(s_t) = d(s_{t−1}) → **không bị thành phần này phạt**. Hành vi hy sinh nằm trên lời giải mẫu được **giữ trung lập** thay vì bị trừng phạt.

**Cách chọn κ = 0,01:** tổng định hình bị chặn trên bởi κ·d(s₀). Muốn không lấn át phần thưởng mục tiêu thì cần **κ·d(s₀) < 1** → **d(s₀) < 100 đơn vị** — chiều dài hành lang hiện tại thỏa mãn với biên độ an toàn rất rộng.

#### Phần thưởng bàn giao — ba chi tiết đều có lý do

| Chi tiết | Lý do |
|---|---|
| **Điều kiện "cổng đang khóa"** | Ghép với kết luận §5.2.4 (không có lối tắt cá nhân) → sự kiện kích hoạt phần thưởng **tương đương về mặt logic** với sự kiện hợp tác thành công. Tín hiệu không còn là **đại lượng thay thế gần đúng**, mà là **chỉ báo chính xác** — tránh đúng cái bẫy Amodei cảnh báo |
| **Phạm vi nhóm** | Agent đang giữ bàn đạp cũng được ghi công cho cú vượt cổng của đồng đội |
| **Đặc tính một lần** | Không thể khai thác bằng cách ra vào cổng lặp đi lặp lại — bài học từ phiên bản đầu tiên |

#### Hai khoản theo bước cố tình đi ngược Nguyên tắc 2 — và cách khống chế

Thưởng đứng bàn đạp + đẩy vật cản **cộng dồn theo bước**, đi ngược nguyên tắc "ưu tiên sự kiện một lần". Lý do: **khám phá**. Giữ bàn đạp là hành vi phải *duy trì theo thời gian*, không cách nào diễn đạt bằng sự kiện tức thời; mà nếu chẳng có tín hiệu nào thì xác suất agent tình cờ đứng yên đủ lâu trên bàn đạp là quá nhỏ.

**Rủi ro nấn ná được khống chế bằng chuẩn hóa theo N:**
```
0,5/N mỗi bước × N bước = 0,5 điểm   (đứng lì cả lượt)
      vs
1,5 điểm nếu tham gia trọn vẹn một lời giải bàn giao   ← THUA XA
```

**Phạt thời gian nhóm −0,1/N:** tổng trọn lượt chỉ **0,1 điểm** — đủ phá thế hòa giữa hai chính sách cùng hoàn thành nhiệm vụ, nhưng **không đủ để chi phối tín hiệu học** — đúng cái sai lầm mà phiên bản đầu tiên đã mắc.

#### Kiểm tra trật tự độ lớn

```
Lượt hoàn thành trọn vẹn:  1,0 (đích) + 1,0 (2 lần vượt cổng) + κ·d(s₀)
Toàn bộ khoản theo bước:   từ −0,1  tới  +0,75
```
→ **Σ_b < |R_mt| ✓** — không tồn tại chính sách nào vừa không hoàn thành nhiệm vụ vừa thu tổng phần thưởng cao hơn một chính sách hoàn thành nhiệm vụ. **Phiên bản đầu tiên thiếu đúng tính chất này.**

### 5.2.6. ⭐⭐ Quá trình hiệu chỉnh — phiên bản THẤT BẠI và cách chẩn đoán

> **Đây là phần có giá trị phương pháp luận cao nhất của cả đồ án. Hội đồng rất có thể sẽ hỏi vào đây.**

#### Phiên bản 1 — đi theo trực giác thông thường

Thưởng cho cột mốc trung gian, phạt cho trạng thái bị coi là "xấu":
- Thưởng nhóm khi cả hai tới đích
- Thưởng cá nhân khi đứng trên bàn đạp
- Thưởng khi đã rời phòng xuất phát
- Thưởng nhóm khi cả hai đã rời phòng
- Thưởng đẩy khối vật cản
- Phạt thời gian mỗi bước
- ⚠️ **Phạt nhóm khi một agent đứng trên bàn đạp mà đồng đội chưa rời phòng**
- ⚠️ **Phạt nặng hơn khi một agent đã ra ngoài còn agent kia vẫn kẹt lại**

#### Triệu chứng quan sát được

Huấn luyện với MA-POCA: **phần thưởng nhóm trung bình mắc kẹt ngay ở mức sàn — đúng bằng khoản phạt thời gian tích lũy trọn một lượt chơi — và không nhúc nhích suốt hàng triệu bước.**

> 💡 **Manh mối định lượng rất đáng giá:** việc chỉ số đứng im ở **đúng giá trị của riêng khoản phạt thời gian** nói rằng (a) không lượt chơi nào chạm đích, và (b) không hành vi trung gian nào được tưởng thưởng đủ để kéo chỉ số lên.

#### Ba khuyết tật đan vào nhau

| # | Khuyết tật | Nguyên tắc bị vi phạm |
|---|---|---|
| **1 (nghiêm trọng nhất)** | **Hai khoản phạt nhóm giáng đúng vào những trạng thái mà lời giải bắt buộc phải đi qua.** Màn bàn giao nhất thiết trải qua giai đoạn **bất đối xứng** — một agent giữ bàn đạp, agent kia vượt cổng. Mà đó chính xác là cấu hình bị phạt. **Mọi con đường dẫn tới lời giải đều xuyên qua vùng bị phạt** → chính sách tối ưu cục bộ hóa thành *"không ai cố gắng bàn giao cả"* | **Nguyên tắc 1** — bám theo lời giải mẫu |
| **2** | **Lợi dụng phần thưởng ở giai đoạn cửa mở.** Các khoản trung gian cộng theo bước mà **không chuẩn hóa theo độ dài lượt chơi** → agent nhận ra chỉ cần nấn ná ở một cấu hình cho điểm là đã tích được phần thưởng. Chỉ số phình lên **gần gấp đôi** giá trị của một lời giải sạch → **tạo ảo giác tiến bộ trong khi hành vi thực chất vô nghĩa** | **Nguyên tắc 3** — giữ trật tự độ lớn |
| **3** | **Cửa sập xuống tức thì khi agent rời bàn đạp.** Đòi hỏi đồng bộ thời gian gần như hoàn hảo → xác suất khám phá bằng thử–sai gần bằng 0. **Hàm phần thưởng có đúng đến mấy cũng vô ích, vì hành vi cần học hầu như không bao giờ xuất hiện để mà được tưởng thưởng** | **Nguyên tắc 4** — sửa cơ chế môi trường trước |

#### Bốn thay đổi phối hợp đã khắc phục

1. **Gỡ bỏ toàn bộ khoản phạt nhóm** cho trạng thái bất đối xứng → thay bằng **phần thưởng bàn giao một lần** (chuyển từ **trừng phạt** sang **tưởng thưởng** đúng cái hành vi mà bài toán đòi hỏi)
2. **Thay khoản thưởng cộng dồn theo bước bằng định hình thế năng** (Ng et al.), kèm bảo đảm bất biến chính sách
3. **Thêm khoảng ân hạn 1 giây** cho cửa — đủ ngắn để không agent nào tự vượt cổng, đủ dài để màn bàn giao từ chỗ gần như không thể khám phá trở thành **khả học**
4. **Bổ sung 2 cờ trạng thái vượt cổng** (bản thân + đồng đội) vào quan sát + **chương trình học hai bài**

#### Bài học rút ra (câu chốt)

> **Một hàm phần thưởng hỏng thường để lại dấu vết định lượng rất rõ ngay trên các chỉ số huấn luyện — chẳng hạn việc mắc kẹt đúng ở giá trị của một thành phần phạt. Biết đọc những dấu vết ấy là công cụ chẩn đoán hiệu quả hơn hẳn việc dò tìm hệ số một cách mù quáng.**

### 5.2.7. Học theo chương trình (Curriculum Learning)

Tham số môi trường `handoff_required` điều khiển trạng thái cổng:

```
             ┌ 0 (cổng MỞ)    nếu r̄ < 0,6
Bài học =    │
             └ 1 (cổng KHÓA)  nếu r̄ ≥ 0,6 trong ít nhất 100 lượt liên tiếp
```

- **Bài 1:** vô hiệu hóa 2 cánh cửa → cổng luôn mở → agent chỉ việc học **điều hướng**
- **Bài 2:** cổng bị khóa → màn **bàn giao** thành bắt buộc

→ Cho agent dựng xong nền tảng điều hướng rồi mới phải đối mặt với thách thức phối hợp.

### 5.2.8. Cấu hình huấn luyện

```yaml
behaviors:
  PuzzleBehavior:
    trainer_type: poca                       # MAPPO dùng ĐÚNG file này, chỉ đổi trainer_type: mappo
    hyperparameters:
      batch_size: 1024        buffer_size: 20480
      learning_rate: 3.0e-4   beta: 0.01
      epsilon: 0.2            lambd: 0.95
      num_epoch: 3            learning_rate_schedule: linear
    network_settings:
      normalize: false        hidden_units: 256    num_layers: 3
      vis_encode_type: simple
    reward_signals:
      extrinsic: { gamma: 0.99, strength: 1.0 }
      curiosity: { gamma: 0.99, strength: 0.02, learning_rate: 3.0e-4 }
    max_steps: 1700000      time_horizon: 128     summary_freq: 20000
```

**Kỳ vọng lý thuyết:** MA-POCA là thuật toán hợp nhất (critic tập trung + cơ sở phản thực). MAPPO là đối chứng gần nhất. PPO/SAC/DQN không có cơ chế riêng cho phối hợp → **mốc so sánh để trả lời câu hỏi "critic tập trung có thật sự đáng giá hay không"**.

**Điều kiện kết thúc lượt chơi:**
- *Thành công:* cả hai chạm đích → nhóm nhận +1, toàn bộ khu vực được đặt lại
- *Hết giờ:* 100.000 bước vật lý → lượt chơi bị **ngắt** (interrupted) **chứ không phải kết thúc** — giá trị trạng thái cuối vẫn được ước lượng và đưa vào cập nhật chính sách. **Nếu không, thuật toán sẽ hiểu nhầm trạng thái đó là một thất bại tuyệt đối.**

---

## 5.3. CROSS THE ROAD — Điều hướng đơn tác nhân, phần thưởng thưa

### 5.3.1. Mô tả bài toán

Một agent băng qua con đường có phương tiện chạy liên tục để tới vạch đích mà không va chạm. Hình thức đơn giản, nhưng là **mô hình thu nhỏ của rất nhiều tình huống điều hướng tránh vật cản động trong game** — né đạn, né kẻ địch, vượt chướng ngại đang chuyển động.

> **Thách thức cốt lõi: học được lúc nào nên ĐI và lúc nào nên ĐỢI.** Lao lên đúng lúc có phương tiện qua thì va chạm; mà chờ mãi thì chẳng bao giờ tới đích.

**Bố cục:** 5 làn xe giữa điểm xuất phát và vạch đích. Mỗi làn 1 xe chạy theo chiều cố định, ra khỏi biên thì quay lại đầu làn. **Tốc độ mỗi xe được bốc ngẫu nhiên lại sau từng lượt chơi**, dao động **1–8 đơn vị/giây** tùy làn.

> ⭐ Chính sự ngẫu nhiên này **chặn agent học vẹt một chuỗi hành động cố định**, buộc nó phải học một chính sách phản ứng thật sự dựa trên tình huống quan sát được.

Ngoài xe còn có **tường và cây** làm vật cản tĩnh.

### 5.3.2. Không gian quan sát — 132 giá trị

| Nguồn | Số giá trị | Nội dung |
|---|---|---|
| **Vị trí** | **6** | Tọa độ 3D của agent + tọa độ 3D của đích (hệ tọa độ địa phương) |
| **Cảm biến tia** | **126** | 21 tia × 6 giá trị |

**Cấu hình cảm biến tia:** 21 tia trải đều trong góc quạt **180°** phía trước, tầm xa **40 đơn vị**, **4 nhãn** (xe, tường, cây, đích).

```
o_tia_j = ( chạm_j, d_j/d_max, c_{j,1}, …, c_{j,m} )
dim(o)  = 6 + k × (m + 2) = 6 + 21 × 6 = 132 ✓
```

> ⭐ **Cách phân vai bám sát đúng cấu trúc bài toán:**
> - **Thông tin vị trí** trả lời câu hỏi **"đi về đâu"**
> - **Cảm biến tia** trả lời câu hỏi **"lúc nào thì an toàn để đi"**
>
> Bỏ cảm biến tia → agent mất căn cứ né tránh, chỉ còn nước đoán mù. Bỏ thông tin vị trí → agent né rất giỏi nhưng chẳng biết tiến về hướng nào.

### 5.3.3. Không gian hành động — 4 rời rạc

**4 hành động:** đứng yên, sang trái, sang phải, tiến về phía trước.

**Cơ chế:** một hành động di chuyển đặt ô đích cách vị trí hiện tại **đúng 1 đơn vị**, agent **trượt đều** tới đó; chừng nào chưa tới nơi thì mọi hành động mới đều bị bỏ qua. **Khác hai môi trường kia, chuyển động ở đây không đi qua mô phỏng lực** mà chỉ là phép nội suy vị trí → **quỹ đạo hoàn toàn xác định**.

**Nhịp quyết định:** mỗi **5 bước vật lý** = **10 quyết định/giây**.

> **Rời rạc hóa theo ô lưới là lựa chọn có chủ đích.** Nó đẩy bản chất cốt lõi của bài toán lên hàng đầu: đây là **bài toán quyết định thời điểm** — chọn đúng khoảnh khắc để tiến hay để chờ — chứ không phải bài toán điều khiển vận động tinh vi.
>
> **Hành động "đứng yên" vì thế chẳng phải lựa chọn thừa, mà là một nước đi chiến lược.** Đứng yên đúng lúc để nhường một phương tiện đi qua thường chính là mấu chốt của một lượt chơi thành công.

### 5.3.4. ⭐ Hàm phần thưởng — tối giản nhất, và lập luận đằng sau tỉ lệ 1:40

| Sự kiện | Giá trị | Loại |
|---|---|---|
| Đến được vạch đích | **+1,0** | Thưởng mục tiêu |
| Va chạm với xe, tường hoặc cây | **−0,025** | Phạt mục tiêu |
| Tín hiệu tò mò khuyến khích khám phá | cường độ **0,02** | Nội tại |

Chiếu vào khuôn dạng 3 lớp: **chỉ dùng thành phần mục tiêu** — không định hình, không khoản nào cộng dồn theo bước. Sự tối giản ấy là chủ ý: **quan sát vốn đã chứa sẵn tọa độ đích nên chẳng cần tín hiệu dẫn đường nhân tạo**, còn bài toán thì đủ ngắn để tín hiệu thưa vẫn xuất hiện thường xuyên.

#### Vì sao hình phạt va chạm chỉ bằng 1/40 phần thưởng?

**Vấn đề:** môi trường **không giới hạn số bước**, nên agent luôn có sẵn một lựa chọn tầm thường là **đứng yên vĩnh viễn**, với giá trị kỳ vọng đúng bằng 0.

Gọi p = xác suất băng qua thành công, R₋ = hình phạt va chạm. Tiến lên chỉ hơn đứng yên khi:

```
p · 1 − (1−p) · R₋ > 0    ⟺    p  >  R₋ / (1 + R₋)
```

| R₋ | Ngưỡng p | Diễn giải |
|---|---|---|
| **0,025 (được chọn)** | **2,4%** | Một chính sách vụng về, băng qua thành công **chưa nổi 3 lần trong 100 lần thử**, đã ăn đứt việc đứng yên → **quá trình học luôn có động lực tiến lên ngay từ những bước đầu** |
| **1 (cân bằng)** | **50%** | Agent học được rằng **đứng yên là tối ưu** cho tới lúc nó thắng quá nửa số lần thử — **một điều không tài nào đạt được nếu nó chưa từng thử** |

> ⚠️ **Hiện tượng "chính sách tự đóng băng" là một dạng cực tiểu cục bộ do CHÍNH HÀM PHẦN THƯỞNG tạo ra** — và bất đẳng thức trên cho thấy nó nằm hoàn toàn dưới quyền điều khiển của tỉ lệ giữa hai hằng số.

#### Vì sao hình phạt nhỏ không làm yếu tác dụng răn đe?

> **Vì hình phạt vốn không phải cơ chế răn đe chính.** Va chạm **kết thúc lượt chơi ngay tức khắc** → tổn thất thật sự là **mất trắng cơ hội nhận 1 điểm ở đích**, chứ đâu phải khoản 0,025 bị trừ.
>
> **Chi phí cơ hội mới là thứ răn đe;** hằng số R₋ chỉ để **phá thế hòa giữa các quỹ đạo thất bại**, nên giữ ở mức tối thiểu là hợp lý.

#### Vai trò của tín hiệu tò mò ở đây

Bù cho việc môi trường **không có hình phạt thời gian**:
- **Đứng yên là trạng thái dễ dự đoán nhất** → hầu như chẳng sinh phần thưởng nội tại nào → **chính sách bất động mất động cơ**
- Mà không cần đưa vào khoản phạt cộng dồn vô hạn theo số bước — thứ sẽ **vi phạm ngay Nguyên tắc 3** trong một môi trường không giới hạn độ dài lượt chơi

**Cường độ 0,02** = 1/50 trọng số của tín hiệu ngoại lai: đủ dẫn dắt khám phá lúc đầu, quá nhỏ để làm lệch mục tiêu khi chính sách đã về đích đều đặn.

### 5.3.5. Cấu hình huấn luyện

```yaml
behaviors:
  CrossTheRoad:
    trainer_type: sac            # ví dụ file SAC
    hyperparameters:
      batch_size: 256           buffer_size: 100000
      learning_rate: 3.0e-4     learning_rate_schedule: constant
      buffer_init_steps: 1000   tau: 0.005
      steps_per_update: 20      # ⚠️ tham số quyết định tốc độ hội tụ đo được của SAC
      init_entcoef: 0.5         reward_signal_steps_per_update: 20
    network_settings:
      normalize: false          hidden_units: 128    num_layers: 2
    reward_signals:
      extrinsic: { gamma: 0.99, strength: 1.0 }
      curiosity: { gamma: 0.99, strength: 0.02, learning_rate: 3.0e-4 }
    max_steps: 2000000        time_horizon: 64      summary_freq: 10000
```

**Cấu hình DQN** dùng chung `buffer_size`, `tau`, `steps_per_update` với SAC (để hai thuật toán off-policy tiêu thụ dữ liệu theo cùng nhịp), thêm nhóm riêng:
```yaml
exploration_schedule: linear
exploration_initial_eps: 1.0
exploration_final_eps: 0.05
exploration_decay_steps: 500000
```

**Vai trò của môi trường này:** đây là **môi trường duy nhất** mà cả 5 thuật toán chạy được **mà không phải sửa gì bên phía Unity** → cho phép **so sánh sạch nhất** (không có self-play làm nhiễu thước đo, cũng không có tác nhân thứ hai gây phụ thuộc lẫn nhau).

⚠️ **Lưu ý về kỳ vọng:** đây là môi trường **đơn tác nhân, không có nhóm**, nên ưu thế critic tập trung của MAPPO và MA-POCA **chẳng có đối tượng nào để phát huy** — cả hai **được kỳ vọng suy biến về PPO**. (Kết quả thực đo cho thấy điều ngược lại với MAPPO — xem §7.2.)

**Kết thúc lượt chơi:** chạm đích **hoặc** va chạm → đưa agent về xuất phát, đặt lại xe và bốc tốc độ mới. **Không giới hạn số bước** — an toàn vì hình phạt va chạm + tín hiệu tò mò đã đủ; thực tế cuối huấn luyện độ dài lượt chơi chỉ còn vài chục bước.

---

# PHẦN 6 — Triển khai kỹ thuật & thiết lập thực nghiệm

## 6.1. Đưa MAPPO và DQN vào ML-Agents

### Hai con đường khả dĩ

| | **Con đường 1** — Python Low-Level API | **Con đường 2** — Trainer mở rộng ✅ |
|---|---|---|
| Cách làm | Bỏ hẳn chương trình huấn luyện của ML-Agents, nối qua `mlagents_envs` → dùng thư viện ngoài (Stable-Baselines3) | Giữ nguyên chương trình huấn luyện, chỉ thêm thuật toán mới dưới dạng trainer đăng ký theo tên |
| Ưu | Toàn quyền kiểm soát vòng lặp huấn luyện | **Cả 5 thuật toán chạy trên CÙNG một đường ống** |
| Nhược | Hạ tầng đo khác nhau → không so sánh được | Bị ràng buộc bởi kiến trúc trainer của ML-Agents |

**Đồ án chọn con đường 2** cho cả MAPPO lẫn DQN. **Lý do mang tính quyết định với mục tiêu kiểm chứng môi trường:**

> Chỉ khi cả 5 thuật toán chạy trên cùng một đường ống thu thập quỹ đạo, cùng một cách ghi nhật ký, cùng một định dạng mô hình xuất ra, thì **chênh lệch đo được giữa chúng mới nói lên đặc tính của môi trường** — chứ không phải nói lên sự khác biệt của hạ tầng đo.

### Cơ chế đăng ký

Mỗi trainer mới khai báo một mục trong danh sách `ML_AGENTS_TRAINER_TYPE`, gắn một chuỗi định danh với hàm khởi tạo. Cài gói mở rộng vào rồi thì `mlagents-learn` nhận ra giá trị mới của `trainer_type` trong YAML và khởi tạo đúng lớp trainer đã đăng ký. **Mọi phần khác của quy trình giữ nguyên** — gRPC với Unity, ghi TensorBoard, lưu checkpoint, xuất ONNX.

### MAPPO được cài như thế nào?

**Kế thừa bộ tối ưu của MA-POCA**, giữ nguyên mạng critic đa tác nhân (nhận quan sát cả nhóm làm đầu vào).

**Điểm khác biệt duy nhất — cách tính lợi thế:**
- **MA-POCA**: trừ đi một **đường cơ sở phản thực** (counterfactual baseline) ước lượng riêng cho từng agent
- **MAPPO**: tính lợi thế **trực tiếp so với giá trị tập trung**, bỏ hẳn số hạng đường cơ sở khỏi hàm mất mát

> ⭐ Đó **chính xác** là điểm phân biệt hai phương pháp về mặt thuật toán. Cài đặt kiểu này bảo đảm **mọi chênh lệch quan sát được giữa MAPPO và MA-POCA đều đến từ cơ chế gán công lao**, chứ không từ kiến trúc mạng hay siêu tham số. Cấu hình MAPPO vì vậy dùng **đúng bộ siêu tham số** của PPO và MA-POCA.

### DQN được cài như thế nào?

**Kế thừa lớp trainer off-policy có sẵn** — chính lớp mà SAC đang dùng → thừa hưởng nguyên vẹn replay buffer và lịch cập nhật theo `steps_per_update`.

**Phần phải viết mới:** một mạng Q + mạng mục tiêu cập nhật mềm, hàm mất mát TD, quy tắc ε-tham lam.

**Ràng buộc kỹ thuật lớn nhất:** DQN chỉ làm việc được với **hành động rời rạc** → Football Table phải dựng lại thành bản riêng, `BehaviorParameters` chuyển từ **8 kênh liên tục** sang **8 nhánh 3 mức**.

### Con đường 1 vẫn được dựng xong và kiểm chứng

```python
from mlagents_envs.environment import UnityEnvironment
from mlagents_envs.envs.unity_gym_env import UnityToGymWrapper
from stable_baselines3 import SAC

unity_env = UnityEnvironment(file_name=None, base_port=5005)
env = UnityToGymWrapper(unity_env, allow_multiple_obs=False)

model = SAC("MlpPolicy", env, learning_rate=3e-4, buffer_size=500000,
            batch_size=1024, tau=0.005, gamma=0.99, ent_coef="auto",
            policy_kwargs=dict(net_arch=[512, 512, 512]), verbose=1)
model.learn(total_timesteps=10_000_000)
```

> ⚠️ **Phải nói rõ để khỏi hiểu nhầm:** **15/15 lần chạy báo cáo ở Chương 4 đều dùng chương trình huấn luyện của ML-Agents, kể cả 5 lần chạy SAC.** Đường đi qua Stable-Baselines3 xuất hiện với tư cách **một phương án đã dựng xong và dùng lại được**, chứ **không phải nguồn của bất kỳ con số nào** trong bảng kết quả.

## 6.2. Cấu trúc mã nguồn Python bổ sung

| Thành phần | Vai trò |
|---|---|
| **Chương trình điều phối** | Chạy tuần tự 15 lần huấn luyện, tự nạp đúng file cấu hình cho từng tổ hợp môi trường–thuật toán, quản lý trạng thái tiến độ, ghi nhật ký, **tiếp tục từ điểm dừng nếu bị gián đoạn** |
| **Gói trainer mở rộng** | Cung cấp MAPPO và DQN + lớp bọc môi trường cho con đường tích hợp qua thư viện ngoài |
| **`export_training_data.py`** | Đọc file sự kiện TensorBoard của cả 15 lần chạy, trích chỉ số (reward, độ dài lượt chơi, loss, entropy), tự sinh biểu đồ so sánh + báo cáo tổng hợp |

## 6.3. Cấu hình phần cứng và phần mềm

| Thành phần | Chi tiết |
|---|---|
| CPU | **Intel Core i5-14600KF** |
| GPU | **NVIDIA GeForce RTX 3050** |
| RAM | **32 GB** |
| Hệ điều hành | Windows 11 |
| Unity ML-Agents | **4.0.2** trên Unity **6000.3** |
| Nền tảng học sâu | **PyTorch 2.2.2** với **CUDA 12.1** |
| Thư viện bổ sung | Stable-Baselines3, giao diện Python của ML-Agents |
| Hệ số tăng tốc mô phỏng | **×20** thời gian thực |

> 💡 **Điểm đáng nói:** cấu hình chỉ dùng **một GPU tầm trung** — đúng điều kiện thực tế mà phần lớn sinh viên và nhà phát triển độc lập có thể với tới → **các kết luận của đồ án cũng thực tiễn hơn**.

## 6.4. Siêu tham số — nguyên tắc thiết lập

> **Nguyên tắc: những tham số chung (learning rate, γ, kiến trúc mạng) phải GIỐNG NHAU nhiều nhất có thể giữa 5 thuật toán trên cùng một môi trường, để khác biệt về kết quả phản ánh BẢN CHẤT THUẬT TOÁN chứ không phải chênh lệch tham số.**

| Tham số | PPO | SAC | MA-POCA | MAPPO | DQN |
|---|---|---|---|---|---|
| **Tốc độ học** | 3e−4 | 3e−4 | 3e−4 | 3e−4 | 3e−4 |
| **Hệ số chiết khấu γ** | 0,99 | 0,99 | 0,99 | 0,99 | 0,99 |
| Kích thước lô | 512–2048 | 256–1024 | 512–2048 | 512–2048 | 256–1024 |
| Kích thước bộ đệm | 10K–41K | **100K–500K** | 10K–41K | 10K–41K | **100K–500K** |
| Số đơn vị ẩn | 128–256 | 128–256 | 128–256 | 128–256 | 128–256 |
| Số lớp ẩn | 2–3 | 2–3 | 2–3 | 2–3 | 2–3 |
| Cơ chế riêng | cắt tỉ lệ 0,2 | cập nhật mềm 0,005 | phê bình tập trung | phê bình tập trung + chia sẻ | mạng mục tiêu + ε-tham lam |

**Kiến trúc mạng cố định theo môi trường:**
- Cross The Road: **2 lớp × 128**
- Football Table: **2 lớp × 256**
- Capture The Flag: **3 lớp × 256**

**Hai thuật toán off-policy dùng chung `steps_per_update = 20`** — mạng chỉ được cập nhật 1 lần sau mỗi 20 bước môi trường. Giá trị này chọn để thời gian chạy nằm gọn trong quỹ thời gian của đồ án, và **nó ảnh hưởng trực tiếp lên tốc độ hội tụ đo được của SAC** (xem §7.5).

## 6.5. ⭐ Bốn tiêu chí đánh giá

| # | Tiêu chí | Định nghĩa chính xác | Vì sao định nghĩa như vậy |
|---|---|---|---|
| **1** | **Mức năng lực đạt được** | Phần thưởng **trung bình của 10% cuối** quá trình huấn luyện | Phản ánh mức hiệu năng **ổn định** giữ được ở cuối, thay vì một giá trị tức thời có khi chỉ là đỉnh nhiễu |
| **2** | **Tốc độ hội tụ** | Bước huấn luyện **đầu tiên mà từ đó trở đi** đường cong **không còn tụt xuống dưới 90%** mức năng lực ổn định cuối | **Bền hơn tiêu chí "lần đầu chạm ngưỡng"** — không bị một đỉnh nhiễu đơn lẻ kéo về đầu chuỗi. Đánh đổi: lần chạy còn dao động mạnh ở cuối sẽ **"không đạt"** — mà bản thân điều đó cũng là một kết quả cần báo cáo |
| **3** | **Độ ổn định huấn luyện** | **Độ lệch chuẩn** của đường cong phần thưởng trên 10% cuối | Đường cong càng ít dao động, quá trình học càng bền |
| **4** | **Độ dài lượt chơi** | Trung bình số bước/lượt | ⭐ Cả 3 môi trường đều kết thúc lượt chơi ngay khi nhiệm vụ xong → **đại lượng thay thế đo được cho tỷ lệ hoàn thành**. Đặc biệt có ích: **tách được hai kiểu kết thúc sớm mà riêng phần thưởng không phân biệt nổi — về đích nhanh, hay thất bại sớm** |

**Riêng môi trường đối kháng dùng thêm chỉ số ELO** — bởi trong self-play, **phần thưởng tuyệt đối không nói lên tiến bộ khi cả hai phía cùng mạnh lên**.

**Quy ước chữ "cuối":** mọi đại lượng (entropy, phần thưởng tò mò, hàm mất mát phê bình, độ dài lượt chơi) đều lấy **trung bình 10% cuối chuỗi tương ứng**. **Ngoại lệ duy nhất là ELO** — đại lượng này tích lũy theo thời gian nên chỉ giá trị tại bước cuối mới có nghĩa.

**Nguồn số liệu:** trích thẳng từ file sự kiện TensorBoard (`Environment/Cumulative Reward`), **không qua bước làm mượt nào** → từng điểm trên đồ thị đối chiếu được với đúng một bản ghi trong file sự kiện, bảng số liệu luôn khớp đồ thị.

---

# PHẦN 7 — Kết quả 15 lần chạy & cách đọc số liệu

## 7.0. Bảng tổng hợp toàn bộ 15 lần chạy

| Môi trường | Lần chạy | Thuật toán | Bước | Reward TB (10% cuối) | Thời gian |
|---|---|---|---|---|---|
| **Cross The Road** | `ctr01` | PPO | 2,00M | 0,690 | ~48 phút |
| | `CrossTheRoad_SAC_01` | SAC | 2,00M | **0,846** 🥇 | ~139 phút |
| | `ctr_poca_v1` | MA-POCA | 2,00M | 0,556 | ~59 phút |
| | `ctr_mappo_v1` | MAPPO | 2,00M | 0,835 | ~58 phút |
| | `ctr_dqn_v1` | DQN | 2,00M | **0,336** ⚠️ | ~148 phút |
| **Capture The Flag** | `ctf_ppo_v1` | PPO | 1,70M | 0,834 | ~50 phút |
| | `ctf_sac_v1` | SAC | 1,70M | **0,183** ❌ | ~152 phút † |
| | `ctf_poca_v2` | MA-POCA | 1,70M | 0,838 | ~53 phút |
| | `ctf_mappo_v2` | MAPPO | 1,70M | **0,840** 🥇 | ~52 phút |
| | `ctf_dqn_v1` | DQN | 1,70M | 0,800 | ~258 phút |
| **Football Table** | `FB01` | PPO | 1,60M | 1,691 (ELO 1259) | ~47 phút |
| | `Football_SAC_01` | SAC | 1,60M | 1,842 (ELO 1254) | ~165 phút |
| | `Football_POCA_01` | MA-POCA | 1,60M | 1,752 (ELO 1237) | ~50 phút |
| | `Football_MAPPO_01` | MAPPO | 1,60M | **2,117** (ELO **1260**) 🥇 | ~48 phút |
| | `football_dqn_v1` | DQN ‡ | 1,60M | 1,825 (không có ELO) | ~147 phút |

† Thời gian `ctf_sac_v1` chỉ tính đoạn 1,0M–1,7M sau khi khôi phục từ checkpoint.
‡ DQN trên Football phải **tắt self-play** → **không so sánh trực tiếp được** với 4 thuật toán còn lại.

---

## 7.1. Football Table — đọc theo ELO, không đọc theo phần thưởng

> ⚠️ **Điều phải nói trước vì nó chi phối cách đọc cả chương:** trong cơ chế tự chơi, **phần thưởng tuyệt đối là chỉ báo gây hiểu nhầm**. Cả hai phía cùng mạnh lên thì lợi thế bên này bị bù trừ bởi tiến bộ bên kia → đường cong phần thưởng dao động quanh mức gần như đứng yên thay vì tăng đều. **Mọi kết luận về Football Table đều dựa trên ELO.**

| Thuật toán | Reward TB | Reward tốt nhất | Độ lệch chuẩn | **ELO cuối** | ELO đầu → cuối |
|---|---|---|---|---|---|
| PPO | 1,691 | 3,548 | **0,276** (mượt nhất) | 1259 | 1199 → 1259 (**+60**) |
| SAC | 1,842 | 3,237 | 0,432 | 1254 | 1197 → 1254 (**+57**) |
| MA-POCA | 1,752 | 2,867 | **0,590** (dao động nhất) | **1237** | 1201 → 1237 (**+36**) |
| MAPPO | **2,117** | 3,394 | 0,486 | **1260** | 1196 → 1260 (**+64**) |
| DQN ‡ | 1,825 | 2,028 | 0,073 ‡ | — | — |

### Cách đọc ELO đúng

> ⚠️ **ELO của hai lần chạy khác nhau KHÔNG đem so trực tiếp với nhau được** — mỗi lần chạy tính điểm dựa trên **kho đối thủ của riêng nó**. Đại lượng có nghĩa là **mức tăng so với giá trị khởi tạo 1200**.

**Kết luận rút được:** cả 4 thuật toán đều **học được cách đánh bại chính mình**. Không lần chạy nào kết thúc dưới điểm xuất phát → tiêu chí **"học được" ✓**

### Diễn biến các đường cong khác nhau khá nhiều

| Thuật toán | Diễn biến | Diễn giải |
|---|---|---|
| **PPO** | Tăng gần như đơn điệu tới ~1,1M bước rồi **đứng im hẳn ở 1258,9** cho tới hết | Chính sách **không còn vượt nổi kho đối thủ** |
| **MAPPO** | Tăng chậm hơn nhưng **vẫn dốc lên ở đoạn cuối**, đỉnh 1265,7, khép ở 1260,0 | **Chưa chạm trần trong ngân sách đã cho** |
| **SAC** | Gần như **bất động quanh mốc khởi tạo suốt 900K bước đầu** rồi mới bứt lên nửa sau | Đúng đặc điểm off-policy — cần thời gian **nạp đầy bộ đệm** trước khi chính sách bắt đầu cải thiện |

### ⚠️ Cảnh báo về độ phân giải

Khoảng cách **1 điểm** giữa MAPPO (1260) và PPO (1259) **nhỏ hơn nhiều so với biên độ dao động của chính đường cong ELO** — riêng MAPPO đã dao động trong dải **gần 20 điểm** ở đoạn cuối.

> **Phân tách DUY NHẤT đứng vững: MA-POCA tụt lại sau ba thuật toán còn lại.**

**Vì sao biên độ chung quá hẹp?** Cơ chế tự chơi tạo ra một chương trình học tự nhiên — độ khó của đối thủ tăng dần theo năng lực agent. Nhưng khi cả hai phía cùng mạnh lên với **tốc độ xấp xỉ nhau**, ELO gần như đứng yên **dù chính sách vẫn đang cải thiện**.

→ **Football Table chỉ đạt 2/3 tiêu chí nghiệm thu** (học được ✓, không có lối tắt ✓, **phân biệt được ✗**).

**Về độ lệch chuẩn:** trong nhóm self-play, PPO dao động ít nhất (0,276), MA-POCA nhiều nhất (0,590). Giá trị **0,073** của DQN thấp hơn hẳn nhưng **không đem so được** — DQN không chạy self-play nên đối thủ cố định, mà môi trường không đổi thì đương nhiên cho đường cong phẳng hơn.

---

## 7.2. Cross The Road — môi trường cho phép so sánh SẠCH NHẤT

| Thuật toán | Reward TB | Reward tốt nhất | **Bước hội tụ** | **Độ dài lượt chơi** | Độ lệch chuẩn | Entropy cuối |
|---|---|---|---|---|---|---|
| PPO | 0,690 | 1,000 | ~1,97M | **811,6** ⚠️ | **0,116** (dao động nhất) | 0,79 |
| **SAC** | **0,846** 🥇 | 0,914 | ~1,79M | 61,8 | 0,025 | 0,28 |
| MA-POCA | 0,556 | 0,616 | **~450K** (sớm nhất) | 42,2 | **0,017** (mượt nhất) | **0,20** |
| MAPPO | **0,835** 🥈 | 0,900 | ~1,72M | 52,0 | 0,024 | 0,43 |
| DQN | **0,336** ⚠️ | 0,633 | **Không đạt** | 124,7 | — | — (không có) |

### Bốn phát hiện

**① SAC dẫn đầu (0,846), MAPPO bám sát (0,835).** Khoảng cách 0,011 **nhỏ hơn biên độ dao động** của chính các đường cong ở giai đoạn cuối → số liệu một lần chạy chưa đủ để khẳng định ai thực sự dẫn đầu. Điều **nói chắc được**: cả hai **tách hẳn khỏi phần còn lại** (PPO 0,690, MA-POCA 0,556, DQN 0,336).

→ **Phổ 0,336 → 0,846 đủ rộng** → tiêu chí **"phân biệt được" ✓**. Đây là môi trường duy nhất cho phổ đủ rộng để xếp hạng có nghĩa.

**② ⭐ Hội tụ sớm ≠ học nhanh.**
> MA-POCA chạm mốc ổn định **sớm nhất nhóm (~450K)** — nhưng **hội tụ về mức thấp (0,556) rồi nằm im ở đó tới cuối**. **Đó là sự ổn định của một chính sách tầm thường, không phải dấu hiệu học nhanh.**

Khớp với nhận định MA-POCA **suy biến gần về PPO** ở bài toán đơn tác nhân: không có phần thưởng nhóm thì thế mạnh critic tập trung chẳng có chỗ phát huy, trong khi chi phí kiến trúc phức tạp hơn vẫn phải gánh.

**③ ⚠️ MAPPO ĐẢO NGƯỢC dự đoán ban đầu.**
> Xét thiết kế, MAPPO nhắm tới bài toán hợp tác đa tác nhân → trên môi trường **đơn tác nhân** nó được kỳ vọng **suy biến thành PPO thường**. Thực đo cho thấy ngược lại: **MAPPO 0,835 vs PPO 0,690**, dù hai thuật toán **chỉ khác nhau ở phần critic tập trung** — thứ lẽ ra vô hiệu khi nhóm chỉ có một thành viên.

**Đồ án thừa nhận thẳng: chưa giải thích được cơ chế đằng sau**, và với đúng 1 lần chạy mỗi thuật toán thì cũng chưa loại trừ được khả năng đây chỉ là dao động ngẫu nhiên giữa các seed. **Nếu mở rộng thực nghiệm, đây là điểm đáng kiểm chứng trước tiên.**

**④ DQN xếp cuối, cách biệt khá xa** (0,336, chưa bằng một nửa SAC). Theo tiêu chí hội tụ, đường cong **không đạt mốc ổn định nào** trước khi hết ngân sách — thuật toán vẫn còn dao động lúc dừng. Cộng thêm thời gian chạy **148 phút, gấp 3 lần PPO** → **lựa chọn kém hiệu quả nhất trên môi trường này xét cả về mẫu lẫn thời gian**.

### ⭐ Độ dài lượt chơi tách các thuật toán RÕ HƠN CẢ PHẦN THƯỞNG

4/5 thuật toán giữ độ dài lượt chơi trong khoảng 42–130 bước suốt quá trình. **Riêng PPO mất ổn định hoàn toàn từ khoảng 600K bước trở đi:** đường cong nhảy giữa **270 và 2.547 bước**, trung bình 10% cuối lên tới **811,6**.

> Lượt chơi kéo dài như thế nghĩa là **agent không kết thúc nổi — nó lang thang, không về đích mà cũng chẳng va chạm.**

**Ghép phần thưởng + độ dài lượt chơi phân biệt được hai kiểu kết thúc sớm trông y hệt nhau:**

| Thuật toán | Độ dài | Reward | → Diễn giải |
|---|---|---|---|
| MAPPO | 52,0 (ngắn) | 0,835 (cao) | ✅ **Về đích nhanh** |
| MA-POCA | 42,2 (ngắn) | 0,556 (thấp) | ❌ **Kết thúc do va chạm** |
| SAC | 61,8 (giữa) | 0,846 (cao nhất) | ✅ Tốt |
| DQN | 60 → 130+ (tăng dần) | 0,336 (thấp nhất) | ⚠️ **Chính sách ngày càng lưỡng lự** |

### ⚠️ Bất thường quan trọng nhất: entropy của PPO TĂNG NGƯỢC

Cả 4 thuật toán policy-based xuất phát quanh **1,37** (khám phá ngẫu nhiên ban đầu), rồi rẽ theo hướng khác nhau:

- MA-POCA: giảm đều, kết thúc thấp nhất (**0,204**) — chính sách quyết đoán nhất. Nhưng đặt cạnh reward chỉ 0,556 → **dấu hiệu chốt sớm vào phương án tầm thường**, khớp với mốc hội tụ rất sớm ~450K
- SAC: giảm dốc rồi ổn định quanh **0,280**
- MAPPO: dừng ở mức cao hơn (**0,429**) → **vẫn giữ được một phần khả năng khám phá trong khi reward đã gần chạm mức cao nhất**
- ⚠️ **PPO: giảm xuống 0,657 ở ~290K bước, rồi QUAY ĐẦU TĂNG NGƯỢC và giữ quanh 0,8 cho tới hết**

> **Entropy tăng nghĩa là chính sách ngày càng kém dứt khoát theo thời gian — ngược hẳn diễn biến của một quá trình huấn luyện lành mạnh.**
>
> **Ba chỉ số cùng dẫn tới một cách giải thích:** (1) entropy tăng ngược, (2) độ dài lượt chơi bùng nổ từ cùng thời điểm, (3) reward dừng ở mức trung bình dù ngân sách ngang bằng → **chính sách PPO đã rời khỏi vùng nghiệm tốt sau giai đoạn đầu và không tìm được đường quay lại.**

### ⚠️ Bẫy khi đọc hàm mất mát phê bình

- **SAC**: rơi về gần 0 chỉ sau vài trăm nghìn bước (off-policy tái dùng dữ liệu đã lưu)
- **Ba thuật toán họ PPO**: giữ mức dương nhỏ, ổn định — đặc trưng on-policy, critic phải liên tục thích ứng với dữ liệu mới
- ⚠️ **DQN**: sau một đỉnh nhọn ở vài nghìn bước đầu, rơi xuống **~0,001** rồi nằm im — **thấp hơn cả ba thuật toán họ PPO**. **Vậy mà DQN chính là thuật toán có phần thưởng THẤP NHẤT.**

> **Hàm mất mát phê bình nhỏ chỉ nói rằng mạng dự đoán khớp với mục tiêu DO CHÍNH NÓ đặt ra, chứ chẳng bảo đảm mục tiêu ấy dẫn tới một chính sách tốt. Đọc chỉ số này tách rời khỏi phần thưởng là con đường ngắn nhất tới kết luận sai.**

---

## 7.3. Capture The Flag — trường hợp SAC sụp đổ

| Thuật toán | Reward TB | Reward tốt nhất | Bước hội tụ | **Độ dài lượt chơi** | Độ lệch chuẩn | Entropy cuối | Tò mò cuối |
|---|---|---|---|---|---|---|---|
| PPO | 0,834 | 0,844 | **~180K** | 292,9 | 0,006 | 0,82 | 1,146 |
| **SAC** | **0,183** ❌ | 0,795 | **Không đạt** | **4999,0** (trần) | **0,210** | **1,74** | **18,726** |
| MA-POCA | 0,838 | 0,844 | ~540K | 174,3 | 0,002–0,006 * | 0,72 | 0,577 |
| **MAPPO** | **0,840** 🥇 | 0,852 | ~260K | **153,3** | **0,002** | **0,65** | **0,478** |
| DQN | 0,800 | 0,836 | ~1,04M | 2017,9 | — | — | 7,014 |

\* Bản gốc chỉ nêu dải "từ 0,002 của MAPPO tới 0,006 của PPO" cho cả ba thuật toán họ PPO, không ghi riêng giá trị của MA-POCA.

### Kết quả chia thành hai nhóm rất rõ

**Nhóm dẫn đầu:** MAPPO (0,840), MA-POCA (0,838), PPO (0,834), DQN (0,800) — **cùng về đích trong một dải rộng 0,04**.
**SAC đứng lẻ loi ở 0,183.**

> ⚠️ Khoảng cách giữa 4 thuật toán dẫn đầu **còn nhỏ hơn dao động của chính các đường cong** → ở cấu hình hiện tại, **môi trường này không phân biệt nổi chúng**.

**Bằng chứng đáng tin hơn phần thưởng nằm ở độ dài lượt chơi:** 4 thuật toán dẫn đầu đều kéo được xuống thấp (153,3 của MAPPO → 2017,9 của DQN) → **chúng đều học được cách kết thúc câu đố** thay vì để hết giờ.

**Đáng chú ý:** MAPPO và MA-POCA xuống thấp nhất và sớm nhất — **hợp lý vì cả hai đều có critic tập trung nhìn được quan sát cả nhóm**. Nhưng **PPO thường, vốn chẳng có cơ chế nào dành riêng cho phối hợp, cũng đạt 0,834 và rút lượt chơi xuống 292,9 bước.**

### ⭐ SAC thất bại theo một kiểu RẤT RIÊNG — bốn chỉ số độc lập cùng chỉ về một hướng

| # | Chỉ số | Quan sát | Diễn giải |
|---|---|---|---|
| **1** | **Độ dài lượt chơi** | Nằm lì ở trần **4999 bước** gần như suốt quá trình | Hai agent **hầu như không bao giờ giải xong câu đố** |
| **2** | **Phần thưởng** | **Nhảy dữ dội giữa −0,018 và 0,795**. 11/44 điểm đo vượt 0,5, và **đúng 11 điểm** nằm dưới 0,1. Độ lệch chuẩn toàn chuỗi **0,221** | ⭐ **Chính sách không phải là không học được gì; nó HỌC ĐƯỢC RỒI ĐÁNH MẤT, lặp đi lặp lại.** Con số 0,183 chỉ là kết quả của việc lấy trung bình trên một chuỗi dao động — **không mô tả năng lực ổn định nào cả** |
| **3** | **Entropy** | Xuất phát 1,946 (= ln 7, cực đại cho 7 hành động) → **lao xuống đáy 0,013 tại bước 620K** (gần như chính sách xác định hoàn toàn) → **bật ngược lên ĐÚNG mức cực đại 1,946**, nằm lì suốt 1,04M–1,26M, chỉ giảm chậm về 1,663 ở bước cuối | ⭐ **Bằng chứng trực tiếp nhất: SAC từng học được một chính sách có cấu trúc rồi ĐÁNH MẤT SẠCH, quay về trạng thái chọn hành động ngẫu nhiên đều nhau.** Vấn đề không phải SAC học quá chậm, mà là **nó không giữ nổi thứ đã học** |
| **4** | **Phần thưởng tò mò** | Chỉ giảm từ **33,6 xuống 18,7** rồi dừng — trong khi MAPPO xuống 0,478, MA-POCA 0,577, PPO 1,146 | **Mô hình động lực của nó vẫn liên tục dự đoán sai. Sau 1,7 triệu bước, thế giới của SAC vẫn xa lạ y như lúc bắt đầu** |

**So sánh: ba thuật toán họ PPO** đều giảm entropy gần như đơn điệu và song song nhau (chỉ khác độ dốc): MAPPO 0,645, MA-POCA 0,719, PPO 0,820 — **cả ba đều đã định hình được một chính sách có cấu trúc**.

### Chi tiết đồ thị cần giải thích để khỏi hiểu nhầm

Đường cong reward của SAC **dừng ở ~1,64M bước**, trong khi 4 đường kia kéo tới hết 1,70M. **Nhưng lần chạy này không hề ngắn hơn** — chuỗi entropy và loss của nó đều đủ điểm tới bước cuối.

**Nguyên do:** ML-Agents **chỉ ghi phần thưởng tích lũy khi một lượt chơi KẾT THÚC**, mà lượt chơi của SAC gần như luôn chạm trần thời gian → 60K bước cuối chẳng có lượt nào kết thúc để sinh bản ghi mới.

> Bản thân **chuỗi phần thưởng thưa thớt của SAC — vỏn vẹn 44 điểm so với 79 điểm của MA-POCA và MAPPO — đã là một dấu hiệu thất bại.**

### Giả thuyết về cơ chế (đồ án thừa nhận chưa xác định được)

> **Giả thuyết khớp với dữ liệu:** replay buffer của SAC **lưu lẫn lộn kinh nghiệm của HAI bài học** trong chương trình học, khiến critic phải khớp đồng thời hai chế độ phần thưởng khác nhau.
>
> **Cách kiểm chứng:** chạy lại với **bộ đệm tách riêng theo từng bài học**. Nằm ngoài phạm vi đã làm.

**Đỉnh nhọn ở nửa đầu của cả 5 đường cong tò mò** ứng với thời điểm **chương trình học chuyển bài** — `handoff_required` vừa bật lên là môi trường đột ngột sinh ra những trạng thái mà mô hình động lực chưa từng gặp → sai số dự đoán vọt lên.

---

## 7.4. Bảng chỉ số huấn luyện nội tại (các môi trường hành động rời rạc)

| Lần chạy | Thuật toán | Entropy đầu → cuối | Mất mát phê bình cuối | Thưởng tò mò cuối |
|---|---|---|---|---|
| Cross The Road | PPO | 1,37 → **0,79** ⚠️(tăng ngược) | 0,006 | 0,201 |
| Cross The Road | SAC | 1,37 → 0,28 | ≈ 0,000 | 0,038 |
| Cross The Road | MA-POCA | 1,38 → **0,20** | 0,025 | **0,007** (thấp nhất) |
| Cross The Road | MAPPO | 1,38 → 0,43 | 0,010 | 0,015 |
| Cross The Road | DQN | — | 0,001 | 0,112 |
| Capture The Flag | PPO | 1,95 → 0,82 | 0,051 | 1,146 |
| Capture The Flag | **SAC** | 1,95 → **1,74** ❌ | ≈ 0,000 | **18,726** ❌ |
| Capture The Flag | MA-POCA | 1,95 → 0,72 | 0,047 | 0,577 |
| Capture The Flag | MAPPO | 1,95 → **0,65** | 0,047 | **0,478** |
| Capture The Flag | DQN | — | 0,001 | 7,014 |

**Phần thưởng tò mò là chỉ số phân tách mạnh nhất** — biên độ trải **hơn ba bậc độ lớn**, từ 0,007 (MA-POCA/CTR) tới 18,726 (SAC/CTF).

### ⚠️ Entropy phải đọc thận trọng — nó KHÔNG phải chỉ báo chất lượng

| Môi trường | Entropy có dự đoán được thứ hạng không? |
|---|---|
| **Capture The Flag** | ✅ **CÓ** — 3 thuật toán giải được câu đố đều hạ entropy xuống dải 0,65–0,82, còn SAC giữ nguyên 1,74 trên mức cực đại 1,95. **Chênh lệch đó là chỉ báo SỚM NHẤT và RÕ NHẤT cho thất bại của SAC — nó xuất hiện TRƯỚC CẢ khi ta nhìn vào phần thưởng** |
| **Cross The Road** | ❌ **KHÔNG** — MA-POCA hạ entropy thấp nhất (0,20) mà reward chỉ 0,556; PPO giữ entropy cao nhất (0,79) và cũng chỉ được 0,690 |

> **Kết luận: entropy thấp cho biết chính sách đã QUYẾT ĐOÁN, chứ không nói được nó quyết đoán về một phương án TỐT hay XẤU.**

### Hàm mất mát phê bình phải đọc trong ngữ cảnh riêng của từng thuật toán

- **SAC ≈ 0,000**: critic hội tụ nhanh nhờ tái dùng dữ liệu đã lưu
- **DQN 0,001**: nguyên nhân khác hẳn — mạng dự đoán khớp với mục tiêu **do chính nó sinh ra**, chuyện vẫn xảy ra ngay cả khi chính sách kém
- **Ba thuật toán họ PPO**: mức dương nhỏ, và **cao hơn hẳn ở Capture The Flag (0,047–0,051) so với Cross The Road (0,006–0,025)** — hợp lý, vì **phần thưởng nhóm vừa thưa vừa trì hoãn khiến việc ước lượng giá trị khó hơn nhiều**

---

## 7.5. Đánh giá tổng hợp

### Xếp hạng theo từng môi trường

| Môi trường | Hạng 1 | Hạng 2 | Hạng 3 | Hạng 4 | Hạng 5 |
|---|---|---|---|---|---|
| **Football Table** (theo ELO) | MAPPO | PPO | SAC | MA-POCA | DQN (N/A) |
| **Cross The Road** (theo reward) | SAC | MAPPO | PPO | MA-POCA | DQN |
| **Capture The Flag** (theo reward) | MAPPO | MA-POCA | PPO | DQN | SAC |

> ⚠️ **Cảnh báo về độ phân giải — đọc kèm bảng này:**
> - Football Table: 4 thuật toán self-play chen nhau trong dải ELO **1237–1260**
> - Capture The Flag: 4 thuật toán dẫn đầu nằm gọn trong dải reward **0,800–0,840**
>
> Những khoảng cách ấy **còn nhỏ hơn dao động của chính các đường cong** → **thứ tự trong nội bộ hai nhóm đó ĐỪNG coi là kết luận.**
>
> **Chỉ BA phân tách là thực sự vững:**
> 1. **SAC thất bại trên Capture The Flag**
> 2. **DQN xếp cuối trên Cross The Road**
> 3. **Nhóm dẫn đầu tách khỏi nhóm sau ở Cross The Road**

### ⭐ Bức tranh KHÔNG giống giả thuyết ban đầu

**Giả thuyết ban đầu:** "mỗi thuật toán thắng trên đúng loại bài toán nó được thiết kế cho." **Dữ liệu bác bỏ:**

| Kỳ vọng | Thực tế |
|---|---|
| Capture The Flag (hợp tác) là **sân của các phương pháp đa tác nhân** | 4 thuật toán về đích trong dải 0,04; **PPO thường bám sát MAPPO**. Critic tập trung của MA-POCA và MAPPO **không tạo nổi khác biệt đo được** so với PPO |
| Cross The Road (đơn tác nhân) → MAPPO **suy biến thành PPO** | MAPPO **vượt PPO một khoảng lớn** (0,835 vs 0,690) |
| Football Table → PPO self-play dẫn đầu | Biên độ ELO hẹp tới mức **không phân định nổi** 4 thuật toán self-play |

### ⭐⭐ Cái mà dữ liệu ỦNG HỘ CHẮC CHẮN

> **Sự phù hợp giữa thuật toán và môi trường CÓ THẬT, nhưng nó lộ ra qua THẤT BẠI rõ hơn qua CHIẾN THẮNG.**
>
> - SAC dẫn đầu Cross The Road (**0,846**) rồi sụp đổ hoàn toàn ở Capture The Flag (**0,183**) — chênh lệch **0,663**
> - DQN xếp cuối Cross The Road (0,336) nhưng lại **nằm trong nhóm giải được câu đố** ở Capture The Flag (0,800)
> - Trong khi đó chênh lệch **nội bộ** từng môi trường chỉ 0,04 (CTF) và 0,011 (nhóm đầu CTR)
>
> **→ CHỌN SAI thuật toán cho một cơ chế game gây thiệt hại LỚN HƠN NHIỀU so với cái lợi của việc CHỌN ĐÚNG thuật toán tốt nhất trong nhóm khả dụng.**

⚠️ **Lưu ý khi đọc biểu đồ cột so sánh:** chiều cao các cột **chỉ đem so được trong nội bộ từng môi trường**, vì thang phần thưởng ba môi trường vốn thiết kế khác nhau. Football Table cộng dồn nhiều thành phần định hướng nên thang lớn hơn hẳn; Cross The Road và Capture The Flag đã chuẩn hóa quanh mức 1 đơn vị / lần hoàn thành nhiệm vụ.

### ⭐ Tốc độ hội tụ — hiệu quả mẫu của SAC là ĐẠI LƯỢNG ĐÁNH ĐỔI ĐƯỢC

> **Số bước hội tụ chỉ có nghĩa khi đọc kèm MỨC NĂNG LỰC mà chính sách hội tụ tới.** MA-POCA chạm mốc ổn định sớm nhất (~450K) nhưng ổn định ở 0,556; SAC và MAPPO phải tới ~1,7M nhưng đạt 0,846 và 0,835. **Hội tụ sớm ở đây là dấu hiệu chốt vào phương án tầm thường, không phải học nhanh.**

**Ưu thế hiệu quả mẫu của SAC hóa ra chỉ xuất hiện CÓ ĐIỀU KIỆN:**

| Cấu hình `steps_per_update` | Bước hội tụ của SAC |
|---|---|
| **1** (cập nhật mỗi bước môi trường) | **~150.000 bước** |
| **20** (dùng trong đồ án, để thời gian chạy khả thi) | **~1.790.000 bước** |

> **→ Hiệu quả mẫu của thuật toán off-policy là một ĐẠI LƯỢNG ĐÁNH ĐỔI ĐƯỢC VỚI THỜI GIAN TÍNH TOÁN, chứ không phải hằng số của thuật toán.**

**Xét theo thời gian đồng hồ, trên cùng ngân sách bước:** SAC **139 phút** vs PPO **48 phút** (gần gấp 3).

### Độ ổn định

| Môi trường | Mượt nhất → dao động nhất |
|---|---|
| **Cross The Road** | MA-POCA (0,017) < MAPPO (0,024) < SAC (0,025) << **PPO (0,116)** |
| **Capture The Flag** | MAPPO (0,002) … PPO (0,006) << **SAC (0,210)** — lớn hơn **hai bậc độ lớn** |
| **Football Table** | PPO (0,276) < SAC (0,432) < MAPPO (0,486) < **MA-POCA (0,590)** |

**Giải thích:** tính mượt của nhóm họ PPO ở hai môi trường rời rạc đến từ **cơ chế cắt tỉ lệ (clipping)** vốn giới hạn độ lớn mỗi bước cập nhật.

⚠️ **Nhưng quy luật đó KHÔNG kéo sang Football Table** — ở đó MA-POCA mới là kẻ dao động mạnh nhất. **Lý do: trong self-play, độ lệch chuẩn phản ánh cả biến động của ĐỐI THỦ chứ không riêng của chính sách đang học** → ở môi trường đối kháng chỉ số này **mất gần hết ý nghĩa so sánh**.

## 7.6. Phân tích ưu nhược từng thuật toán (rút từ thực nghiệm)

| Thuật toán | Nhận xét |
|---|---|
| **MAPPO** | ⭐ **Thuật toán DUY NHẤT góp mặt ở nhóm dẫn đầu CẢ BA môi trường** — hạng 1 ở Football Table và Capture The Flag, hạng 2 ở Cross The Road với khoảng cách không đáng kể so với SAC. **Kết quả này vượt xa phạm vi mà thiết kế của MAPPO nhắm tới.** Đồ án chưa giải thích được cơ chế, và với 1 seed/ô cũng chưa loại được yếu tố ngẫu nhiên |
| **PPO** | **Lựa chọn mặc định hợp lý** — chẳng dẫn đầu ở đâu, nhưng cũng không thất bại ở đâu. **Nhược điểm lộ ra trên Cross The Road**: entropy tăng ngược + độ dài lượt chơi bùng nổ ở nửa sau → **có thể rời khỏi vùng nghiệm tốt rồi không tự quay lại được** |
| **SAC** | **Thuật toán PHÂN HÓA MẠNH NHẤT.** Dẫn đầu CTR (0,846), hạng 3 Football, **sụp đổ hoàn toàn ở CTF** (0,183). **Biên độ giữa thành công và thất bại của riêng SAC còn lớn hơn mọi chênh lệch giữa các thuật toán trong cùng một môi trường** → khi chưa thử nghiệm trên bài toán cụ thể, đây là **lựa chọn RỦI RO NHẤT** |
| **MA-POCA** | **Kết quả TRÁI HẲN kỳ vọng.** Là thuật toán thiết kế riêng cho gán công lao nhóm, nó chỉ **ngang bằng** MAPPO và PPO ở môi trường hợp tác, lại **xếp áp chót** ở Cross The Road và **cuối cùng trong nhóm self-play** ở Football Table. **Cơ chế attention không tạo nổi lợi thế nào đo được trong ba môi trường của đồ án** |
| **DQN** | **Vừa yếu nhất xét toàn cục vừa khó triển khai nhất.** Xếp cuối CTR cách biệt lớn, chen được nhóm giữa ở CTF, còn Football Table thì cần bản dựng riêng mà vẫn không ghép nổi với self-play. **Ưu điểm duy nhất là đường cong ổn định — nhưng sự ổn định đó đến từ việc chính sách ÍT THAY ĐỔI, chứ không từ chất lượng của chính sách** |

## 7.7. Hàm ý thực tiễn cho phát triển game

> **Quan trọng nhất: chọn thuật toán nên dựa trên CƠ CHẾ GAME cụ thể, chứ đừng đi tìm một thuật toán "tốt nhất" chung chung.**

| Loại game | Khuyến nghị |
|---|---|
| **Đối kháng** (thể thao, đấu trường, PvP/PvE) | **Họ PPO + self-play.** Tự sinh ra đối thủ máy có trình độ tăng dần một cách tự nhiên → trải nghiệm vừa thử thách vừa công bằng |
| **Điều hướng / né vật cản / giải đố đơn tuyến** | **SAC đạt mức năng lực cao nhất — nhưng KÈM HAI ĐIỀU KIỆN:** (1) hiệu quả sử dụng dữ liệu phụ thuộc vào tần suất cập nhật mạng; (2) thời gian chạy thực tế **cao gấp gần 3 lần PPO** trên cùng ngân sách bước. Nhóm ít tài nguyên nên cân nhắc kỹ trước khi chọn SAC chỉ vì lý do "ít mẫu hơn" |
| **Hợp tác nhiều nhân vật máy** | **PPO thường bám sát cả MAPPO lẫn MA-POCA** → công sức tích hợp một thuật toán đa tác nhân chuyên biệt **chưa chắc được đền đáp**. Khuyến nghị thực dụng: **khởi đầu bằng PPO để có mốc so sánh, rồi mới tính tới MAPPO nếu mốc đó chưa đủ** |
| ❌ **Điều cần TRÁNH rõ ràng nhất** | **Đừng dùng thuật toán off-policy như SAC cho bài toán hợp tác có phần thưởng nhóm thưa kèm chương trình học nhiều bài** — đó là **cấu hình DUY NHẤT trong đồ án dẫn tới thất bại hoàn toàn** |

---

# PHẦN 8 — Ứng dụng trình diễn & đóng gói UPM

## 8.1. Vì sao cần ứng dụng trình diễn?

> **Biểu đồ và bảng số liệu chẳng nói được gì trực tiếp về chất lượng hành vi của tác nhân trong game.** Rất nhiều lỗi đặc tả **chỉ chịu lộ ra khi nhìn hành vi thật.**

**Giá trị của ứng dụng không nằm ở phần game, mà ở chỗ nó là CÔNG CỤ SOI LỖI ĐẶC TẢ** — và cũng là cách khép kín quãng đường từ một file YAML tới một hành vi mà người chơi cảm nhận được bằng tay.

## 8.2. Bốn nhóm yêu cầu chức năng

1. **Lựa chọn nội dung chơi** — menu chọn 1 trong 3 môi trường + 1 trong 3 chế độ chơi
2. **Ba cách phân vai người–máy:**
   - *Người chơi* — tự điều khiển bằng bàn phím, **nếm thử độ khó của nhiệm vụ mà agent phải học**
   - *Agent tự chơi* — giao toàn bộ cho mô hình đã huấn luyện, **quan sát và đánh giá trực quan chất lượng chính sách**
   - *Chơi với Agent* — người và máy cùng có mặt, đóng vai đồng đội hay đối thủ tùy môi trường
3. **Lựa chọn mô hình** — chọn được mô hình cụ thể (PPO/SAC/MA-POCA/MAPPO/DQN) → **biến ứng dụng thành công cụ so sánh trực quan**
4. **Tra cứu kết quả huấn luyện ngay trong ứng dụng** — 2 tab: *THÔNG SỐ* và *SO SÁNH*, phủ đúng phạm vi 15 lần chạy

**Ràng buộc kỹ thuật quan trọng:** ⚠️ **Ứng dụng không được phá cấu hình huấn luyện hiện có của các scene.** Mọi thay đổi phục vụ chế độ chơi chỉ được xảy ra **tại thời gian chạy**, khi người dùng đi vào từ menu. Mở scene trực tiếp trong Editor để huấn luyện thì mọi thứ phải y nguyên.

## 8.3. Kiến trúc hệ thống

```
[Scene MainMenu]  ──ghi lựa chọn──→  [GameModeSelection]  (static: môi trường, chế độ, mô hình)
    MainMenuUI                              │
                                            ▼
[GameModeApplier] ◀──thông báo──── [Nạp scene môi trường]
 (sự kiện sceneLoaded)                      │
    │                                       ▼
    ├──→ [Cấu hình tác nhân]         [InGameHUD + điều khiển người chơi]
    │     Heuristic / Inference
    │     + mô hình ONNX
```

| Thành phần | Vai trò |
|---|---|
| `GameModeSelection` | Lớp **tĩnh** lưu lựa chọn, tồn tại xuyên suốt giữa các scene |
| `ModelRegistry` | Liệt kê và nạp mô hình ONNX từ `Resources/AgentModels` tại thời gian chạy |
| `MainMenuUI` | Dựng toàn bộ giao diện menu 3 tab **bằng mã lệnh** (không dùng prefab UI) |
| `UIBuilder` | Thư viện dựng thành phần giao diện dùng chung |
| `Preview3D` | Dựng bản sao **"chỉ có hình khối"** của prefab môi trường, render bằng camera riêng ra `RenderTexture` |
| `TrainingDataStore` | Nạp `training_data.json` chứa đường cong + thống kê thật đã xuất từ TensorBoard |
| `UILineChart` | Biểu đồ đường **tự vẽ bằng mesh** trên uGUI |
| `GameModeApplier` | ⭐ Lắng nghe `sceneLoaded`; chọn số khu vực giữ lại và cấu hình lại các agent |
| `InGameHUD` | Giao diện phủ: nút về menu, thông tin chế độ, dòng hướng dẫn phím |
| `*HumanInput` | `CrossRoadHumanInput`, `PuzzleHumanInput`, `FootballHumanInput` |

**⭐ Mấu chốt của thiết kế — cách tiếp cận dựa trên sự kiện:**
`GameModeApplier` đăng ký với `sceneLoaded` ngay từ lúc ứng dụng khởi động (thuộc tính `[RuntimeInitializeOnLoadMethod]`). Scene nạp xong, nó kiểm tra người dùng có đi vào từ menu hay không:
- **Có** → tìm agent trong scene và cấu hình lại theo chế độ đã chọn
- **Không** (ai đó mở scene trực tiếp để huấn luyện) → **đứng ngoài, scene giữ nguyên cấu hình gốc**

→ **Thêm đầy đủ chức năng chơi game mà không phải sửa bất kỳ scene môi trường nào.**

**Chuyển đổi loại hành vi:**
- Người điều khiển → `BehaviorType.HeuristicOnly` (hành động lấy từ hàm `Heuristic`)
- Agent máy → `BehaviorType.InferenceOnly` + nạp mô hình ONNX

```csharp
ModelAsset[] models = Resources.LoadAll<ModelAsset>("AgentModels/" + envName);
agent.SetModel(behaviorName, selectedModel);
behaviorParameters.BehaviorType = BehaviorType.InferenceOnly;
```

**Mọi thứ chạy cục bộ trên máy người chơi với chi phí tính toán không đáng kể, chẳng cần tiến trình Python nào như hồi huấn luyện.**

## 8.4. Đường ống dữ liệu TensorBoard → game

`export_training_data.py` đọc file `tfevents` bằng `EventAccumulator`, chạy **4 bước xử lý**:

1. **Gộp** chuỗi `Environment/Cumulative Reward` của mọi file nhật ký cùng lần chạy, sắp theo số bước
2. **Làm mượt** bằng trung bình trượt
3. **Rút gọn** xuống tối đa **120 điểm cách đều** (giữ file đủ nhỏ để nạp trong game)
4. **Tính thống kê tóm tắt** — reward cuối, reward tốt nhất, TB 10% cuối, bước hội tụ ước lượng, tổng số bước

**Cùng lượt chạy đó, kịch bản làm thêm 2 việc để dữ liệu và mô hình KHÔNG BAO GIỜ LỆCH PHA:**
- Sao chép file ONNX cuối cùng của từng lần chạy vào thư mục tài nguyên dưới **đúng tên mã lần chạy**
- **Xác định không gian hành động** của từng mô hình bằng cách đọc thẳng tên tensor đầu ra trong file ONNX, ghi vào JSON

> **→ Một lệnh duy nhất sau mỗi đợt huấn luyện là đủ để biểu đồ, bảng thống kê VÀ danh mục mô hình cùng được cập nhật.** Phần trình diễn và phần số liệu của Chương 4 **không thể lệch nhau**.

**Bảng màu thống nhất:** PPO xanh dương, SAC xanh lá, MA-POCA cam, MAPPO tím, DQN đỏ — **trùng với bảng màu các đồ thị ở Chương 4** để người xem đối chiếu giữa hai nơi mà khỏi đọc lại chú giải.

⚠️ **Một khác biệt nhỏ cần lưu ý:** đường cong trong ứng dụng **được làm mượt** bằng trung bình trượt cho dễ đọc trên màn hình nhỏ → con số ở đó **lệch chút ít** so với Chương 4 (vốn dùng chuỗi thô).

## 8.5. Ánh xạ ba chế độ chơi vào ba môi trường

| Môi trường | Người chơi | Agent tự chơi | Chơi với Agent |
|---|---|---|---|
| **Cross The Road** | Người điều khiển nhân vật | Mô hình điều khiển nhân vật | **Người và agent đua song song ở 2 khu vực liền kề** |
| **Capture The Flag** | 2 người chơi trên cùng bàn phím | 2 agent cùng dùng 1 mô hình | **Người phối hợp cùng agent đồng đội** |
| **Football Table** | Người đấu với bot luật đơn giản | **Mô hình đấu mô hình** (phải cùng loại hành động)* | Người đấu mô hình |

*Hai ô mô hình phải cùng liên tục hoặc cùng rời rạc, vì mỗi loại chạy trên một bản scene riêng.

**Chi tiết đáng chú ý:**
- Cross The Road chế độ *Người chơi*: **ràng buộc người chơi vào ĐÚNG 4 hành động rời rạc mà agent được phép dùng** — chủ ý, để người dùng đánh giá đúng độ khó bài toán. Được điều khiển tự do hơn agent thì rất dễ đi tới kết luận sai lệch
- Football Table chế độ *Chơi với Agent*: 8 kênh liên tục → sơ đồ phím theo nguyên tắc **"một thanh tại một thời điểm"** (Q/E hoặc 1–4 chọn thanh, W/S trượt, A/D xoay). Giá trị hành động **được nhân với dấu của đội**, y như cách chuẩn hóa hệ tọa độ khi huấn luyện → cùng một sơ đồ phím dùng được cho cả hai phía sân

## 8.6. 15 mô hình ONNX đóng gói sẵn

| Môi trường | File mô hình | Thuật toán | Bước |
|---|---|---|---|
| **Cross The Road** | `ctr01` / `CrossTheRoad_SAC_01` / `ctr_poca_v1` / `ctr_mappo_v1` / `ctr_dqn_v1` | PPO / SAC / MA-POCA / MAPPO / DQN | 2,00M |
| **Capture The Flag** | `ctf_ppo_v1` / `ctf_sac_v1` / `ctf_poca_v2` / `ctf_mappo_v2` / `ctf_dqn_v1` | PPO / SAC / MA-POCA / MAPPO / DQN | 1,70M (SAC 1,64M) |
| **Football Table** | `FB01` / `Football_SAC_01` / `Football_POCA_01` / `Football_MAPPO_01` / `football_dqn_v1` | 4 thuật toán self-play + DQN rời rạc | 1,60M |

**Tên file = mã lần chạy = nhãn hiển thị trong menu** → mọi con số trong ứng dụng **truy vết ngược được** về đúng thư mục kết quả và đúng biểu đồ ở Chương 4.

### ⚠️ Vấn đề kỹ thuật: không gian hành động cố định từ lúc nạp scene

ML-Agents dựng bộ truyền động từ `BehaviorParameters` ngay trong pha `OnEnable` — **trước khi sự kiện nạp scene kịp báo về cho ứng dụng**. Vì thế **không thể đổi KIỂU hành động tại thời gian chạy** như cách đổi mô hình.

**Giải pháp:** giữ song song **hai bản scene Football** — bản liên tục (4 thuật toán) và bản rời rạc `FootballDiscrete` (sinh tự động từ bản gốc bằng kịch bản Editor). Menu nạp bản phù hợp với mô hình người dùng chọn. → **Đổi scene thay vì đổi đặc tả hành động**, không phải đụng tới scene gốc dùng cho huấn luyện.

Lớp agent Football vốn đã chấp nhận cả hai kiểu và tự quy đổi 3 mức {0,1,2} → {−1,0,+1}.

## 8.7. Bảy vấn đề kỹ thuật đáng nhớ (hay bị hỏi)

| # | Vấn đề | Giải pháp |
|---|---|---|
| **1** | **Độ trễ điều khiển do Decision Period** — agent chỉ ra quyết định sau mỗi vài bước vật lý → nhân vật phản hồi phím rất chậm | Hạ chu kỳ quyết định xuống **1** cho agent do người điều khiển; agent máy **giữ nguyên chu kỳ gốc** để tái hiện đúng điều kiện huấn luyện |
| **2** | **Mất phím bấm giữa hai lần quyết định** — `Heuristic` đọc sự kiện nhấn phím tức thời | Thêm **thành phần đệm đầu vào**: phím ghi nhận trong `Update` (mỗi khung hình), giữ lại tới khi `Heuristic` tiêu thụ |
| **3** | **Xung đột thứ tự khởi tạo Football** — `Agent` gọi `OnEpisodeBegin` ngay trong `OnEnable`, trước khi bộ khởi tạo scene kịp xong → lỗi tham chiếu rỗng ngắt quãng | Làm `Team` và `Ball` **tự khởi tạo an toàn**: thao tác đặt lại tự gọi khởi tạo nếu phát hiện chưa khởi tạo; khởi tạo lặp chặn bằng cờ |
| **4** | ⭐ **Nhiều khu vực huấn luyện trong một scene** — ứng dụng ban đầu viết cho scene 1 khu vực, xác định khu vực bằng **đối tượng gốc** của agent. Sau khi nhân bản, mọi bản sao **chung một đối tượng gốc** → cách xác định sụp đổ. Football lãnh hậu quả nặng nhất: quy tắc *"đội Đỏ là agent đầu tiên không phải đội Xanh"* chọn trúng một agent Xanh của **bàn khác** → trận đấu chẳng bao giờ hình thành, 14 agent kia vẫn chạy ở cấu hình huấn luyện | **Xác định khu vực theo cấu trúc cây**: đi ngược lên cha cho tới ngay dưới đối tượng chứa chung → cả bản gốc lẫn bản sao đều trả về đúng khu vực của mình |
| **5** | **Đóng khung camera cho vùng chơi dài và dẹt** — cách ban đầu (đặt camera cách tâm một khoảng tỉ lệ với bán kính hình cầu bao) đẩy camera ra quá xa với bàn bi lắc | **Chiếu 8 đỉnh hộp bao lên 3 trục camera**: máy quay trực giao → tính kích thước vừa khít; máy quay phối cảnh → tính khoảng cách nhỏ nhất. Dùng chung cho cả 3 môi trường mà không cần tham số riêng. *(Phép đóng khung phải hoãn tới cuối khung hình đầu tiên — lúc scene vừa nạp xong, xe chưa về vị trí xuất phát nên hộp bao tính sớm sẽ sai)* |
| **6** | **Agent thừa ở chế độ Người chơi** — Football đội Đỏ do bot luật cầm, nhưng agent ML-Agents vẫn trong scene và có thể sinh hành động nhiễu | Vô hiệu hóa bộ yêu cầu quyết định + **đặt giới hạn bước của tập về 0** |
| **7** | ⚠️ **Phạt thời gian chia cho KHÔNG** — trớ trêu là chính việc đặt giới hạn bước về 0 ở trên **lại làm lộ một lỗi tiềm ẩn**: phạt thời gian tính bằng **nghịch đảo của giới hạn bước** → giới hạn = 0 thì reward hóa **vô cực** và ML-Agents ném ngoại lệ mỗi bước | Chỉ áp dụng phạt thời gian khi giới hạn bước > 0. ⭐ **Ví dụ điển hình cho chuyện chuyển một môi trường từ chế độ huấn luyện sang chế độ chơi có thể đánh thức những nhánh mã CHƯA TỪNG CHẠY trong suốt quá trình huấn luyện** |

## 8.8. Đóng gói thành gói UPM `com.vanhuyen.rl-game-envs`

### Cấu trúc gói

| Thư mục | Nội dung |
|---|---|
| `Runtime/` | **36 lớp điều khiển** của 3 môi trường (agent, quan sát, hàm phần thưởng, sinh vật cản, trọng tài) + giao diện `IManualActionSource`. **Một assembly riêng** |
| `Editor/` | Trình hướng dẫn cài đặt + **4 công cụ**: nhân khu vực huấn luyện, build headless, sinh bản scene hành động rời rạc, cài cấu hình huấn luyện |
| `Configs/` | **15 file YAML** cho 5 thuật toán × 3 môi trường |
| `Samples~/` | 4 mẫu import được: 3 môi trường (scene, prefab, vật liệu, thiết lập vật lý) + bộ cấu hình huấn luyện |
| `Documentation~/` | Tài liệu, `README`, `CHANGELOG`, `LICENSE` |

> ⭐ **Điểm đáng nói không phải danh sách thư mục, mà là RANH GIỚI giữa chúng.** Toàn bộ mã điều khiển biên dịch thành **một assembly riêng**, tách khỏi `Assembly-CSharp`. **Chính trình biên dịch canh giữ tính độc lập của gói** — một lớp môi trường lỡ tham chiếu tới mã của ứng dụng trình diễn là **dự án hỏng biên dịch ngay**, chứ không phải đợi tới khi ai đó cài gói mới lòi ra.

### ⭐ Gỡ phụ thuộc ngược — bài học thiết kế

**Vấn đề:** hàm `Heuristic` của cả 3 agent từng gọi thẳng `GetComponent` tới các lớp cụ thể của ứng dụng trình diễn. **Quan hệ đó ngược với thứ bậc đúng** — môi trường là tầng dưới, lẽ ra chẳng biết gì về ứng dụng nhúng nó. Trong một dự án đơn lẻ thì vô hại, nhưng tách gói ra là **lỗi biên dịch thật sự**.

**Giải pháp — đảo chiều phụ thuộc bằng một giao diện đặt trong chính gói:**

```csharp
public interface IManualActionSource
{
    void WriteActions(in ActionBuffers actionsOut);
}
```

Hàm `Heuristic` giờ chỉ hỏi đúng một câu: *"trên GameObject này có thành phần nào hiện thực giao diện đó không?"* — có thì giao quyền, không thì quay về sơ đồ phím mặc định.

→ **Người dùng gói muốn thêm cách điều khiển mới (gamepad, kịch bản kiểm thử tự động, hay chính một mô hình ngôn ngữ lớn) chỉ việc viết một `MonoBehaviour` rồi gắn vào — khỏi động tới dòng nào trong mã môi trường.**

### Trình hướng dẫn cài đặt 7 bước

> **Rào cản lớn nhất với người mới không phải thiếu tài liệu, mà là KHÔNG BIẾT MÌNH ĐANG ĐỨNG Ở ĐÂU trong tài liệu đó.**

**Mấu chốt: mỗi bước TỰ KIỂM TRA TRẠNG THÁI HIỆN TẠI** rồi hiện dấu tích hoặc nút hành động, chứ không chỉ liệt kê việc cần làm.

1. Kiểm tra gói phụ thuộc
2. Import môi trường từ mục Samples
3. Kiểm tra các gói art bên thứ ba
4. Chép cấu hình huấn luyện ra `config/`
5. Nhân khu vực huấn luyện
6. Build môi trường headless
7. Lệnh mẫu chạy huấn luyện (kèm nút chép sang clipboard)

**Ba bước giữa gọi lại đúng những công cụ mà đồ án đã dùng cho phần thực nghiệm của chính mình** → người dùng gói đi theo **một quy trình đã được kiểm chứng**, chứ không phải quy trình viết riêng cho tài liệu.

**Về bước kiểm tra art bên thứ ba — ràng buộc PHÁP LÝ:** Cross The Road hiển thị bằng vài gói art miễn phí trên Unity Asset Store. Giấy phép Asset Store cho phép dùng trong dự án của người đã tải, nhưng **cấm đóng gói lại để phát hành** — kể cả khi gói art đó miễn phí. Gói của đồ án vì vậy **không kèm chúng**; trình hướng dẫn quét dự án, nêu đích danh gói thiếu, mở thẳng trang tải, và nói rõ **thiếu art thì môi trường vẫn huấn luyện bình thường — chỉ là xe với nhân vật không có hình**.

**Mã nguồn và cấu hình do đồ án viết: giấy phép MIT.**

### ⭐ Dự án tự dùng chính gói của mình

Gói nằm ở dạng **nhúng** trong `Packages/`, và ứng dụng trình diễn tiêu thụ nó **đúng theo cách một dự án bên ngoài sẽ làm**: qua ranh giới assembly, qua giao diện công khai, **không đường tắt nào**.

> **→ Toàn bộ phần thực nghiệm lẫn phần trình diễn của đồ án trở thành MỘT PHÉP KIỂM THỬ THƯỜNG TRỰC cho gói** — thay vì phải đặt niềm tin vào một bản đóng gói chỉ được thử đúng một lần lúc phát hành.

## 8.9. Kiểm thử và hạn chế của ứng dụng

**13 luồng kiểm thử, tất cả đều Đạt** — mỗi luồng xác nhận 4 điểm: (1) scene nạp đúng, agent được cấu hình đúng vai trò; (2) ONNX nạp thành công và agent hành xử đúng kỳ vọng; (3) giao diện phủ hiện đúng, nút về menu chạy được; (4) console Unity sạch lỗi.

Đáng chú ý trong danh sách: *"Mở scene trực tiếp (không qua menu) → cấu hình huấn luyện gốc được giữ nguyên: **Đạt**"* và *"Gói môi trường: assembly riêng biên dịch được, 3 scene không đứt tham chiếu script: **Đạt**"*.

**Hiệu năng:** suy luận mạng nơ-ron cho các agent đồng thời + giao diện **không làm tốc độ khung hình sụt đáng kể** → khẳng định việc nhúng thẳng mô hình đã huấn luyện vào sản phẩm game là **khả thi**.

### Hai hạn chế đã biết

| Hạn chế | Chi tiết |
|---|---|
| **Dung lượng** | Riêng **5 mô hình Capture The Flag đã chiếm ~325 MB** — gấp nhiều lần tổng dung lượng 2 môi trường còn lại. ⚠️ **Thủ phạm không phải số lượng mô hình mà là KIẾN TRÚC MẠNG:** quan sát tín hiệu mục tiêu của môi trường này khiến ML-Agents dựng bộ mã hóa theo kiểu **hypernetwork** (một nhánh phụ sinh trọng số cho lớp ẩn chính), đẩy số tham số của một chính sách nhỏ lên **gần 17 triệu**. → **Muốn giảm dung lượng thì phải huấn luyện lại CTF với kiểu điều kiện hóa mục tiêu khác, chứ bớt mô hình đi không giải quyết được gì** |
| **Dữ liệu tĩnh** | Hai tab số liệu phản ánh nội dung `training_data.json` **tại thời điểm xuất** → sau mỗi đợt huấn luyện mới phải chạy lại kịch bản. **Bù lại, cùng lệnh đó cũng cập nhật luôn danh mục mô hình, nên hai phần không thể lệch nhau** |

---

# PHẦN 9 — Kết luận, đóng góp, hạn chế

## 9.1. Kết quả đạt được — đối chiếu với 3 tiêu chí nghiệm thu

| Tiêu chí | Bằng chứng |
|---|---|
| **Học được** ✓ | Ở cả 3 môi trường đều có **ít nhất 4/5 thuật toán tiến bộ rõ rệt** so với lúc khởi tạo |
| **Phân biệt được** | **Cross The Road ✓**: reward cuối trải từ **0,846** (SAC) xuống **0,336** (DQN). **Capture The Flag ✓**: 4 thuật toán trong dải 0,800–0,840 trong khi SAC sụp đổ ở 0,183. **Thứ hạng ở cả hai nơi đều GIẢI THÍCH ĐƯỢC bằng cơ chế bài toán.** ⚠️ **Football Table ✗** |
| **Không có lối tắt** ✓ | **Không lần chạy nào đạt reward sát trần mà lại không giải được nhiệm vụ** khi quan sát trực tiếp trong ứng dụng trình diễn. Riêng CTF còn có lập luận định lượng loại trừ lối tắt cá nhân (§5.2.4) |

### ⚠️ Giới hạn của Football Table — thừa nhận thẳng thắn

Cả 4 thuật toán ghép được với self-play đều tăng ELO **từ 36 tới 64 điểm** → cơ chế tự chơi **hoạt động đúng**. Nhưng **biên độ ấy quá hẹp để môi trường phân định được các thuật toán với nhau**.

> **Ở cấu hình hiện tại, Football Table chỉ đạt 2/3 tiêu chí.** Muốn dùng nó làm thước đo so sánh thì cần **ngân sách bước lớn hơn**, hoặc **một đối thủ mốc cố định thay cho tự chơi thuần túy**.

### Quan sát xuyên suốt ủng hộ luận điểm trung tâm

> **Chênh lệch của CÙNG MỘT thuật toán giữa HAI MÔI TRƯỜNG luôn lớn hơn chênh lệch giữa CÁC THUẬT TOÁN trong CÙNG MỘT môi trường.**
>
> Khoảng cách giữa thành công của SAC trên Cross The Road (0,846) và sự sụp đổ của chính nó trên Capture The Flag (0,183) **lớn hơn mọi khoảng cách nội bộ**.
>
> **→ Đặc tính bài toán — thứ do THIẾT KẾ MÔI TRƯỜNG quyết định — chi phối kết quả mạnh hơn LỰA CHỌN THUẬT TOÁN. Và đó chính là lý do khâu xây dựng môi trường đáng được đầu tư nhiều hơn mức thường thấy.**

## 9.2. Bốn đóng góp (xếp theo mức hữu ích)

### ① Bộ môi trường đã kiểm chứng ⭐ (quan trọng nhất)

3 môi trường 3D phủ 3 dạng bài toán RL phổ biến, đóng thành gói UPM cài được vào dự án bất kỳ, kèm **15 cấu hình huấn luyện đã chạy thật**, bộ công cụ Editor và trình hướng dẫn 7 bước biết tự kiểm tra trạng thái.

> **Điều khiến nó khác việc chỉ công bố mã nguồn: ba môi trường này ĐÃ QUA KIỂM CHỨNG.** Mỗi môi trường đã chịu 5 thuật toán khác hẳn nhau về nguyên lý → **người dùng lại biết trước rằng nó học được, nó phân biệt được, và nó không có lối tắt — những điều mà một môi trường mới dựng chẳng bao giờ bảo đảm nổi.**

### ② Tri thức thiết kế môi trường ⭐

Ghi lại đầy đủ quá trình đặc tả cho 3 dạng bài toán, **gồm cả những phương án thất bại và DẤU HIỆU NHẬN RA CHÚNG**:
- Một hàm phần thưởng **trừng phạt chính hành vi đích** (CTF v1)
- Một agent **thiếu quan sát về đồng đội** nên không định được thời điểm phối hợp
- Một khoản **phạt thời gian chia cho không** khi giới hạn bước bằng 0

Đi cùng là các **quyết định vận hành ảnh hưởng lớn nhưng ít được bàn**: nhân khu vực huấn luyện để tăng thông lượng, dựng biến thể không gian hành động rời rạc cho thuật toán value-based.

Và **hai con đường đưa một thuật toán không có sẵn vào Unity**: gói trainer mở rộng (MAPPO + DQN) và lớp bọc môi trường qua `mlagents_envs` để nối Stable-Baselines3.

**Trường hợp điển hình — Capture The Flag:**
> Đặc tả ban đầu **trừng phạt đúng cái trạng thái phối hợp mà nhiệm vụ đòi hỏi** — hai agent đứng tách nhau ở hai phía cửa — nên agent mắc kẹt ở đáy phần thưởng nhóm **bất kể chạy thuật toán nào**. **Lỗi đó không hiện ra thành lỗi chương trình, nó chỉ hiện thành một đường cong phẳng, và chỉ lộ diện khi ta ngồi xem hành vi thật.**
>
> Bài học — **phải kiểm tra xem hàm phần thưởng có vô tình phạt chính hành vi đích hay không** — áp dụng được cho **bất kỳ môi trường hợp tác nào**.

### ③ Kết quả so sánh 5 thuật toán (sản phẩm phụ nhưng tham khảo được)

**Đáng chú ý nhất là một KẾT QUẢ PHỦ ĐỊNH:**
> Trên bài toán hợp tác có tác nhân đồng nhất, **PPO thường bám sát cả MAPPO lẫn MA-POCA trong dải chênh lệch chưa tới 1%** → **chi phí tích hợp một thuật toán đa tác nhân chuyên biệt chưa chắc được đền đáp.**

Đi kèm nó là **một kết quả gây ngạc nhiên theo chiều ngược lại**: MAPPO vượt PPO một khoảng lớn **trên chính môi trường đơn tác nhân**, nơi lý thuyết bảo rằng critic tập trung của nó lẽ ra vô hiệu.

### ④ Ứng dụng trình diễn

3 chế độ chơi, cơ chế chọn mô hình cho phép đặt cạnh nhau cả 15 chính sách, 2 tab số liệu nhúng thẳng trong game.

> **Giá trị của nó không nằm ở phần game, mà ở chỗ nó là CÔNG CỤ SOI LỖI ĐẶC TẢ.** Quan sát hành vi thật là **cách duy nhất phát hiện những sai sót mà đường cong phần thưởng giấu đi** — và cũng là cách khép kín quãng đường từ một file YAML tới một hành vi mà người chơi cảm nhận được bằng tay. **Chính bảng xếp hạng ở Chương 4 có thể kiểm chứng lại bằng mắt**, bằng cách cho hai mô hình khác thuật toán chạy trên cùng một nhiệm vụ.

## 9.3. ⚠️ Bốn hạn chế (thuộc lòng — hội đồng chắc chắn hỏi)

### ① Chỉ một seed cho mỗi tổ hợp — hạn chế NẶNG NHẤT

> Mọi chênh lệch báo cáo ở Chương 4 **chưa tách được phần do bản chất thuật toán khỏi phần do may rủi của một lần khởi tạo.**
>
> - **Những khoảng cách LỚN** (DQN xếp cuối Cross The Road, SAC sụp đổ ở Capture The Flag) **nhiều khả năng vẫn đứng vững**
> - **Các thứ hạng SÁT NHAU thì ĐỪNG đọc như một kết luận thống kê**
>
> Đây là **hệ quả của quỹ thời gian tính toán chứ không phải của một lựa chọn phương pháp luận** — và *"nếu chỉ được sửa đúng một điều trong đồ án này thì tôi sẽ sửa điều đó."*

### ② Độ phân giải của phép đo

- Football Table: 4 thuật toán self-play trong dải ELO **1237–1260**
- Capture The Flag: 4 thuật toán dẫn đầu trong dải reward **0,800–0,840**

Cả hai khoảng cách **nhỏ hơn dao động của chính các đường cong** → ở cấu hình hiện tại **hai môi trường này không phân biệt nổi các thuật toán trong nhóm dẫn đầu**. **Chỉ Cross The Road cho phổ đủ rộng.**

> ⭐ **Câu quan trọng: "Muốn hai môi trường kia nói được nhiều hơn thì phải làm chúng KHÓ LÊN, chứ không phải CHẠY CHÚNG LÂU HƠN."**

### ③ Một ô của lưới nằm ngoài phép so sánh

**DQN trên Football Table chạy không có self-play** (ML-Agents báo lỗi khi ghép trainer off-policy với ghost trainer) → không có ELO, học trong điều kiện khác hẳn → mọi con số **chỉ đọc được như một tham chiếu rời**.

### ④ Hai hiện tượng chưa giải thích được — do chính số liệu của đồ án phơi ra

| Hiện tượng | Trạng thái |
|---|---|
| **MAPPO vượt PPO trên môi trường đơn tác nhân** — nơi hai thuật toán chỉ khác nhau ở phần critic tập trung, thứ lẽ ra vô hiệu khi nhóm có mỗi một thành viên | Cần thực nghiệm **tách riêng phần critic tập trung, chạy trên nhiều seed**. Với 1 seed/ô, **chưa loại được khả năng đây chỉ là dao động ngẫu nhiên** |
| **Kiểu thất bại của SAC trên Capture The Flag** — entropy sụp xuống gần 0 rồi **bật ngược lên đúng mức cực đại** và nằm đó tới cuối | Giả thuyết: **replay buffer lưu lẫn lộn kinh nghiệm của hai bài học** trong curriculum. Kiểm chứng bằng cách chạy lại với **bộ đệm tách riêng theo từng bài** |

## 9.4. Hướng phát triển (theo thứ tự ưu tiên)

**Ưu tiên 1 — Chạy lại 15 tổ hợp với nhiều seed.** *"Chừng nào chưa có phương sai giữa các lần chạy thì mọi so sánh trong đồ án vẫn treo lơ lửng."*

**Ưu tiên 2 — Làm Football Table và Capture The Flag KHÓ LÊN.** Với CTF, hướng cụ thể: **thêm bài trong curriculum hoặc buộc hai agent phối hợp chặt hơn**, chứ **không phải kéo dài thời lượng huấn luyện**.

**Ưu tiên 3 — Trả lời hai câu hỏi bỏ ngỏ:**
- Vì sao MAPPO vượt PPO trên môi trường đơn tác nhân? → thực nghiệm tách riêng critic tập trung, nhiều seed
- Cơ chế nào đứng sau kiểu thất bại của SAC? → chạy lại với bộ đệm tách theo bài học

**Ưu tiên 4 — Khảo sát ranh giới giữa chia sẻ tham số và attention:** bằng một môi trường hợp tác có **hai agent vai trò BẤT ĐỐI XỨNG**, hoặc **có agent rời nhóm giữa lượt chơi** — đúng tình huống mà MA-POCA sinh ra để giải.

**Tầm xa hơn:**
- Mở rộng bộ so sánh với **DreamerV3, QMIX** — việc bổ sung giờ đã **rẻ hơn nhiều nhờ cơ chế trainer mở rộng đã dựng sẵn**
- Nâng độ phức tạp 3 môi trường lên gần với game thương mại
- Ứng dụng trình diễn cần **bản chạy độc lập (WebGL/desktop)** + **bảng xếp hạng người chơi đấu agent** + **khảo sát trải nghiệm người dùng** → *cách duy nhất trả lời được câu hỏi mà không chỉ số huấn luyện nào chạm tới: **hành vi của agent có thực sự "tự nhiên" trong mắt người chơi hay không.***

---

# PHẦN 10 — Chuẩn bị bảo vệ

## 10.1. Nếu chỉ được nói 60 giây

> "Đề tài xuất phát từ một nhận xét: trong dự án RL cho game, thuật toán đã có sẵn trong thư viện, gọi PPO tốn đúng một dòng lệnh — thứ không ai đưa sẵn là **môi trường huấn luyện**. Em lấy chính khâu đó làm đối tượng nghiên cứu.
>
> Em dựng ba môi trường 3D trên Unity ML-Agents, phủ ba dạng bài toán khác nhau: đối kháng 1v1 hành động liên tục, hợp tác hai tác nhân với phần thưởng nhóm, và điều hướng đơn tác nhân phần thưởng thưa. Với mỗi môi trường, em ghi lại trọn vẹn quá trình thiết kế quan sát – hành động – phần thưởng, **kể cả những phương án đã thử rồi phải bỏ**.
>
> Để nghiệm thu, em chạy năm thuật toán trên cả ba môi trường — mười lăm lần chạy, cùng ngân sách bước. Năm thuật toán ở đây đóng vai **phép thử**, không phải đối tượng đánh giá: một môi trường đạt yêu cầu thì tác nhân phải học được, các hướng tiếp cận phải phân biệt được, và không được tồn tại lối tắt.
>
> Kết quả đáng chú ý nhất: **cùng một thuật toán, khoảng cách giữa hai môi trường luôn lớn hơn khoảng cách giữa các thuật toán trong cùng một môi trường**. SAC dẫn đầu Cross The Road với 0,846 rồi sụp xuống 0,183 ở Capture The Flag — trong khi cả nhóm dẫn đầu Capture The Flag chỉ cách nhau 0,04. Nói cách khác, đặc tính bài toán chi phối kết quả mạnh hơn lựa chọn thuật toán. Sản phẩm cuối là một gói Unity Package Manager gồm ba môi trường đã kiểm chứng, kèm mười lăm cấu hình huấn luyện và một ứng dụng trình diễn nạp trực tiếp mười lăm mô hình ONNX."

## 10.2. ⚠️ Điểm yếu cần phòng thủ — chuẩn bị sẵn câu trả lời

### Q1. "Sao chỉ chạy MỘT seed cho mỗi tổ hợp? Kết quả có đáng tin không?"

*Đây là câu hỏi khả năng cao nhất. Đừng né — nhận thẳng.*

> "Vâng, đây là hạn chế nặng nhất của đồ án và em đã ghi rõ ở Mục 6.3. Nó là hệ quả của quỹ thời gian tính toán chứ không phải lựa chọn phương pháp luận — mười lăm lần chạy trên một GPU tầm trung đã mất tổng cộng hơn hai mươi giờ.
>
> Nhưng có hai điều em muốn nói thêm. **Thứ nhất**, mục tiêu của đồ án không phải xếp hạng thuật toán mà là **kiểm chứng môi trường** — và cho mục tiêu đó, năm thuật toán khác nhau về nguyên lý trên cùng một môi trường có giá trị chẩn đoán tương đương với nhiều seed của cùng một thuật toán. **Thứ hai**, em đã phân định rõ đâu là kết luận vững và đâu là không: trong toàn bộ báo cáo em chỉ khẳng định **ba phân tách** — SAC thất bại trên Capture The Flag, DQN xếp cuối Cross The Road, và nhóm dẫn đầu tách khỏi nhóm sau ở Cross The Road. Ba cái đó có biên độ lớn hơn dao động đường cong rất nhiều. Còn những thứ hạng sát nhau, em ghi rõ trong báo cáo là **đừng đọc như kết luận thống kê**."

### Q2. "Football Table không phân biệt được thuật toán — vậy môi trường đó có thất bại không?"

> "Nó đạt hai trong ba tiêu chí nghiệm thu, và em ghi rõ điều đó ở Mục 6.1 chứ không giấu. Cả bốn thuật toán ghép được với self-play đều tăng ELO từ ba mươi sáu tới sáu mươi tư điểm so với phiên bản cũ của chính mình — tức môi trường **học được** và **không có lối tắt**. Cái nó thiếu là độ phân giải.
>
> Nguyên nhân nằm ở bản chất self-play: đối thủ mạnh lên cùng tốc độ với tác nhân, nên ELO gần như đứng yên dù chính sách vẫn đang cải thiện. **Cách sửa không phải chạy lâu hơn mà là thay đổi thiết kế đo** — dùng một đối thủ mốc cố định thay cho self-play thuần túy, hoặc tăng ngân sách bước đáng kể. Em đã ghi hướng đó ở phần Hướng phát triển.
>
> Còn với mục tiêu chính của đề tài — để lại một môi trường đối kháng dùng lại được — thì nó vẫn đạt: cơ chế self-play chạy đúng, ELO sinh ra được, và mô hình xuất ra chơi được thật trong ứng dụng trình diễn."

### Q3. "MAPPO vượt PPO trên môi trường đơn tác nhân — em giải thích thế nào?"

*Không được bịa. Đây là chỗ thể hiện tính trung thực khoa học.*

> "Em chưa giải thích được, và em ghi thẳng điều đó trong báo cáo. Về lý thuyết, hai thuật toán chỉ khác nhau ở phần phê bình tập trung — thứ lẽ ra vô hiệu khi nhóm chỉ có một thành viên. Thực đo lại cho MAPPO 0,835 so với PPO 0,690.
>
> Có hai khả năng em chưa loại trừ được. **Một**, đây là hiệu ứng thật, đến từ chi tiết cài đặt nào đó của lớp phê bình đa tác nhân mà em kế thừa từ MA-POCA. **Hai**, đây chỉ là dao động ngẫu nhiên giữa các hạt giống — mà với một seed thì em không có cách nào phân biệt. Em đã đề xuất cách kiểm chứng cụ thể ở phần Hướng phát triển: một thực nghiệm tách riêng phần phê bình tập trung, chạy trên nhiều hạt giống. Đây là điểm em sẽ kiểm chứng trước tiên nếu mở rộng đề tài."

### Q4. "Sao không dùng Stable-Baselines3 cho tiện, mà phải tự viết trainer mở rộng?"

> "Vì mục tiêu là kiểm chứng môi trường. **Chỉ khi cả năm thuật toán chạy trên cùng một đường ống thu thập quỹ đạo, cùng một cách ghi nhật ký, cùng một định dạng mô hình xuất ra, thì chênh lệch đo được giữa chúng mới nói lên đặc tính của môi trường** — chứ không phải nói lên sự khác biệt của hạ tầng đo.
>
> Nếu MAPPO chạy qua ML-Agents còn DQN chạy qua SB3, thì khi thấy DQN thua em sẽ không biết đó là do thuật toán hay do cách hai thư viện tính advantage, xử lý normalization, hoặc ghi TensorBoard khác nhau.
>
> Con đường qua Python Low-Level API em vẫn dựng xong và kiểm chứng — nó nằm ở Phụ lục B — nhưng với tư cách **một phương án đã sẵn sàng cho những trường hợp cần can thiệp sâu vào vòng lặp huấn luyện**, chứ không phải nguồn của bất kỳ số liệu nào trong bảng kết quả."

### Q5. "Hàm phần thưởng em đặt các con số dựa vào đâu? Có phải thử sai không?"

*Đây là câu hỏi mà đồ án trả lời tốt nhất — hãy dẫn dắt hội đồng về đây nếu có cơ hội.*

> "Không phải thử sai. Em đặt ra **bốn nguyên tắc thiết kế** ở Mục 3.1.4, và **mọi con số trong các bảng phần thưởng đều giải thích được bằng bốn nguyên tắc đó**. Em xin lấy hai ví dụ.
>
> **Football Table, tỉ lệ ghi bàn trên thủng lưới là năm trên một.** Con số này đến từ một bất đẳng thức. Với hàm phần thưởng đối xứng, tác nhân chỉ chịu tấn công khi xác suất thắng vượt ngưỡng (R₋ − 1)/(R₊ + R₋). Đặt R₊ = R₋ = 5 thì ngưỡng là 0,4 — tác nhân phải tự tin thắng bốn mươi phần trăm số pha bóng mới chịu dâng lên, mà giai đoạn đầu huấn luyện điều đó không bao giờ đúng, nên chính sách hội tụ về phòng ngự tuyệt đối. Đổi sang 5 và 1 thì ngưỡng tụt xuống đúng bằng không.
>
> **Cross The Road, phạt va chạm chỉ bằng một phần bốn mươi phần thưởng đích.** Cũng vậy: ngưỡng để tiến lên hơn đứng yên là R₋/(1 + R₋). Với 0,025 thì ngưỡng chỉ 2,4 phần trăm; nếu đặt phạt bằng 1 thì ngưỡng vọt lên năm mươi phần trăm và tác nhân sẽ học được rằng đứng yên là tối ưu — một cực tiểu cục bộ do chính hàm phần thưởng tạo ra."

### Q6. "Em có gặp lỗi gì trong quá trình làm không?"

*Đây là cơ hội, không phải bẫy. Kể về CTF v1.*

> "Có, và em dành hẳn một mục để thuật lại — Mục 3.4.6. Phiên bản phần thưởng đầu tiên của Capture The Flag thất bại hoàn toàn: huấn luyện với MA-POCA, phần thưởng nhóm **mắc kẹt ngay ở mức sàn — đúng bằng khoản phạt thời gian tích lũy trọn một lượt chơi — và không nhúc nhích suốt hàng triệu bước**.
>
> Chính con số đó là manh mối. Chỉ số đứng im ở đúng giá trị của riêng khoản phạt thời gian nói rằng không lượt chơi nào chạm đích, và cũng không hành vi trung gian nào được tưởng thưởng đủ để kéo chỉ số lên.
>
> Đào sâu thì lộ ra ba khuyết tật. Nghiêm trọng nhất: em có hai khoản **phạt nhóm cho trạng thái bất đối xứng** — một tác nhân ra ngoài còn tác nhân kia ở trong. Nhưng màn bàn giao **nhất thiết phải đi qua** đúng cấu hình đó. Nói cách khác, **hàm phần thưởng của em đang trừng phạt chính hành vi mà em muốn dạy**. Mọi con đường dẫn tới lời giải đều xuyên qua vùng bị phạt.
>
> Bài học em rút ra: **một hàm phần thưởng hỏng thường để lại dấu vết định lượng rất rõ ngay trên các chỉ số huấn luyện. Biết đọc những dấu vết ấy là công cụ chẩn đoán hiệu quả hơn hẳn việc dò hệ số mù quáng.** Và đó cũng là lý do em đưa nguyên tắc *bám theo lời giải mẫu* lên vị trí đầu tiên trong bốn nguyên tắc."

### Q7. "Ba môi trường của em có gì mới so với các benchmark có sẵn?"

> "Về hình thức trò chơi thì không có gì mới — bi lắc, câu đố hợp tác, băng qua đường đều là những mô-típ quen thuộc. **Cái mới nằm ở ba chỗ khác.**
>
> **Thứ nhất, chúng là môi trường ba chiều có mô phỏng vật lý thật và quan sát chỉ một phần qua cảm biến** — khác hẳn các benchmark hai chiều với vector trạng thái rút gọn, nơi mọi đặc tả đã có người làm sẵn. Chính vì ba chiều nên các bài toán thiết kế mới lộ ra hết.
>
> **Thứ hai, chúng ĐÃ ĐƯỢC KIỂM CHỨNG.** Mỗi môi trường đã chịu năm thuật toán khác hẳn nhau về nguyên lý, nên người dùng biết trước rằng nó học được, phân biệt được, không có lối tắt. Một môi trường mới dựng chẳng bao giờ bảo đảm nổi điều đó.
>
> **Thứ ba, chúng đi kèm quá trình thiết kế được ghi lại đầy đủ.** Cái em muốn để lại không phải ba cấu hình tình cờ chạy được, mà là **những nguyên tắc thiết kế dùng lại được** cho môi trường thứ tư, thứ năm mà người khác sẽ dựng."

### Q8. "SAC thất bại ở Capture The Flag — sao em không sửa để nó chạy được?"

> "Vì đó **không phải lỗi cần sửa, mà là một kết quả cần báo cáo**. Nhớ rằng vai trò của năm thuật toán ở đây là phép thử: một môi trường được kiểm chứng chắc chắn khi nó **phản ứng nhất quán và giải thích được** trước nhiều hướng tiếp cận độc lập.
>
> Việc SAC thất bại còn bốn thuật toán kia thành công chính là bằng chứng cho tiêu chí **phân biệt được** — và quan trọng hơn, nó **giải thích được bằng cơ chế bài toán**: bốn chỉ số độc lập cùng chỉ về một hướng. Entropy sụp xuống 0,013 rồi bật ngược lên đúng mức cực đại 1,946. Phần thưởng tò mò vẫn cao gấp hơn ba mươi lần nhóm còn lại. Độ dài lượt chơi nằm ở trần thời gian 4999 bước. Và phần thưởng thì dao động chứ không hội tụ. Chừng đó đủ để kết luận **SAC học được rồi đánh mất, lặp đi lặp lại** — chứ không phải nó học quá chậm.
>
> Nếu em tinh chỉnh riêng SAC cho môi trường này thì em sẽ mất đúng cái thông tin có giá trị nhất, và phép so sánh cũng không còn công bằng vì bốn thuật toán kia không được tinh chỉnh tương tự. **Còn giá trị thực tiễn của nó thì rất rõ ràng: đừng dùng thuật toán off-policy cho bài toán hợp tác có phần thưởng nhóm thưa kèm chương trình học nhiều bài.**"

### Q9. "Vì sao dùng tám khu vực huấn luyện song song? Có ảnh hưởng kết quả không?"

> "Để tăng lượng kinh nghiệm thu trên mỗi bước mô phỏng và giảm tương quan giữa các mẫu trong cùng một lô cập nhật — nhờ đó thời gian thực rút ngắn đáng kể.
>
> Có ảnh hưởng, và em ghi rõ điều đó trong báo cáo: **cùng một số bước môi trường ở cấu hình tám khu vực không tương đương với cùng số bước ở cấu hình một khu vực**. Đây là chi tiết phải nhớ khi đối chiếu với các công bố khác.
>
> Nhưng nó **không ảnh hưởng tới các so sánh trong nội bộ đồ án**, vì cả mười lăm lần chạy đều dùng chung cấu hình tám khu vực. Đồ án cũng không so sánh chéo giữa các môi trường, chỉ xếp hạng trong nội bộ từng môi trường."

### Q10. "Em nói không có lối tắt — chứng minh thế nào?"

> "Có hai lớp bằng chứng. **Lớp thứ nhất là định lượng**, cho Capture The Flag — môi trường có nguy cơ lối tắt cao nhất. Câu hỏi là: khoảng ân hạn một giây của cửa có cho phép một tác nhân tự mình vượt cổng không?
>
> Khoảng cách từ bàn đạp thứ nhất tới cổng là **mười chín đơn vị**. Vận tốc tối đa của tác nhân là **17,5 đơn vị trên giây**, tính từ thế cân bằng giữa lượng vận tốc cộng thêm 1,4 và hệ số cản 4 trên bước vật lý 0,02 giây. Cứ giả định rộng rãi rằng tác nhân đã chạy sẵn ở vận tốc tối đa, một giây nó vẫn chưa đi nổi mười chín đơn vị. Mà thực tế nó xuất phát từ trạng thái đứng yên trên bàn đạp, phải mất thời gian tăng tốc, nên quãng đường thực chỉ khoảng **mười ba phẩy hai đơn vị — chưa nổi bảy mươi phần trăm** khoảng cách cần vượt. Vậy là **không tồn tại quỹ đạo nào** cho phép một tác nhân đơn độc vượt cổng, nên mọi lần vượt cổng thành công đều là bằng chứng của hợp tác thật.
>
> **Lớp thứ hai là quan sát trực tiếp** qua ứng dụng trình diễn: em nạp cả mười lăm mô hình vào và xem hành vi thật. Không lần chạy nào đạt phần thưởng sát trần mà lại không giải được nhiệm vụ."

### Q11. "Sao ứng dụng nặng tới 325 MB chỉ cho năm mô hình?"

> "Thủ phạm **không phải số lượng mô hình mà là kiến trúc mạng của riêng Capture The Flag**. Cách quan sát tín hiệu mục tiêu của môi trường này khiến ML-Agents dựng bộ mã hóa theo kiểu **hypernetwork** — một nhánh phụ sinh trọng số cho lớp ẩn chính — đẩy số tham số của một chính sách nhỏ lên **gần mười bảy triệu**.
>
> Nghĩa là **bớt mô hình đi không giải quyết được gì**. Muốn giảm dung lượng bản phát hành thì phải huấn luyện lại Capture The Flag với kiểu điều kiện hóa mục tiêu khác. Em đã ghi hạn chế này ở Mục 5.9."

### Q12. "Nếu làm lại, em sẽ làm khác gì?"

> "**Ba việc, theo thứ tự ưu tiên.**
>
> **Một, chạy nhiều seed ngay từ đầu.** Nếu chỉ được sửa đúng một điều thì em sẽ sửa điều này — em sẽ giảm ngân sách bước mỗi lần chạy để đổi lấy ba đến năm seed cho mỗi tổ hợp, vì phương sai giữa các lần chạy có giá trị hơn vài trăm nghìn bước cuối.
>
> **Hai, thiết kế Football Table và Capture The Flag khó hơn ngay từ đầu.** Em đã đặt độ khó ở mức mà cả nhóm dẫn đầu cùng chạm trần, nên hai môi trường đó mất khả năng phân biệt. Với Capture The Flag em sẽ thêm bài trong chương trình học hoặc buộc phối hợp chặt hơn; với Football Table em sẽ thêm một đối thủ mốc cố định bên cạnh self-play.
>
> **Ba, tách bộ đệm phát lại theo bài học** ngay từ đầu cho các thuật toán off-policy chạy cùng curriculum — đó chính là giả thuyết mà em đưa ra cho thất bại của SAC nhưng chưa kịp kiểm chứng."

## 10.3. Bảng số liệu cần nhớ chính xác

**Ba con số quan trọng nhất:**
```
SAC:   Cross The Road 0,846   →   Capture The Flag 0,183     (chênh 0,663)
Nhóm dẫn đầu Capture The Flag:   0,800 – 0,840              (chênh 0,04)
Nhóm dẫn đầu Cross The Road:     0,835 – 0,846              (chênh 0,011)
```

**Ba môi trường — obs / action / budget:**
```
Football Table    60 obs   8 liên tục     1,60M   self-play, 3.000 bước/lượt
Capture The Flag  61 obs   7 rời rạc      1,70M   group reward, 100.000 bước/lượt
Cross The Road    132 obs  4 rời rạc      2,00M   không giới hạn bước
```

**Ba hằng số phần thưởng và lập luận:**
```
Football:  +5 / −1 / −1/3000     ngưỡng tấn công p > (R₋−1)/(R₊+R₋) → 0 thay vì 0,4
CTF:       +1 nhóm, +0,5 nhóm/lần vượt cổng, κ=0,01 PBRS, +0,5/N bàn đạp, −0,1/N thời gian
CTR:       +1 / −0,025 / tò mò 0,02    ngưỡng p > R₋/(1+R₋) = 2,4% thay vì 50%
```

**Thời gian chạy đáng nhớ:**
```
PPO ~48 phút    vs    SAC ~139 phút    vs    DQN ~148 phút   (Cross The Road)
```

**ELO Football Table:** khởi tạo 1200 → MAPPO 1260 (+64), PPO 1259 (+60), SAC 1254 (+57), MA-POCA 1237 (+36)

## 10.4. Bốn câu chốt để dùng linh hoạt

1. *"Năm thuật toán ở đây là **phép thử**, không phải **đối tượng** đánh giá."*
2. *"Một hàm phần thưởng hỏng **không báo lỗi** — nó chỉ lặng lẽ khiến tác nhân học sai."*
3. *"**Đặc tính bài toán chi phối kết quả mạnh hơn lựa chọn thuật toán.**"*
4. *"Muốn hai môi trường kia nói được nhiều hơn thì phải làm chúng **khó lên**, chứ không phải **chạy lâu hơn**."*

## 10.5. Checklist trước buổi bảo vệ

- [ ] Nhớ chính xác 3 con số: 0,846 / 0,183 / 0,04
- [ ] Viết được ra giấy 2 bất đẳng thức ngưỡng (Football + Cross The Road)
- [ ] Kể trôi chảy câu chuyện CTF v1 thất bại → chẩn đoán → 4 thay đổi
- [ ] Giải thích được vì sao PBRS bảo toàn chính sách tối ưu (tổng chu trình = 0)
- [ ] Nhớ 4 nguyên tắc thiết kế reward theo đúng thứ tự
- [ ] Nhớ 3 tiêu chí nghiệm thu môi trường
- [ ] Chuẩn bị sẵn câu trả lời "1 seed" và "Football chỉ đạt 2/3"
- [ ] Demo chạy được: mở ứng dụng, chọn CTR → Agent tự chơi → so 2 mô hình khác thuật toán
- [ ] Sẵn sàng chỉ vào Bảng 4.7 (chỉ số nội tại) để chứng minh SAC thất bại bằng 4 chỉ số độc lập

---

*Tài liệu tổng hợp từ toàn bộ file `.tex` của đồ án. Mọi số liệu, công thức và lập luận đều đối chiếu trực tiếp với bản gốc.*

