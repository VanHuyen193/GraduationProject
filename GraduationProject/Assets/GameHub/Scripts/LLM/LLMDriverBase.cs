using System.Collections.Generic;
using UnityEngine;

namespace GameHub
{
    /// <summary>
    /// Lớp nền cho các driver LLM: định kỳ gửi trạng thái game (dạng text)
    /// tới LLM đã chọn trong menu, parse action từ phản hồi.
    /// Lớp con chỉ cần cung cấp system prompt, mô tả trạng thái và cách parse.
    /// </summary>
    public abstract class LLMDriverBase : MonoBehaviour
    {
        [Tooltip("Giãn cách tối thiểu giữa 2 lần hỏi LLM (giây)")]
        public float requestInterval = 1.5f;

        /// <summary>Dòng trạng thái hiển thị trên HUD.</summary>
        public string StatusLine { get; protected set; } = "LLM: đang khởi động...";

        /// <summary>Số lượt hỏi/đáp thành công (để hiển thị/đánh giá).</summary>
        public int ReplyCount { get; private set; }

        private bool busy;
        private float nextRequestTime;
        private int consecutiveErrors;

        protected abstract string SystemPrompt { get; }

        protected abstract string BuildUserPrompt();

        /// <summary>Parse phản hồi, lưu action; trả về false nếu không hiểu.</summary>
        protected abstract bool TryParseReply(string reply);

        private void Update()
        {
            if (busy || Time.time < nextRequestTime)
            {
                return;
            }

            busy = true;

            LLMClient.Request(
                GameModeSelection.LLM.Provider,
                GameModeSelection.LLM.ModelId,
                SystemPrompt,
                BuildUserPrompt(),
                OnResponse);
        }

        private void OnResponse(string content, string error)
        {
            busy = false;

            if (error != null)
            {
                consecutiveErrors++;

                // Lỗi liên tiếp (hết quota, sai key, mất mạng) → giãn dần
                nextRequestTime = Time.time
                    + Mathf.Min(10f, requestInterval * (1 + consecutiveErrors));

                StatusLine = "LLM lỗi: " + error;
                Debug.LogWarning("[LLM] " + error);
                return;
            }

            consecutiveErrors = 0;
            nextRequestTime = Time.time + requestInterval;

            if (TryParseReply(content))
            {
                ReplyCount++;
            }
            else
            {
                StatusLine = "LLM trả lời không hợp lệ: " + content;
            }
        }

        /// <summary>
        /// Lấy các số nguyên trong phản hồi (LLM có thể kèm giải thích);
        /// trả về danh sách theo thứ tự xuất hiện.
        /// </summary>
        protected static List<int> ExtractInts(string reply)
        {
            var result = new List<int>();

            if (string.IsNullOrEmpty(reply))
            {
                return result;
            }

            int i = 0;

            while (i < reply.Length)
            {
                char c = reply[i];

                bool negative = c == '-'
                    && i + 1 < reply.Length
                    && char.IsDigit(reply[i + 1]);

                if (negative || char.IsDigit(c))
                {
                    int start = i;

                    if (negative)
                    {
                        i++;
                    }

                    while (i < reply.Length && char.IsDigit(reply[i]))
                    {
                        i++;
                    }

                    if (int.TryParse(
                            reply.Substring(start, i - start), out int value))
                    {
                        result.Add(value);
                    }
                }
                else
                {
                    i++;
                }
            }

            return result;
        }
    }
}
