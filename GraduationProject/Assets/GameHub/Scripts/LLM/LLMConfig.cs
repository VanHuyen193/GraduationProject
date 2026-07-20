using System;
using System.IO;
using UnityEngine;

namespace GameHub
{
    // Nhà cung cấp LLM được hỗ trợ
    public enum LLMProvider
    {
        OpenAI,
        Gemini
    }

    /// <summary>Một lựa chọn LLM hiển thị trong menu.</summary>
    public class LLMOption
    {
        public readonly string DisplayName;
        public readonly LLMProvider Provider;
        public readonly string ModelId;

        public LLMOption(string displayName, LLMProvider provider, string modelId)
        {
            DisplayName = displayName;
            Provider = provider;
            ModelId = modelId;
        }
    }

    /// <summary>
    /// Đọc API key từ StreamingAssets/llm_config.json (hoặc biến môi trường
    /// OPENAI_API_KEY / GEMINI_API_KEY) và liệt kê các LLM có thể chọn.
    /// File cấu hình KHÔNG được commit lên git.
    /// </summary>
    public static class LLMConfig
    {
        public static readonly LLMOption[] Options =
        {
            new LLMOption("ChatGPT (GPT-4o mini)", LLMProvider.OpenAI, "gpt-4o-mini"),
            new LLMOption("ChatGPT (GPT-4o)", LLMProvider.OpenAI, "gpt-4o"),
            new LLMOption("Gemini 2.0 Flash", LLMProvider.Gemini, "gemini-2.0-flash"),
            new LLMOption("Gemini 1.5 Flash", LLMProvider.Gemini, "gemini-1.5-flash"),
        };

        [Serializable]
        private class ConfigData
        {
            public string openai_api_key;
            public string gemini_api_key;
        }

        private static ConfigData loaded;
        private static bool loadAttempted;

        public static string ConfigPath =>
            Path.Combine(Application.streamingAssetsPath, "llm_config.json");

        private static ConfigData Load()
        {
            if (loadAttempted)
            {
                return loaded;
            }

            loadAttempted = true;

            try
            {
                if (File.Exists(ConfigPath))
                {
                    loaded = JsonUtility.FromJson<ConfigData>(
                        File.ReadAllText(ConfigPath));
                }
            }
            catch (Exception e)
            {
                Debug.LogWarning("[LLM] Không đọc được llm_config.json: " + e.Message);
            }

            return loaded;
        }

        public static string GetApiKey(LLMProvider provider)
        {
            ConfigData data = Load();

            string key = provider == LLMProvider.OpenAI
                ? data?.openai_api_key
                : data?.gemini_api_key;

            if (string.IsNullOrEmpty(key))
            {
                key = Environment.GetEnvironmentVariable(
                    provider == LLMProvider.OpenAI
                        ? "OPENAI_API_KEY"
                        : "GEMINI_API_KEY");
            }

            return string.IsNullOrEmpty(key) ? null : key.Trim();
        }

        public static bool HasApiKey(LLMProvider provider)
        {
            return GetApiKey(provider) != null;
        }
    }
}
