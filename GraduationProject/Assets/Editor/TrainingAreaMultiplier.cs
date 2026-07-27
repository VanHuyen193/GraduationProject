using System.Collections.Generic;
using System.Linq;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.SceneManagement;

namespace GraduationProject.EditorTools
{
    /// <summary>
    /// Nhân bản training area của scene đang mở thành một lưới N bản sao để tăng
    /// tốc thu thập kinh nghiệm khi huấn luyện.
    ///
    /// Vì sao cần: mỗi scene hiện chỉ có ĐÚNG MỘT area, nên mỗi bước mô phỏng chỉ
    /// sinh ra một mẩu kinh nghiệm. Nhân lên 8 bản cho throughput gấp nhiều lần mà
    /// không đổi bất kỳ thứ gì về mặt thuật toán — miễn là mọi thuật toán trên cùng
    /// một môi trường đều dùng cùng số area (nếu không thì so sánh mất công bằng).
    ///
    /// Bản sao được đặt dưới một GameObject cha tên _TrainingAreas nên gỡ bỏ chỉ là
    /// xoá đúng một object; area gốc luôn được giữ nguyên tại chỗ.
    ///
    /// Dùng: menu  Tools ▸ Training ▸ Multiply Areas…
    /// Hoặc batch mode:  -executeMethod GraduationProject.EditorTools.TrainingAreaMultiplier.BuildAllFromCommandLine
    /// </summary>
    public class TrainingAreaMultiplier : EditorWindow
    {
        private const string ContainerName = "_TrainingAreas";

        // Tên object gốc của area trong từng scene. Khớp theo thứ tự ưu tiên.
        private static readonly string[] AreaNameHints =
        {
            "CrossTheRoadArea", "TrainingArea", "FirstStageArea", "Table", "Area"
        };

        private int _count = 8;
        private int _columns = 4;
        private float _padding = 0.15f;   // khoảng hở giữa các area, theo tỉ lệ bề rộng
        private GameObject _explicitRoot;

        [MenuItem("Tools/Training/Multiply Areas…")]
        public static void Open()
        {
            GetWindow<TrainingAreaMultiplier>(true, "Multiply Training Areas");
        }

        private void OnGUI()
        {
            EditorGUILayout.HelpBox(
                "Nhân bản training area của scene đang mở thành một lưới.\n" +
                "Chạy lại sẽ thay thế các bản sao cũ, không cộng dồn.",
                MessageType.Info);

            _explicitRoot = (GameObject)EditorGUILayout.ObjectField(
                new GUIContent("Area gốc", "Bỏ trống để tự dò theo tên"),
                _explicitRoot, typeof(GameObject), true);

            _count = Mathf.Max(1, EditorGUILayout.IntField("Tổng số area", _count));
            _columns = Mathf.Max(1, EditorGUILayout.IntField("Số cột", _columns));
            _padding = EditorGUILayout.Slider("Khoảng hở", _padding, 0f, 1f);

            EditorGUILayout.Space();
            if (GUILayout.Button($"Nhân thành {_count} area", GUILayout.Height(30)))
            {
                Multiply(_explicitRoot, _count, _columns, _padding);
            }
            if (GUILayout.Button("Gỡ bản sao, quay lại 1 area"))
            {
                ResetToSingle();
            }
        }

        // ─────────────────────────────────────────────────────────────────────
        public static GameObject FindAreaRoot()
        {
            var scene = SceneManager.GetActiveScene();
            var roots = scene.GetRootGameObjects();

            // bản sao cũ nằm trong container -> area gốc là object còn lại
            foreach (var hint in AreaNameHints)
            {
                var hit = roots.FirstOrDefault(
                    g => g.name != ContainerName &&
                         g.name.Replace(" ", "").StartsWith(hint, System.StringComparison.OrdinalIgnoreCase));
                if (hit != null) return hit;
            }

            // dự phòng: object gốc chứa nhiều Agent nhất
            return roots
                .Where(g => g.name != ContainerName)
                .OrderByDescending(g => g.GetComponentsInChildren<Unity.MLAgents.Agent>(true).Length)
                .FirstOrDefault(g => g.GetComponentsInChildren<Unity.MLAgents.Agent>(true).Length > 0);
        }

        public static int Multiply(GameObject explicitRoot, int count, int columns, float padding)
        {
            var area = explicitRoot != null ? explicitRoot : FindAreaRoot();
            if (area == null)
            {
                Debug.LogError("[AreaMultiplier] Không tìm thấy training area trong scene đang mở.");
                return 0;
            }

            var scene = SceneManager.GetActiveScene();
            RemoveContainer(scene);

            if (count <= 1)
            {
                Debug.Log($"[AreaMultiplier] {scene.name}: giữ nguyên 1 area ({area.name}).");
                EditorSceneManager.MarkSceneDirty(scene);
                return 1;
            }

            var size = MeasureWorldSize(area);
            var stepX = size.x * (1f + padding);
            var stepZ = size.z * (1f + padding);
            if (stepX < 0.01f) stepX = 10f;
            if (stepZ < 0.01f) stepZ = 10f;

            var container = new GameObject(ContainerName);
            Undo.RegisterCreatedObjectUndo(container, "Multiply Training Areas");
            SceneManager.MoveGameObjectToScene(container, scene);

            var origin = area.transform.position;
            for (int i = 1; i < count; i++)
            {
                int row = i / columns;
                int col = i % columns;

                var copy = (GameObject)PrefabUtility.InstantiatePrefab(
                    PrefabUtility.GetCorrespondingObjectFromSource(area) ?? area, scene);
                if (copy == null) copy = Object.Instantiate(area);

                copy.name = $"{area.name}_{i:D2}";
                copy.transform.SetParent(container.transform, true);
                copy.transform.position = origin + new Vector3(col * stepX, 0f, row * stepZ);
                copy.transform.rotation = area.transform.rotation;
                copy.SetActive(true);
                Undo.RegisterCreatedObjectUndo(copy, "Multiply Training Areas");
            }

            EditorSceneManager.MarkSceneDirty(scene);
            Debug.Log($"[AreaMultiplier] {scene.name}: {count} area " +
                      $"(gốc '{area.name}' + {count - 1} bản sao), bước lưới {stepX:F1} x {stepZ:F1}.");
            return count;
        }

        public static void ResetToSingle()
        {
            var scene = SceneManager.GetActiveScene();
            RemoveContainer(scene);
            EditorSceneManager.MarkSceneDirty(scene);
            Debug.Log($"[AreaMultiplier] {scene.name}: đã gỡ bản sao, còn 1 area.");
        }

        private static void RemoveContainer(Scene scene)
        {
            var old = scene.GetRootGameObjects().FirstOrDefault(g => g.name == ContainerName);
            if (old != null) Undo.DestroyObjectImmediate(old);
        }

        /// <summary>Kích thước thế giới của area, gộp mọi Renderer và Collider con.</summary>
        private static Vector3 MeasureWorldSize(GameObject area)
        {
            var has = false;
            var bounds = new Bounds(area.transform.position, Vector3.zero);

            foreach (var r in area.GetComponentsInChildren<Renderer>(true))
            {
                if (!has) { bounds = r.bounds; has = true; }
                else bounds.Encapsulate(r.bounds);
            }
            foreach (var c in area.GetComponentsInChildren<Collider>(true))
            {
                if (!has) { bounds = c.bounds; has = true; }
                else bounds.Encapsulate(c.bounds);
            }
            return has ? bounds.size : new Vector3(10f, 0f, 10f);
        }

        // ─────────────────────────────────────────────────────────────────────
        // Batch mode: mở từng scene, nhân area, lưu lại.
        //   -executeMethod GraduationProject.EditorTools.TrainingAreaMultiplier.BuildAllFromCommandLine
        //   -areaCount 8
        // ─────────────────────────────────────────────────────────────────────
        private static readonly string[] TrainingScenes =
        {
            "Assets/CrossTheRoad/Scenes/CrossTheRoad.unity",
            "Assets/Collaboration/Scenes/CaptureTheFlag.unity",
            "Assets/Football/Football.unity",
        };

        public static void BuildAllFromCommandLine()
        {
            int count = 8, columns = 4;
            var argv = System.Environment.GetCommandLineArgs();
            for (int i = 0; i < argv.Length - 1; i++)
            {
                if (argv[i] == "-areaCount") int.TryParse(argv[i + 1], out count);
                if (argv[i] == "-areaColumns") int.TryParse(argv[i + 1], out columns);
            }

            var failed = new List<string>();
            foreach (var path in TrainingScenes)
            {
                try
                {
                    var scene = EditorSceneManager.OpenScene(path, OpenSceneMode.Single);
                    var made = Multiply(null, count, columns, 0.15f);
                    if (made == 0) { failed.Add(path); continue; }
                    EditorSceneManager.SaveScene(scene);
                    Debug.Log($"[AreaMultiplier] Đã lưu {path} với {made} area.");
                }
                catch (System.Exception e)
                {
                    Debug.LogError($"[AreaMultiplier] Lỗi ở {path}: {e.Message}");
                    failed.Add(path);
                }
            }

            if (failed.Count > 0)
            {
                Debug.LogError("[AreaMultiplier] Thất bại: " + string.Join(", ", failed));
                EditorApplication.Exit(1);
            }
            EditorApplication.Exit(0);
        }
    }
}
