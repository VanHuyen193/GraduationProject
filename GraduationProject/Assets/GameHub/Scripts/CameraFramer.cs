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

            // Chiếu 8 đỉnh hộp bao lên ba trục của camera: dùng chung cho cả hai
            // kiểu chiếu, thay vì lấy bán kính hình cầu (quá rộng với vùng chơi
            // dài và dẹt như bàn bi lắc).
            Transform t = camera.transform;
            float halfWidth = 0f;
            float halfHeight = 0f;
            float halfDepth = 0f;

            for (int i = 0; i < 8; i++)
            {
                Vector3 local = Vector3.Scale(
                    bounds.extents,
                    new Vector3(
                        (i & 1) == 0 ? 1 : -1,
                        (i & 2) == 0 ? 1 : -1,
                        (i & 4) == 0 ? 1 : -1));

                halfWidth = Mathf.Max(
                    halfWidth, Mathf.Abs(Vector3.Dot(local, t.right)));

                halfHeight = Mathf.Max(
                    halfHeight, Mathf.Abs(Vector3.Dot(local, t.up)));

                halfDepth = Mathf.Max(
                    halfDepth, Mathf.Abs(Vector3.Dot(local, t.forward)));
            }

            const float margin = 1.08f;

            if (camera.orthographic)
            {
                camera.transform.position = bounds.center
                    - t.forward * (halfDepth + bounds.extents.magnitude);

                camera.orthographicSize = Mathf.Max(
                    halfHeight, halfWidth / camera.aspect) * margin;
            }
            else
            {
                // Khoảng cách đủ để nửa chiều cao/rộng nằm trong góc nhìn
                float tanV = Mathf.Tan(camera.fieldOfView * 0.5f * Mathf.Deg2Rad);
                float tanH = tanV * camera.aspect;

                float distance = Mathf.Max(halfHeight / tanV, halfWidth / tanH)
                    * margin + halfDepth;

                camera.transform.position = bounds.center - t.forward * distance;
            }
        }
    }
}
