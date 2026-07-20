# Chế độ "Agent đấu LLM" (ChatGPT / Gemini)

Chế độ chơi thứ 4 trong GameHub: agent RL đã train đấu / phối hợp với một
mô hình ngôn ngữ lớn. LLM nhận **mô tả trạng thái game bằng text** mỗi ~1-1.5
giây, trả về **action** qua API; action được đưa vào agent qua cơ chế
Heuristic — giống hệt cách người chơi điều khiển, nên không đụng vào
model RL hay logic môi trường.

## Cài đặt API key (1 lần)

Copy `Assets/StreamingAssets/llm_config.example.json` thành
`Assets/StreamingAssets/llm_config.json` rồi điền key:

```json
{
    "openai_api_key": "sk-...",
    "gemini_api_key": "AIza..."
}
```

- Chỉ cần key của nhà cung cấp bạn định dùng (menu sẽ báo nếu thiếu).
- Lấy key: OpenAI → https://platform.openai.com/api-keys ,
  Gemini → https://aistudio.google.com/apikey (Gemini có bậc miễn phí).
- File này đã nằm trong `.gitignore` — **không commit key lên git**.
- Cách khác: đặt biến môi trường `OPENAI_API_KEY` / `GEMINI_API_KEY`
  trước khi mở Unity.

## Cách chơi

Mở scene `MainMenu` → chọn môi trường → chế độ **"Agent đấu LLM"** →
slot 1 chọn model RL (.onnx), slot 2 chọn LLM (GPT-4o mini / GPT-4o /
Gemini 2.0 Flash / Gemini 1.5 Flash) → **BẮT ĐẦU**.

Từng môi trường:

| Môi trường | Thể thức | LLM thấy gì / làm gì |
|---|---|---|
| Cross The Road | **Đua** — RL khu trái, LLM khu phải | Vị trí mình/đích/xe (kèm hướng, tốc độ) → chọn 1 action (0-3), 1 giây/lượt |
| Capture The Flag | **Phối hợp** — RL 1 nhân vật, LLM 1 nhân vật | Vị trí 2 agent, nút bấm, checkpoint → chọn 1 action (0-6), giữ tới lượt sau |
| Football Table | **Đối kháng** — Xanh = RL, Đỏ = LLM | Bóng + 4 thanh (chuẩn hoá) → 8 lệnh [trượt, xoay] × 4 thanh, giữ tới lượt sau |

Dòng trạng thái LLM (action vừa chọn, số lượt, lỗi API nếu có) hiển thị
ngay dưới thanh thông tin trên cùng.

## Kiến trúc (cho báo cáo)

```
MainMenu (chọn LLM) ──► GameModeSelection.LLM
                              │
Scene load ──► GameModeApplier (case AgentVsLLM)
                              │  AddComponent
                              ▼
   LLM*Driver (mỗi môi trường một driver, kế thừa LLMDriverBase)
     │  BuildUserPrompt()  ── mô tả trạng thái bằng text
     │  LLMClient.Request() ── UnityWebRequest → OpenAI / Gemini API
     │  TryParseReply()    ── parse số nguyên từ phản hồi
     ▼
   Agent.Heuristic() đọc action từ driver (như human input)
```

- `LLMClient` — gọi `POST /v1/chat/completions` (OpenAI) hoặc
  `models/{id}:generateContent` (Gemini), `temperature = 0`.
- Driver giãn request khi API lỗi liên tiếp (backoff), nên hết quota /
  mất mạng không làm treo game — agent LLM chỉ đứng yên.
- So sánh trong đồ án: RL suy luận cục bộ mỗi bước (~ms), LLM cần
  1-2 giây/lượt gọi API — thể hiện rõ trade-off giữa policy học chuyên biệt
  và khả năng suy luận tổng quát zero-shot của LLM.

## Lưu ý

- Chi phí: mỗi lượt là 1 request API (~200-400 token). GPT-4o mini và
  Gemini Flash rất rẻ; tránh treo chế độ này hàng giờ với GPT-4o.
- Cần Internet khi chơi chế độ này.
- Muốn thêm LLM khác (Claude, model local qua Ollama...): thêm vào
  `LLMConfig.Options` + một nhánh build request trong `LLMClient`.
