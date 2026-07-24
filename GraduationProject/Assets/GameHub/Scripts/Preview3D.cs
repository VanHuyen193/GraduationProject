using System.Collections.Generic;
using UnityEngine;

namespace GameHub
{
    /// <summary>
    /// Xem trước môi trường dạng 3D tương tác: dựng lại hình khối của prefab môi
    /// trường (chỉ sao chép mesh + vật liệu, bỏ mọi script/vật lý nên KHÔNG chạy mô
    /// phỏng), render bằng camera riêng ra RenderTexture. Kéo để xoay, lăn để zoom.
    /// Sân khấu đặt xa khu vực menu để không lẫn với cảnh khác.
    /// </summary>
    public class Preview3D : MonoBehaviour
    {
        private Camera cam;
        private Transform content;
        private RenderTexture rt;

        private float yaw = 35f;
        private float pitch = 22f;
        private float distance = 10f;
        private Vector3 pivot;
        private bool userInteracted;
        private float autoSpin = 12f;

        private readonly Dictionary<string, Transform> cache =
            new Dictionary<string, Transform>();
        private readonly Dictionary<string, Vector3> pivotCache =
            new Dictionary<string, Vector3>();
        private readonly Dictionary<string, float> distCache =
            new Dictionary<string, float>();

        private string current;
        private Shader unlitShader;

        public RenderTexture Texture => rt;

        public void Init(int w, int h, Vector3 origin, Color bg)
        {
            unlitShader = Shader.Find("Unlit/Color");
            transform.position = origin;

            content = new GameObject("Content").transform;
            content.SetParent(transform, false);

            var keyGo = new GameObject("Key");
            keyGo.transform.SetParent(transform, false);
            var key = keyGo.AddComponent<Light>();
            key.type = LightType.Directional;
            key.intensity = 1.1f;
            key.transform.rotation = Quaternion.Euler(45f, -40f, 0f);

            var fillGo = new GameObject("Fill");
            fillGo.transform.SetParent(transform, false);
            var fill = fillGo.AddComponent<Light>();
            fill.type = LightType.Directional;
            fill.intensity = 0.5f;
            fill.transform.rotation = Quaternion.Euler(20f, 150f, 0f);

            var camGo = new GameObject("Cam");
            camGo.transform.SetParent(transform, false);
            cam = camGo.AddComponent<Camera>();
            cam.clearFlags = CameraClearFlags.SolidColor;
            cam.backgroundColor = bg;
            cam.fieldOfView = 34f;
            cam.nearClipPlane = 0.05f;
            cam.farClipPlane = 500f;

            rt = new RenderTexture(w, h, 24, RenderTextureFormat.ARGB32)
            {
                antiAliasing = 4
            };
            rt.Create();
            cam.targetTexture = rt;

            UpdateCamera();
        }

        public void SetRendering(bool on)
        {
            if (cam != null)
            {
                cam.enabled = on;
            }
        }

        public void ResetView()
        {
            yaw = 35f;
            pitch = 22f;
            userInteracted = false;
            UpdateCamera();
        }

        public void Orbit(Vector2 delta)
        {
            userInteracted = true;
            yaw += delta.x * 0.3f;
            pitch = Mathf.Clamp(pitch - delta.y * 0.3f, 4f, 82f);
            UpdateCamera();
        }

        public void Zoom(float amount)
        {
            distance = Mathf.Clamp(distance - amount * distance * 0.08f, 2f, 200f);
            UpdateCamera();
        }

        /// <summary>Hiển thị môi trường theo key (đồng thời là tên prefab trong Resources/EnvPrefabs).</summary>
        public void Show(string key)
        {
            if (current == key)
            {
                ResetView();
                return;
            }

            if (current != null && cache.TryGetValue(current, out Transform prevT) && prevT != null)
            {
                prevT.gameObject.SetActive(false);
            }

            current = key;

            if (!cache.TryGetValue(key, out Transform holderT) || holderT == null)
            {
                holderT = Build(key);
                cache[key] = holderT;
            }

            holderT.gameObject.SetActive(true);
            pivot = pivotCache[key];
            distance = distCache[key];
            ResetView();
        }

        private Transform Build(string key)
        {
            var holder = new GameObject(key);
            holder.transform.SetParent(content, false);
            holder.SetActive(false);

            GameObject prefab = Resources.Load<GameObject>("EnvPrefabs/" + key);
            if (prefab == null)
            {
                var cube = GameObject.CreatePrimitive(PrimitiveType.Cube);
                cube.transform.SetParent(holder.transform, false);
                FrameFromBounds(key, holder);
                holder.SetActive(false);
                return holder.transform;
            }

            // Tạo bản sao ẩn (parent inactive nên Awake KHÔNG chạy), copy mesh rồi bỏ.
            GameObject inst = Instantiate(prefab, holder.transform);

            var filters = inst.GetComponentsInChildren<MeshFilter>(true);
            foreach (MeshFilter mf in filters)
            {
                if (mf.sharedMesh == null || !mf.gameObject.activeSelf)
                {
                    continue;
                }

                var mr = mf.GetComponent<MeshRenderer>();
                if (mr == null || !mr.enabled)
                {
                    continue;
                }

                var g = new GameObject(mf.name);
                g.transform.SetParent(holder.transform, false);
                g.transform.SetPositionAndRotation(
                    mf.transform.position, mf.transform.rotation);
                g.transform.localScale = mf.transform.lossyScale;

                g.AddComponent<MeshFilter>().sharedMesh = mf.sharedMesh;
                var nmr = g.AddComponent<MeshRenderer>();
                nmr.sharedMaterials = mr.sharedMaterials;
            }

            DestroyImmediate(inst);

            FrameFromBounds(key, holder);
            holder.SetActive(false);
            return holder.transform;
        }

        private void FrameFromBounds(string key, GameObject holder)
        {
            var renderers = holder.GetComponentsInChildren<MeshRenderer>(true);
            Vector3 center;
            float radius;

            if (renderers.Length == 0)
            {
                center = holder.transform.position;
                radius = 1f;
            }
            else
            {
                Bounds b = renderers[0].bounds;
                foreach (MeshRenderer r in renderers)
                {
                    b.Encapsulate(r.bounds);
                }
                center = b.center;
                radius = Mathf.Max(0.5f, b.extents.magnitude);
            }

            pivotCache[key] = content.InverseTransformPoint(center);
            distCache[key] = radius * 2.4f;
        }

        private void UpdateCamera()
        {
            if (cam == null)
            {
                return;
            }

            Vector3 worldPivot = content.TransformPoint(pivot);
            Quaternion rot = Quaternion.Euler(pitch, yaw, 0f);
            Vector3 dir = rot * Vector3.back;
            cam.transform.position = worldPivot + dir * distance;
            cam.transform.rotation = Quaternion.LookRotation(
                worldPivot - cam.transform.position, Vector3.up);
        }

        private void LateUpdate()
        {
            if (!userInteracted && cam != null && cam.enabled)
            {
                yaw += autoSpin * Time.unscaledDeltaTime;
                UpdateCamera();
            }
        }

        private void OnDestroy()
        {
            if (rt != null)
            {
                rt.Release();
            }
        }
    }
}
