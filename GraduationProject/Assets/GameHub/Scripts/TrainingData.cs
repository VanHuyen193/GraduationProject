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
        public int[] cs;   // curve steps
        public float[] cv; // curve values (đã làm mượt + rút gọn)
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

        public static readonly string[] AlgoOrder = { "PPO", "SAC", "MA-POCA", "MAPPO" };

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
                default: return new Color32(160, 160, 160, 255);
            }
        }
    }
}
