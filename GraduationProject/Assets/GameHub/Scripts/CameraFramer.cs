using System.Collections;
using UnityEngine;

namespace GameHub
{
    /// <summary>
    /// Đưa camera chính về khung nhìn bao trọn các khu vực được chỉ định.
    /// Chờ hết frame đầu tiên rồi mới tính bounds, vì tại thời điểm sceneLoaded
    /// một số object (xe, target...) chưa được reset về đúng vị trí.
    /// </summary>
    public class CameraFramer : MonoBehaviour
    {
        private GameObject[] areas;

        public static void FrameWhenReady(GameObject[] areas)
        {
            var go = new GameObject("GameHubCameraFramer");
            var framer = go.AddComponent<CameraFramer>();
            framer.areas = areas;
        }

        private void Start()
        {
            StartCoroutine(FrameRoutine());
        }

        private IEnumerator FrameRoutine()
        {
            // Chờ hết frame đầu để mọi object về đúng vị trí episode
            yield return new WaitForEndOfFrame();
            yield return new WaitForFixedUpdate();

            Frame(areas);
            Destroy(gameObject);
        }

        private static void Frame(GameObject[] areas)
        {
            Camera camera = Camera.main;

            if (camera == null || areas == null || areas.Length == 0)
            {
                return;
            }

            Bounds bounds = default;
            bool hasBounds = false;

            foreach (GameObject area in areas)
            {
                if (area == null)
                {
                    continue;
                }

                foreach (Renderer renderer in
                    area.GetComponentsInChildren<Renderer>())
                {
                    if (!hasBounds)
                    {
                        bounds = renderer.bounds;
                        hasBounds = true;
                    }
                    else
                    {
                        bounds.Encapsulate(renderer.bounds);
                    }
                }
            }

            if (!hasBounds)
            {
                return;
            }

            float radius = bounds.extents.magnitude;

            // Đặt camera trên trục nhìn đi qua tâm vùng chơi
            camera.transform.position =
                bounds.center - camera.transform.forward * (radius * 2.2f);

            if (camera.orthographic)
            {
                // Chiếu 8 góc bounds lên trục ngang/dọc của camera
                // để tính orthographicSize vừa khít
                Transform t = camera.transform;
                float halfWidth = 0f;
                float halfHeight = 0f;

                for (int i = 0; i < 8; i++)
                {
                    Vector3 corner = bounds.center + Vector3.Scale(
                        bounds.extents,
                        new Vector3(
                            (i & 1) == 0 ? 1 : -1,
                            (i & 2) == 0 ? 1 : -1,
                            (i & 4) == 0 ? 1 : -1));

                    Vector3 local = corner - bounds.center;

                    halfWidth = Mathf.Max(
                        halfWidth, Mathf.Abs(Vector3.Dot(local, t.right)));

                    halfHeight = Mathf.Max(
                        halfHeight, Mathf.Abs(Vector3.Dot(local, t.up)));
                }

                camera.orthographicSize = Mathf.Max(
                    halfHeight, halfWidth / camera.aspect) * 1.08f;
            }
        }
    }
}
