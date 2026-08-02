using Unity.MLAgents.Actuators;
using UnityEngine;
using VanHuyen.RLGameEnvs;

namespace TableFootball
{
    /// <summary>
    /// Điều khiển bàn bi lắc bằng bàn phím cho chế độ người chơi.
    /// Q/E hoặc phím 1-4: chọn thanh | W/S: trượt thanh | A/D: xoay (sút).
    /// FootballAgent.Heuristic sẽ đọc action từ component này.
    /// </summary>
    public class FootballHumanInput : MonoBehaviour, IManualActionSource
    {
        // Đệm 8 giá trị liên tục trước khi giao cho ManualActionSource.Write
        private readonly float[] buffer = new float[8];

        // Team mà người chơi điều khiển (gán runtime bởi GameModeApplier)
        public Team team;

        private int selectedRod;

        private static readonly string[] rodNames =
        {
            "Thủ môn", "Hậu vệ", "Tiền vệ", "Tiền đạo"
        };

        public int SelectedRod => selectedRod;

        public string SelectedRodName =>
            selectedRod < rodNames.Length ? rodNames[selectedRod] : ("Thanh " + (selectedRod + 1));

        private int RodCount =>
            team != null && team.Positions != null ? team.Positions.Count : 4;

        private void Update()
        {
            // Chọn thanh trực tiếp bằng phím số
            for (int i = 0; i < RodCount && i < 4; i++)
            {
                if (Input.GetKeyDown(KeyCode.Alpha1 + i))
                {
                    selectedRod = i;
                }
            }

            // Chuyển thanh bằng Q / E
            if (Input.GetKeyDown(KeyCode.Q))
            {
                selectedRod = (selectedRod + RodCount - 1) % RodCount;
            }
            else if (Input.GetKeyDown(KeyCode.E))
            {
                selectedRod = (selectedRod + 1) % RodCount;
            }
        }

        /// <summary>
        /// Ghi action liên tục (8 giá trị: [trượt, xoay] x 4 thanh) cho thanh đang chọn.
        /// </summary>
        public void WriteActions(ActionSegment<float> actions)
        {
            for (int i = 0; i < actions.Length; i++)
            {
                actions[i] = 0f;
            }

            float slide = 0f;
            if (Input.GetKey(KeyCode.W)) slide = 1f;
            else if (Input.GetKey(KeyCode.S)) slide = -1f;

            float spin = 0f;
            if (Input.GetKey(KeyCode.D)) spin = 1f;
            else if (Input.GetKey(KeyCode.A)) spin = -1f;

            float sign = team != null ? team.Sign : 1f;

            int moveIndex = selectedRod * 2;
            int spinIndex = moveIndex + 1;

            if (spinIndex < actions.Length)
            {
                actions[moveIndex] = slide * sign;
                actions[spinIndex] = spin * sign;
            }
        }

        /// <summary>
        /// Ghi hành động cho môi trường (IManualActionSource). Luôn sinh ra 8 giá
        /// trị liên tục; nếu brain đang ở chế độ rời rạc thì helper của gói môi
        /// trường tự lượng tử hoá về ba mức.
        /// </summary>
        public void WriteActions(in ActionBuffers actionsOut)
        {
            WriteActions(new ActionSegment<float>(buffer));
            ManualActionSource.Write(actionsOut, buffer);
        }
    }
}
