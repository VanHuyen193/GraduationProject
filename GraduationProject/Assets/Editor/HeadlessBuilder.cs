using System;
using System.Collections.Generic;
using System.IO;
using UnityEditor;
using UnityEditor.Build.Reporting;
using UnityEngine;

namespace GraduationProject.EditorTools
{
    /// <summary>
    /// Build ba file .exe không đồ hoạ, mỗi file chứa đúng MỘT scene huấn luyện.
    ///
    /// Vì sao cần: nếu huấn luyện qua Unity Editor thì mỗi lần chạy phải mở scene
    /// rồi bấm Play bằng tay — không tự động hoá được 9 run, không chạy qua đêm
    /// được, và không dùng được --num-envs để chạy nhiều tiến trình song song.
    /// Có file .exe thì mlagents-learn tự khởi chạy môi trường qua --env.
    ///
    /// Mỗi build chỉ nhét một scene để tránh nạp nhầm scene menu của GameHub.
    ///
    /// Dùng: menu  Tools ▸ Training ▸ Build Training Envs
    /// Hoặc batch mode:  -executeMethod GraduationProject.EditorTools.HeadlessBuilder.BuildAllFromCommandLine
    /// </summary>
    public static class HeadlessBuilder
    {
        private struct EnvBuild
        {
            public string Scene;
            public string Exe;
        }

        private static readonly EnvBuild[] Targets =
        {
            new EnvBuild { Scene = "Assets/CrossTheRoad/Scenes/CrossTheRoad.unity",   Exe = "CrossTheRoad" },
            new EnvBuild { Scene = "Assets/Collaboration/Scenes/CaptureTheFlag.unity", Exe = "CaptureTheFlag" },
            new EnvBuild { Scene = "Assets/Football/Football.unity",                   Exe = "Football" },
        };

        private static string BuildRoot =>
            Path.Combine(Directory.GetParent(Application.dataPath)!.FullName, "Builds");

        [MenuItem("Tools/Training/Build Training Envs")]
        public static void BuildAllFromMenu()
        {
            var failed = BuildAll();
            if (failed.Count == 0)
                EditorUtility.DisplayDialog("Build xong",
                    $"Đã build {Targets.Length} môi trường vào:\n{BuildRoot}", "OK");
            else
                EditorUtility.DisplayDialog("Build lỗi",
                    "Thất bại:\n" + string.Join("\n", failed), "OK");
        }

        public static void BuildAllFromCommandLine()
        {
            var failed = BuildAll();
            EditorApplication.Exit(failed.Count == 0 ? 0 : 1);
        }

        private static List<string> BuildAll()
        {
            var failed = new List<string>();
            Directory.CreateDirectory(BuildRoot);

            foreach (var t in Targets)
            {
                if (!File.Exists(t.Scene))
                {
                    Debug.LogError($"[HeadlessBuilder] Không thấy scene {t.Scene}");
                    failed.Add(t.Exe);
                    continue;
                }

                // Mỗi môi trường một thư mục riêng: Unity ghi kèm thư mục _Data,
                // dồn chung một chỗ thì các build ghi đè lẫn nhau.
                var outDir = Path.Combine(BuildRoot, t.Exe);
                Directory.CreateDirectory(outDir);

                var options = new BuildPlayerOptions
                {
                    scenes = new[] { t.Scene },
                    locationPathName = Path.Combine(outDir, t.Exe + ".exe"),
                    target = BuildTarget.StandaloneWindows64,
                    // EnableHeadlessMode đã lỗi thời ở Unity 6; truyền -nographics
                    // lúc chạy (mlagents-learn --no-graphics) là đủ và vẫn build
                    // được player bình thường.
                    //
                    // KHÔNG dùng BuildOptions.Development: development player bật
                    // profiler và bỏ một phần tối ưu, chạy chậm hơn hẳn release —
                    // mà toàn bộ mục đích của build này là chạy nhanh.
                    options = BuildOptions.None
                };

                Debug.Log($"[HeadlessBuilder] Đang build {t.Exe} từ {t.Scene} …");
                var report = BuildPipeline.BuildPlayer(options);
                var summary = report.summary;

                if (summary.result == BuildResult.Succeeded)
                {
                    Debug.Log($"[HeadlessBuilder] {t.Exe}: OK " +
                              $"({summary.totalSize / (1024 * 1024)} MB, {summary.totalTime.TotalSeconds:F0}s) " +
                              $"→ {options.locationPathName}");
                }
                else
                {
                    Debug.LogError($"[HeadlessBuilder] {t.Exe}: {summary.result} " +
                                   $"({summary.totalErrors} lỗi)");
                    failed.Add(t.Exe);
                }
            }

            if (failed.Count > 0)
                Debug.LogError("[HeadlessBuilder] Thất bại: " + string.Join(", ", failed));
            else
                Debug.Log($"[HeadlessBuilder] Đã build xong toàn bộ vào {BuildRoot}");

            return failed;
        }
    }
}
