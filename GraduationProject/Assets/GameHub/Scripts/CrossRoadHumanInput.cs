using UnityEngine;

namespace GameHub
{
    /// <summary>
    /// Đệm input bàn phím cho CrossTheRoadAgent ở chế độ người chơi.
    /// Bắt phím trong Update (không bị mất phím như GetKeyDown trong Heuristic)
    /// rồi Heuristic tiêu thụ ở lần quyết định kế tiếp.
    /// </summary>
    public class CrossRoadHumanInput : MonoBehaviour
    {
        // 0 = đứng yên, 1 = trái, 2 = phải, 3 = tiến
        private int pendingAction;

        private void Update()
        {
            if (Input.GetKeyDown(KeyCode.LeftArrow) || Input.GetKeyDown(KeyCode.A))
            {
                pendingAction = 1;
            }
            else if (Input.GetKeyDown(KeyCode.RightArrow) || Input.GetKeyDown(KeyCode.D))
            {
                pendingAction = 2;
            }
            else if (Input.GetKeyDown(KeyCode.UpArrow) || Input.GetKeyDown(KeyCode.W))
            {
                pendingAction = 3;
            }
        }

        /// <summary>Lấy action đang chờ và xoá đệm.</summary>
        public int Consume()
        {
            int action = pendingAction;
            pendingAction = 0;
            return action;
        }
    }
}
