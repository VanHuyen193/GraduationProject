using System.IO;
using System.Linq;
using Unity.MLAgents.Actuators;
using Unity.MLAgents.Policies;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;

namespace GraduationProject.EditorTools
{
    /// <summary>
    /// Sinh Assets/Football/FootballDiscrete.unity — bản sao của Football.unity với
    /// Behavior Parameters đổi từ continuous(8) sang discrete 8 nhánh × 3 mức.
    ///
    /// Vì sao cần một scene riêng thay vì sửa tại chỗ: DQN chỉ chạy được action rời
    /// rạc, còn PPO/SAC/MA-POCA/MAPPO trên Football dùng continuous. Action spec
    /// được nướng vào file .exe lúc build nên hai bên không thể dùng chung một
    /// build. Sửa tại chỗ thì mỗi lần đổi thuật toán lại phải sửa scene và build
    /// lại — giữ hai scene song song thì chạy được cả 5 thuật toán không cần đụng
    /// tay vào Unity nữa.
    ///
    /// Ánh xạ mức → lực đã có sẵn trong FootballAgent.OnActionReceived:
    /// DiscreteActions[i] - 1 cho ra {-1, 0, +1} cho từng kênh [trượt, xoay] × 4 thanh.
    ///
    /// Dùng: menu  Tools ▸ Training ▸ Make FootballDiscrete Scene
    /// Hoặc batch mode:  -executeMethod GraduationProject.EditorTools.FootballDiscreteMaker.RunFromCommandLine
    /// </summary>
    public static class FootballDiscreteMaker
    {
        private const string SourceScene = "Assets/Football/Football.unity";
        private const string TargetScene = "Assets/Football/FootballDiscrete.unity";
        private const int Branches = 8;
        private const int BranchSize = 3;

        [MenuItem("Tools/Training/Make FootballDiscrete Scene")]
        public static void RunFromMenu()
        {
            var n = Build();
            EditorUtility.DisplayDialog(
                n > 0 ? "Xong" : "Lỗi",
                n > 0 ? $"Đã đổi {n} Behavior Parameters sang discrete {Branches}×{BranchSize}.\n{TargetScene}"
                      : "Không đổi được — xem Console.",
                "OK");
        }

        public static void RunFromCommandLine()
        {
            EditorApplication.Exit(Build() > 0 ? 0 : 1);
        }

        private static int Build()
        {
            if (!File.Exists(SourceScene))
            {
                Debug.LogError($"[FootballDiscrete] Không thấy scene nguồn {SourceScene}");
                return 0;
            }

            var scene = EditorSceneManager.OpenScene(SourceScene, OpenSceneMode.Single);

            // Lấy cả object đang tắt: các bản sao area do TrainingAreaMultiplier tạo
            // có thể không active, mà chúng vẫn được nướng vào build.
            var all = Resources.FindObjectsOfTypeAll<BehaviorParameters>()
                               .Where(b => b.gameObject.scene == scene)
                               .ToArray();

            if (all.Length == 0)
            {
                Debug.LogError("[FootballDiscrete] Không tìm thấy BehaviorParameters nào.");
                return 0;
            }

            var spec = ActionSpec.MakeDiscrete(
                Enumerable.Repeat(BranchSize, Branches).ToArray());

            int changed = 0;
            foreach (var bp in all)
            {
                var before = bp.BrainParameters.ActionSpec;
                bp.BrainParameters.ActionSpec = spec;
                // Model continuous cũ gán sẵn trong scene sẽ không khớp action spec
                // mới; để nguyên thì agent chạy inference bằng model sai thay vì
                // nhận lệnh từ trainer. Gỡ ra, DQN sẽ tự nạp model của nó.
                bp.Model = null;
                EditorUtility.SetDirty(bp);
                changed++;

                if (changed == 1)
                    Debug.Log($"[FootballDiscrete] Mẫu đầu: '{bp.BehaviorName}' " +
                              $"continuous {before.NumContinuousActions} → " +
                              $"discrete {Branches}×{BranchSize}");
            }

            EditorSceneManager.MarkSceneDirty(scene);
            if (!EditorSceneManager.SaveScene(scene, TargetScene, true))
            {
                Debug.LogError($"[FootballDiscrete] Lưu {TargetScene} thất bại.");
                return 0;
            }
            AssetDatabase.Refresh();

            Debug.Log($"[FootballDiscrete] Đã đổi {changed} Behavior Parameters → {TargetScene}");
            return changed;
        }
    }
}
