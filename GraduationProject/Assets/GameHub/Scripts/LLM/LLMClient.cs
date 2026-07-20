using System;
using System.Collections;
using System.Text;
using UnityEngine;
using UnityEngine.Networking;

namespace GameHub
{
    /// <summary>
    /// Gọi API chat của OpenAI (ChatGPT) / Google (Gemini) bằng UnityWebRequest.
    /// Dùng chung cho mọi driver LLM; request chạy bằng coroutine trên một
    /// runner ẩn nên không chặn game loop.
    /// </summary>
    public static class LLMClient
    {
        private class CoroutineRunner : MonoBehaviour { }

        private static CoroutineRunner runner;

        private static CoroutineRunner Runner
        {
            get
            {
                if (runner == null)
                {
                    var go = new GameObject("LLMClientRunner");
                    go.hideFlags = HideFlags.HideInHierarchy;
                    UnityEngine.Object.DontDestroyOnLoad(go);
                    runner = go.AddComponent<CoroutineRunner>();
                }

                return runner;
            }
        }

        /// <summary>
        /// Gửi 1 lượt chat tới LLM. Callback nhận (nội dung trả lời, lỗi);
        /// đúng một trong hai khác null.
        /// </summary>
        public static void Request(
            LLMProvider provider,
            string modelId,
            string systemPrompt,
            string userPrompt,
            Action<string, string> onDone)
        {
            string apiKey = LLMConfig.GetApiKey(provider);

            if (apiKey == null)
            {
                onDone(null, "Chưa có API key cho " + provider);
                return;
            }

            Runner.StartCoroutine(
                SendCoroutine(provider, modelId, apiKey,
                    systemPrompt, userPrompt, onDone));
        }

        private static IEnumerator SendCoroutine(
            LLMProvider provider,
            string modelId,
            string apiKey,
            string systemPrompt,
            string userPrompt,
            Action<string, string> onDone)
        {
            string url;
            string body;

            if (provider == LLMProvider.OpenAI)
            {
                url = "https://api.openai.com/v1/chat/completions";
                body = BuildOpenAIBody(modelId, systemPrompt, userPrompt);
            }
            else
            {
                url = "https://generativelanguage.googleapis.com/v1beta/models/"
                    + modelId + ":generateContent?key=" + apiKey;
                body = BuildGeminiBody(systemPrompt, userPrompt);
            }

            using (var request = new UnityWebRequest(url, "POST"))
            {
                request.uploadHandler =
                    new UploadHandlerRaw(Encoding.UTF8.GetBytes(body));
                request.downloadHandler = new DownloadHandlerBuffer();
                request.SetRequestHeader("Content-Type", "application/json");
                request.timeout = 30;

                if (provider == LLMProvider.OpenAI)
                {
                    request.SetRequestHeader(
                        "Authorization", "Bearer " + apiKey);
                }

                yield return request.SendWebRequest();

                if (request.result != UnityWebRequest.Result.Success)
                {
                    string detail = request.downloadHandler != null
                        ? request.downloadHandler.text
                        : "";

                    onDone(null, request.error
                        + (string.IsNullOrEmpty(detail)
                            ? ""
                            : " | " + Truncate(detail, 200)));
                    yield break;
                }

                string content = provider == LLMProvider.OpenAI
                    ? ParseOpenAI(request.downloadHandler.text)
                    : ParseGemini(request.downloadHandler.text);

                if (content == null)
                {
                    onDone(null, "Không đọc được phản hồi: "
                        + Truncate(request.downloadHandler.text, 200));
                }
                else
                {
                    onDone(content, null);
                }
            }
        }

        private static string Truncate(string s, int max)
        {
            return s.Length <= max ? s : s.Substring(0, max) + "...";
        }

        // =====================================================
        // JSON REQUEST/RESPONSE (JsonUtility + escape thủ công)
        // =====================================================

        private static string Escape(string s)
        {
            var sb = new StringBuilder(s.Length + 16);

            foreach (char c in s)
            {
                switch (c)
                {
                    case '"': sb.Append("\\\""); break;
                    case '\\': sb.Append("\\\\"); break;
                    case '\n': sb.Append("\\n"); break;
                    case '\r': sb.Append("\\r"); break;
                    case '\t': sb.Append("\\t"); break;
                    default:
                        if (c < ' ')
                        {
                            sb.Append("\\u").Append(((int)c).ToString("x4"));
                        }
                        else
                        {
                            sb.Append(c);
                        }
                        break;
                }
            }

            return sb.ToString();
        }

        private static string BuildOpenAIBody(
            string model, string system, string user)
        {
            return "{\"model\":\"" + model + "\","
                + "\"temperature\":0,"
                + "\"max_tokens\":200,"
                + "\"messages\":["
                + "{\"role\":\"system\",\"content\":\"" + Escape(system) + "\"},"
                + "{\"role\":\"user\",\"content\":\"" + Escape(user) + "\"}]}";
        }

        private static string BuildGeminiBody(string system, string user)
        {
            return "{\"systemInstruction\":{\"parts\":[{\"text\":\""
                + Escape(system) + "\"}]},"
                + "\"contents\":[{\"role\":\"user\",\"parts\":[{\"text\":\""
                + Escape(user) + "\"}]}],"
                + "\"generationConfig\":{\"temperature\":0,\"maxOutputTokens\":200}}";
        }

        [Serializable]
        private class OpenAIResponse
        {
            [Serializable]
            public class Choice
            {
                public Message message;
            }

            [Serializable]
            public class Message
            {
                public string content;
            }

            public Choice[] choices;
        }

        private static string ParseOpenAI(string json)
        {
            try
            {
                var response = JsonUtility.FromJson<OpenAIResponse>(json);
                return response?.choices != null && response.choices.Length > 0
                    ? response.choices[0].message?.content
                    : null;
            }
            catch
            {
                return null;
            }
        }

        [Serializable]
        private class GeminiResponse
        {
            [Serializable]
            public class Candidate
            {
                public Content content;
            }

            [Serializable]
            public class Content
            {
                public Part[] parts;
            }

            [Serializable]
            public class Part
            {
                public string text;
            }

            public Candidate[] candidates;
        }

        private static string ParseGemini(string json)
        {
            try
            {
                var response = JsonUtility.FromJson<GeminiResponse>(json);

                if (response?.candidates == null
                    || response.candidates.Length == 0)
                {
                    return null;
                }

                GeminiResponse.Part[] parts = response.candidates[0].content?.parts;
                return parts != null && parts.Length > 0 ? parts[0].text : null;
            }
            catch
            {
                return null;
            }
        }
    }
}
