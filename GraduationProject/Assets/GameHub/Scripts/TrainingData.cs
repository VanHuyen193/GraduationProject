using System;
using UnityEngine;

namespace GameHub
{
    /// <summary>Thông số + đường cong reward của một thuật toán trên một môi trường.</summary>
    [Serializable]
    public class AlgoTraining
    {
        public string algo;
        public bool found;
        public string runId;
        public int steps;
        public int maxEnvSteps;
        public int actualCount;
        public float final;
        public float max;
        public float meanLast10;
        public int convergeStep;
        public float epLenFinal;
        public string actionSpace; // "discrete" | "continuous" — đọc từ chính file ONNX
        public string model;       // tên file ONNX trong Resources/AgentModels (= runId)
        public int[] cs;   // curve steps
        public float[] cv; // curve values (đã làm mượt + rút gọn)

        public bool IsDiscrete
        {
            get { return actionSpace == "discrete"; }
        }
    }

    [Serializable]
    public class EnvTraining
    {
        public string key;
        public string name;
        public AlgoTraining[] algorithms;

        public AlgoTraining Algo(string algoName)
        {
            if (algorithms == null)
            {
                return null;
            }

            foreach (AlgoTraining a in algorithms)
            {
                if (a.algo == algoName)
                {
                    return a;
                }
            }

            return null;
        }

        /// <summary>Lần chạy đã sinh ra file ONNX này (tên file = mã lần chạy).</summary>
        public AlgoTraining ByModel(string modelName)
        {
            if (algorithms == null || string.IsNullOrEmpty(modelName))
            {
                return null;
            }

            foreach (AlgoTraining a in algorithms)
            {
                if (a.model == modelName || a.runId == modelName)
                {
                    return a;
                }
            }

            return null;
        }
    }

    [Serializable]
    public class TrainingDataRoot
    {
        public string generated;
        public EnvTraining[] environments;
    }

    /// <summary>
    /// Nạp dữ liệu training thật (xuất từ tfevents bằng export_training_data.py)
    /// từ Resources/TrainingData/training_data.json.
    /// </summary>
    public static class TrainingDataStore
    {
        private static TrainingDataRoot cached;
        private static bool loaded;

        public static readonly string[] AlgoOrder =
            { "PPO", "SAC", "MA-POCA", "MAPPO", "DQN" };

        public static TrainingDataRoot Data
        {
            get
            {
                if (!loaded)
                {
                    loaded = true;
                    TextAsset ta = Resources.Load<TextAsset>(
                        "TrainingData/training_data");

                    if (ta != null)
                    {
                        cached = JsonUtility.FromJson<TrainingDataRoot>(ta.text);
                    }
                    else
                    {
                        Debug.LogWarning(
                            "TrainingDataStore: không tìm thấy training_data.json");
                    }
                }

                return cached;
            }
        }

        public static EnvTraining ForEnv(GameEnvironment env)
        {
            TrainingDataRoot d = Data;
            if (d == null || d.environments == null)
            {
                return null;
            }

            string key = env.ToString();
            foreach (EnvTraining e in d.environments)
            {
                if (e.key == key)
                {
                    return e;
                }
            }

            return null;
        }

        /// <summary>Màu chuẩn cho từng thuật toán (khớp báo cáo).</summary>
        public static Color ColorFor(string algo)
        {
            switch (algo)
            {
                case "PPO": return new Color32(33, 150, 243, 255);    // xanh dương
                case "SAC": return new Color32(76, 175, 80, 255);     // xanh lá
                case "MA-POCA": return new Color32(255, 152, 0, 255); // cam
                case "MAPPO": return new Color32(156, 39, 176, 255);  // tím
                case "DQN": return new Color32(229, 57, 53, 255);     // đỏ
                default: return new Color32(160, 160, 160, 255);
            }
        }

        /// <summary>Lần chạy ứng với một file ONNX trong Resources/AgentModels.</summary>
        public static AlgoTraining RunOf(GameEnvironment env, string modelName)
        {
            EnvTraining e = ForEnv(env);
            return e != null ? e.ByModel(modelName) : null;
        }

        /// <summary>
        /// Nhãn hiển thị cho một model trong menu: "PPO · ctr01".
        /// Model lạ (người dùng tự thả vào thư mục) giữ nguyên tên file.
        /// </summary>
        public static string LabelFor(GameEnvironment env, string modelName)
        {
            AlgoTraining a = RunOf(env, modelName);
            return a != null ? a.algo + " · " + modelName : modelName;
        }
    }
}
