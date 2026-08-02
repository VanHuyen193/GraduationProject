using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using UnityEditor;
using UnityEditor.PackageManager;
using UnityEditor.SceneManagement;
using UnityEngine;
using PackageInfo = UnityEditor.PackageManager.PackageInfo;

namespace VanHuyen.RLGameEnvs.EditorTools
{
    /// <summary>
    /// Trình hướng dẫn cài đặt gói RL Game Environments.
    ///
    /// Mục tiêu: một người mới nhận gói này chỉ cần mở đúng một cửa sổ là biết mình
    /// đang thiếu gì và bấm được nút để bổ sung, thay vì phải đọc tài liệu rồi tự
    /// lần mò qua Package Manager, thư mục Samples và dòng lệnh huấn luyện.
    ///
    /// Cửa sổ chia thành các bước theo đúng thứ tự phải làm; mỗi bước tự kiểm tra
    /// trạng thái hiện tại và chỉ bật nút hành động khi bước đó thực sự còn thiếu.
    ///
    /// Mở bằng: menu  Tools ▸ RL Game Environments ▸ Setup Wizard
    /// </summary>
    public class SetupWizard : EditorWindow
    {
        private const string PackageName = "com.vanhuyen.rl-game-envs";

        private Vector2 _scroll;
        private PackageInfo _package;

        // Cache kết quả kiểm tra để không quét thư mục mỗi lần vẽ lại giao diện
        private bool[] _sampleImported = new bool[3];
        private bool _configsInstalled;
        private string[] _missingArt = new string[0];
        private double _lastCheck;

        private static readonly string[] SampleNames =
        {
            "Cross The Road", "Capture The Flag", "Football Table"
        };

        private static readonly string[] SceneNames =
        {
            "CrossTheRoad", "CaptureTheFlag", "Football"
        };

        /// <summary>
        /// Art bên thứ ba mà môi trường Cross The Road dùng để hiển thị. Gói này
        /// KHÔNG phát hành lại chúng: giấy phép Asset Store chỉ cho phép dùng trong
        /// dự án của người đã tải, không cho phép đóng gói lại cho người khác. Wizard
        /// vì thế chỉ kiểm tra và chỉ chỗ tải.
        /// </summary>
        private static readonly (string folder, string label, string url)[] ThirdPartyArt =
        {
            ("Meshtint Free Car 01 Mega Toon Series", "Meshtint Free Car 01",
             "https://assetstore.unity.com/packages/3d/vehicles/land/meshtint-free-car-01-mega-toon-series-155171"),
            ("Meshtint Free Car 02 Mega Toon Series", "Meshtint Free Car 02",
             "https://assetstore.unity.com/packages/3d/vehicles/land/meshtint-free-car-02-mega-toon-series-155172"),
            ("Meshtint Free Chicken Mega Toon Series", "Meshtint Free Chicken",
             "https://assetstore.unity.com/packages/3d/characters/animals/meshtint-free-chicken-mega-toon-series-152333"),
            ("Gridbox Prototype Materials", "Gridbox Prototype Materials",
             "https://assetstore.unity.com/packages/2d/textures-materials/gridbox-prototype-materials-129127"),
        };

        [MenuItem("Tools/RL Game Environments/Setup Wizard", priority = 0)]
        public static void Open()
        {
            var w = GetWindow<SetupWizard>(true, "RL Game Environments — Setup", true);
            w.minSize = new Vector2(560, 620);
            w.Refresh();
        }

        private void OnEnable()
        {
            Refresh();
        }

        private void OnFocus()
        {
            Refresh();
        }

        // =====================================================
        // KIỂM TRA TRẠNG THÁI
        // =====================================================
        private void Refresh()
        {
            _lastCheck = EditorApplication.timeSinceStartup;
            _package = PackageInfo.FindForAssetPath("Packages/" + PackageName + "/package.json");

            for (int i = 0; i < SampleNames.Length; i++)
            {
                _sampleImported[i] = FindSceneAsset(SceneNames[i]) != null;
            }

            _configsInstalled = Directory.Exists(ConfigTargetDir)
                && Directory.GetFiles(ConfigTargetDir, "*.yaml").Length > 0;

            _missingArt = ThirdPartyArt
                .Where(a => !ArtPresent(a.folder))
                .Select(a => a.label)
                .ToArray();

            Repaint();
        }

        private static string ConfigTargetDir
        {
            get { return Path.Combine(Directory.GetCurrentDirectory(), "config"); }
        }

        private static bool ArtPresent(string folder)
        {
            return AssetDatabase.FindAssets("t:Object")
                .Select(AssetDatabase.GUIDToAssetPath)
                .Any(p => p.Contains(folder));
        }

        private static string FindSceneAsset(string sceneName)
        {
            return AssetDatabase.FindAssets("t:Scene " + sceneName)
                .Select(AssetDatabase.GUIDToAssetPath)
                .FirstOrDefault(p => Path.GetFileNameWithoutExtension(p) == sceneName);
        }

        // =====================================================
        // GIAO DIỆN
        // =====================================================
        private void OnGUI()
        {
            _scroll = EditorGUILayout.BeginScrollView(_scroll);

            Header();
            EditorGUILayout.Space(6);

            Step1Dependencies();
            Step2Samples();
            Step3ThirdPartyArt();
            Step4TrainingConfigs();
            Step5Multiply();
            Step6Build();
            Step7Train();

            EditorGUILayout.Space(10);
            if (GUILayout.Button("Kiểm tra lại trạng thái", GUILayout.Height(24)))
            {
                Refresh();
            }

            EditorGUILayout.EndScrollView();
        }

        private void Header()
        {
            EditorGUILayout.LabelField("RL Game Environments",
                new GUIStyle(EditorStyles.boldLabel) { fontSize = 16 });

            EditorGUILayout.LabelField(
                _package != null
                    ? "Phiên bản " + _package.version + "  •  " + _package.source
                    : "Không đọc được package.json",
                EditorStyles.miniLabel);

            EditorGUILayout.HelpBox(
                "Làm lần lượt các bước dưới đây. Mỗi bước tự kiểm tra trạng thái: "
                + "dấu ✓ nghĩa là đã xong, nút bị mờ nghĩa là không cần làm gì thêm.",
                MessageType.None);
        }

        private static bool StepBox(string title, bool done, string body)
        {
            EditorGUILayout.Space(4);
            EditorGUILayout.BeginVertical(EditorStyles.helpBox);
            EditorGUILayout.LabelField((done ? "✓  " : "•  ") + title, EditorStyles.boldLabel);

            if (!string.IsNullOrEmpty(body))
            {
                EditorGUILayout.LabelField(body, EditorStyles.wordWrappedMiniLabel);
            }

            return done;
        }

        private static void EndStep()
        {
            EditorGUILayout.EndVertical();
        }

        // ---------- Bước 1 ----------
        private void Step1Dependencies()
        {
            bool ok = _package != null;

            StepBox("Bước 1 — Gói phụ thuộc", ok,
                "Gói này cần com.unity.ml-agents và com.unity.ai.inference. Unity tự "
                + "cài chúng theo khai báo dependencies trong package.json; nếu Package "
                + "Manager báo lỗi thì mở nó ra và bấm Resolve.");

            using (new EditorGUI.DisabledScope(ok))
            {
                if (GUILayout.Button("Mở Package Manager"))
                {
                    EditorApplication.ExecuteMenuItem("Window/Package Management/Package Manager");
                }
            }

            EndStep();
        }

        // ---------- Bước 2 ----------
        private void Step2Samples()
        {
            bool all = _sampleImported.All(x => x);

            StepBox("Bước 2 — Import môi trường", all,
                "Mỗi môi trường là một Sample của gói: scene, prefab, material và các "
                + "thiết lập vật lý. Import xong chúng nằm trong Assets/Samples/ và bạn "
                + "sửa được thoải mái mà không đụng tới gói gốc.");

            for (int i = 0; i < SampleNames.Length; i++)
            {
                EditorGUILayout.BeginHorizontal();
                EditorGUILayout.LabelField(
                    (_sampleImported[i] ? "✓ " : "   ") + SampleNames[i],
                    GUILayout.Width(200));

                using (new EditorGUI.DisabledScope(!_sampleImported[i]))
                {
                    if (GUILayout.Button("Mở scene", GUILayout.Width(90)))
                    {
                        string path = FindSceneAsset(SceneNames[i]);
                        if (!string.IsNullOrEmpty(path))
                        {
                            EditorSceneManager.SaveCurrentModifiedScenesIfUserWantsTo();
                            EditorSceneManager.OpenScene(path);
                        }
                    }
                }

                EditorGUILayout.EndHorizontal();
            }

            if (!all && GUILayout.Button("Mở Package Manager để import Samples"))
            {
                EditorApplication.ExecuteMenuItem("Window/Package Management/Package Manager");
            }

            EndStep();
        }

        // ---------- Bước 3 ----------
        private void Step3ThirdPartyArt()
        {
            bool ok = _missingArt.Length == 0;

            StepBox("Bước 3 — Art bên thứ ba (tuỳ chọn)", ok,
                "Cross The Road dùng vài gói art miễn phí trên Asset Store. Giấy phép "
                + "Asset Store không cho phép phát hành lại nên gói này không kèm theo "
                + "chúng. Thiếu art thì môi trường VẪN CHẠY và huấn luyện bình thường, "
                + "chỉ là xe và nhân vật không có hình.");

            if (!ok)
            {
                EditorGUILayout.LabelField("Chưa thấy: " + string.Join(", ", _missingArt),
                    EditorStyles.wordWrappedMiniLabel);

                foreach (var art in ThirdPartyArt.Where(a => _missingArt.Contains(a.label)))
                {
                    if (GUILayout.Button("Mở trang tải: " + art.label))
                    {
                        Application.OpenURL(art.url);
                    }
                }
            }

            EndStep();
        }

        // ---------- Bước 4 ----------
        private void Step4TrainingConfigs()
        {
            StepBox("Bước 4 — Cấu hình huấn luyện", _configsInstalled,
                "Chép 15 tệp YAML (PPO / SAC / MA-POCA / MAPPO / DQN × 3 môi trường) ra "
                + "thư mục config/ ở gốc dự án để dùng với mlagents-learn. MAPPO và DQN "
                + "cần plugin trainer riêng, xem tài liệu đi kèm gói.");

            using (new EditorGUI.DisabledScope(_configsInstalled))
            {
                if (GUILayout.Button("Chép cấu hình vào config/"))
                {
                    TrainingConfigInstaller.Install();
                    Refresh();
                }
            }

            if (_configsInstalled && GUILayout.Button("Mở thư mục config/"))
            {
                EditorUtility.RevealInFinder(ConfigTargetDir);
            }

            EndStep();
        }

        // ---------- Bước 5 ----------
        private void Step5Multiply()
        {
            StepBox("Bước 5 — Nhân khu vực huấn luyện", false,
                "Nhân bản khu vực của scene đang mở thành nhiều bản chạy song song. "
                + "Đây là đòn bẩy tốc độ lớn nhất (4–8×) và không đổi gì về thuật toán. "
                + "Lưu ý: mọi thuật toán so sánh với nhau phải dùng CÙNG số khu vực.");

            if (GUILayout.Button("Mở công cụ nhân khu vực…"))
            {
                EditorApplication.ExecuteMenuItem("Tools/Training/Multiply Areas…");
            }

            EndStep();
        }

        // ---------- Bước 6 ----------
        private void Step6Build()
        {
            StepBox("Bước 6 — Build môi trường headless", false,
                "Huấn luyện nhanh hơn nhiều khi chạy trên bản build không đồ hoạ thay vì "
                + "bấm Play trong Editor, và chỉ khi có build thì mới dùng được nhiều "
                + "tiến trình song song (--num-envs).");

            if (GUILayout.Button("Build các môi trường huấn luyện"))
            {
                EditorApplication.ExecuteMenuItem("Tools/Training/Build Training Envs");
            }

            EndStep();
        }

        // ---------- Bước 7 ----------
        private void Step7Train()
        {
            StepBox("Bước 7 — Chạy huấn luyện", false,
                "Lệnh mẫu (chạy trong môi trường Python đã cài mlagents). Bấm nút để "
                + "chép vào clipboard rồi dán sang terminal.");

            DrawCommand("PPO trên Cross The Road",
                "mlagents-learn config/ctr_ppo.yaml --run-id=ctr_ppo_01 "
                + "--env=Builds/CrossTheRoad/CrossTheRoad.exe --no-graphics");

            DrawCommand("Xem biểu đồ",
                "tensorboard --logdir results");

            EndStep();
        }

        private static void DrawCommand(string label, string command)
        {
            EditorGUILayout.LabelField(label, EditorStyles.miniBoldLabel);
            EditorGUILayout.BeginHorizontal();
            EditorGUILayout.SelectableLabel(command,
                EditorStyles.textField, GUILayout.Height(18));

            if (GUILayout.Button("Chép", GUILayout.Width(50)))
            {
                EditorGUIUtility.systemCopyBuffer = command;
            }

            EditorGUILayout.EndHorizontal();
        }
    }
}
