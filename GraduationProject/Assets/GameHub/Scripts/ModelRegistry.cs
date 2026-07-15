using System.Linq;
using Unity.InferenceEngine;
using UnityEngine;

namespace GameHub
{
    /// <summary>
    /// Truy xuất các model ONNX đặt trong Assets/GameHub/Resources/AgentModels/&lt;Env&gt;/.
    /// Chỉ cần thả thêm file .onnx vào thư mục tương ứng là menu tự nhận.
    /// </summary>
    public static class ModelRegistry
    {
        public static string[] GetModelNames(GameEnvironment env)
        {
            return Resources
                .LoadAll<ModelAsset>(GameModeSelection.ModelFolderFor(env))
                .Select(m => m.name)
                .OrderBy(n => n)
                .ToArray();
        }

        public static ModelAsset Load(GameEnvironment env, string modelName)
        {
            if (string.IsNullOrEmpty(modelName))
            {
                return null;
            }

            ModelAsset model = Resources.Load<ModelAsset>(
                GameModeSelection.ModelFolderFor(env) + "/" + modelName
            );

            if (model == null)
            {
                Debug.LogError(
                    $"[GameHub] Không tìm thấy model '{modelName}' cho môi trường {env}"
                );
            }

            return model;
        }
    }
}
