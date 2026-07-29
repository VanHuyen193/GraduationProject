using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
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
    ///                   [-envs CrossTheRoad,Football]
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
            // Bản action rời rạc, chỉ dùng cho DQN — xem FootballDiscreteMaker.cs.
            new EnvBuild { Scene = "Assets/Football/FootballDiscrete.unity",           Exe = "FootballDiscrete" },
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
            // -envs CrossTheRoad,Football → chỉ build những môi trường được kể tên.
            // Cần vì build cả ba scene mất khoảng một tiếng: khi một scene lỗi hoặc
            // bị giết giữa chừng, không có cách nào build lại riêng nó mà không tốn
            // thêm ~45 phút dựng lại hai scene đã xong.
            string[] only = null;
            var argv = Environment.GetCommandLineArgs();
            for (int i = 0; i < argv.Length - 1; i++)
            {
                if (argv[i] == "-envs")
                    only = argv[i + 1].Split(',')
                                      .Select(s => s.Trim())
                                      .Where(s => s.Length > 0)
                                      .ToArray();
            }

            if (only != null)
            {
                var unknown = only
                    .Where(n => !Targets.Any(t => string.Equals(t.Exe, n,
                                                 StringComparison.OrdinalIgnoreCase)))
                    .ToArray();
                if (unknown.Length > 0)
                {
                    Debug.LogError($"[HeadlessBuilder] -envs có tên lạ: " +
                                   string.Join(", ", unknown) + ". Hợp lệ: " +
                                   string.Join(", ", Targets.Select(t => t.Exe)));
                    EditorApplication.Exit(1);
                    return;
                }
            }

            var failed = BuildAll(only);
            EditorApplication.Exit(failed.Count == 0 ? 0 : 1);
        }

        private static List<string> BuildAll(string[] only = null)
        {
            var failed = new List<string>();
            Directory.CreateDirectory(BuildRoot);

            foreach (var t in Targets)
            {
                if (only != null && !only.Contains(t.Exe, StringComparer.OrdinalIgnoreCase))
                {
                    Debug.Log($"[HeadlessBuilder] Bỏ qua {t.Exe} (không có trong -envs)");
                    continue;
                }

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
