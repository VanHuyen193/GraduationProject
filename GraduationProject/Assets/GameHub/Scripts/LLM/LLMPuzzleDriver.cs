using System.Linq;
using System.Text;
using Unity.MLAgents.Actuators;
using UnityEngine;
using VanHuyen.RLGameEnvs;

namespace GameHub
{
    /// <summary>
    /// LLM điều khiển 1 PuzzleAgent trong Capture The Flag (phối hợp với
    /// agent RL còn lại): mô tả vị trí 2 agent, nút bấm, checkpoint;
    /// LLM chọn 1 trong 7 action. Action được giữ nguyên giữa 2 lần trả lời
    /// (di chuyển bằng lực nên cần bấm giữ như người chơi).
    /// </summary>
    public class LLMPuzzleDriver : LLMDriverBase, IManualActionSource
    {
        private PuzzleAgent agent;
        private PuzzleAgent teammate;
        private Transform[] checkpoints;

        private int currentAction;

        private static readonly string[] ActionNames =
        {
            "đứng yên", "tiến", "lùi", "xoay phải", "xoay trái",
            "ngang trái", "ngang phải"
        };

        private void Awake()
        {
            requestInterval = 1.5f;

            agent = GetComponent<PuzzleAgent>();

            teammate = FindObjectsByType<PuzzleAgent>(FindObjectsSortMode.None)
                .FirstOrDefault(a => a != agent);

            checkpoints = FindObjectsByType<DetectTrigger>(FindObjectsSortMode.None)
                .Where(t => t.IsCheckpoint)
                .Select(t => t.transform)
                .ToArray();
        }

        protected override string SystemPrompt =>
            "You control a robot in a cooperative puzzle. Your teammate is "
            + "controlled by another AI. Both robots must stand on pressure "
            + "plates to open doors, then BOTH must reach the checkpoint. "
            + "You move by continuous force relative to your facing direction "
            + "(yaw in degrees, 0 = +z axis). "
            + "Actions: 0 = idle, 1 = move forward, 2 = move backward, "
            + "3 = rotate right, 4 = rotate left, 5 = strafe left, "
            + "6 = strafe right. The action repeats until your next reply, "
            + "so pick the action to hold for about 1.5 seconds. "
            + "Reply with ONLY one digit 0-6.";

        protected override string BuildUserPrompt()
        {
            var sb = new StringBuilder();

            AppendPosition(sb, "You", agent.transform);
            sb.Append(" yaw=").Append(
                agent.transform.eulerAngles.y.ToString("F0")).Append("deg.");

            if (teammate != null)
            {
                AppendPosition(sb, " Teammate", teammate.transform);
                sb.Append('.');
            }

            // Có thể chưa được PuzzleAgent.Initialize() gán ở lượt hỏi đầu tiên
            GameObject[] plates =
                agent.pressurePlates ?? System.Array.Empty<GameObject>();

            for (int i = 0; i < plates.Length; i++)
            {
                AppendPosition(sb, " Plate" + (i + 1), plates[i].transform);
                sb.Append(plates[i].GetComponent<OpenDoor>().isPressed
                    ? " (pressed, door open)"
                    : " (not pressed, door closed)");
                sb.Append('.');
            }

            foreach (Transform checkpoint in checkpoints)
            {
                AppendPosition(sb, " Checkpoint", checkpoint);
                sb.Append('.');
            }

            sb.Append(" You reached checkpoint: ")
              .Append(agent.FoundCheckpoint ? "yes" : "no");

            if (teammate != null)
            {
                sb.Append(". Teammate reached: ")
                  .Append(teammate.FoundCheckpoint ? "yes" : "no");
            }

            sb.Append(". Which action (0-6)?");

            return sb.ToString();
        }

        private static void AppendPosition(
            StringBuilder sb, string label, Transform t)
        {
            Vector3 p = t.position;

            sb.Append(label)
              .Append(": x=").Append(p.x.ToString("F1"))
              .Append(", z=").Append(p.z.ToString("F1"));
        }

        protected override bool TryParseReply(string reply)
        {
            var ints = ExtractInts(reply);

            for (int i = ints.Count - 1; i >= 0; i--)
            {
                if (ints[i] >= 0 && ints[i] <= 6)
                {
                    currentAction = ints[i];
                    StatusLine = "LLM: " + ActionNames[currentAction]
                        + "  (lượt " + (ReplyCount + 1) + ")";
                    return true;
                }
            }

            return false;
        }

        /// <summary>Agent đọc trong Heuristic; action được giữ tới lượt sau.</summary>
        public int CurrentAction => currentAction;

        /// <summary>Ghi hành động cho môi trường (IManualActionSource).</summary>
        public void WriteActions(in ActionBuffers actionsOut)
        {
            // ActionSegment là struct bọc mảng: gán qua biến cục bộ vẫn
            // ghi vào đúng mảng gốc.
            var discrete = actionsOut.DiscreteActions;
            discrete[0] = CurrentAction;
        }
    }
}
