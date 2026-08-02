using System.Text;
using TableFootball;
using Unity.MLAgents.Actuators;
using UnityEngine;
using VanHuyen.RLGameEnvs;

namespace GameHub
{
    /// <summary>
    /// LLM điều khiển 1 đội bi lắc: mô tả bóng + 4 thanh, LLM trả về 8 số
    /// {-1,0,1} = [trượt, xoay] cho 4 thanh. Bộ 8 số được giữ nguyên
    /// (như bấm giữ phím) tới lần trả lời kế tiếp.
    /// Tọa độ/hành động được chuẩn hoá theo Team.Sign giống FootballHumanInput,
    /// nên LLM luôn "nhìn" sân theo một hướng cố định.
    /// </summary>
    public class LLMFootballDriver : LLMDriverBase, IManualActionSource
    {
        // Đệm 8 giá trị liên tục trước khi giao cho ManualActionSource.Write
        private readonly float[] buffer = new float[8];

        [HideInInspector]
        public Team team;

        [HideInInspector]
        public Ball ball;

        private readonly float[] actions = new float[8];

        private static readonly string[] RodNames =
        {
            "goalkeeper", "defender", "midfielder", "attacker"
        };

        private void Awake()
        {
            requestInterval = 1.2f;
        }

        protected override string SystemPrompt =>
            "You play table football (foosball) controlling 4 rods: "
            + "1 goalkeeper, 2 defender, 3 midfielder, 4 attacker. "
            + "All values are normalized to [-1, 1]. Positive ball vy means "
            + "the ball moves toward the OPPONENT goal; negative vy means it "
            + "comes toward YOUR goal. Rod pos is sideways position; "
            + "angle is rotation (0 = players vertical, able to block). "
            + "For each rod give 2 commands held until your next reply: "
            + "slide (-1 = one way, 0 = hold, +1 = other way, moves the rod "
            + "sideways to align with the ball x) and spin "
            + "(-1/0/+1, spin to kick the ball forward; keep 0 to block). "
            + "Defend when the ball comes to you, kick when it is near your rod. "
            + "Reply with ONLY 8 integers as a JSON array: "
            + "[gk_slide, gk_spin, def_slide, def_spin, mid_slide, mid_spin, "
            + "att_slide, att_spin].";

        protected override string BuildUserPrompt()
        {
            float sign = team.Sign;
            var sb = new StringBuilder();

            Vector2 ballPos = ball.GetNormalizedPosition2D() * sign;
            Vector2 ballVel = ball.GetNormalizedVelocity2D() * sign;

            sb.Append("Ball: x=").Append(ballPos.x.ToString("F2"))
              .Append(", y=").Append(ballPos.y.ToString("F2"))
              .Append(", vx=").Append(ballVel.x.ToString("F2"))
              .Append(", vy=").Append(ballVel.y.ToString("F2"))
              .Append(". Your rods:");

            for (int i = 0; i < team.Positions.Count; i++)
            {
                PlayerPosition rod = team.Positions[i];

                sb.Append(' ')
                  .Append(i + 1).Append('=')
                  .Append(i < RodNames.Length ? RodNames[i] : "rod")
                  .Append("[pos=").Append(rod.GetNormalizedPosition().ToString("F2"))
                  .Append(", angle=").Append(rod.GetNormalizedAngle().ToString("F2"))
                  .Append(']');
            }

            sb.Append(". Your 8 commands?");

            return sb.ToString();
        }

        protected override bool TryParseReply(string reply)
        {
            var ints = ExtractInts(reply);

            // Tên thanh trong prompt có số (1-4) nên chỉ lấy 8 số CUỐI CÙNG
            if (ints.Count < actions.Length)
            {
                return false;
            }

            int start = ints.Count - actions.Length;

            for (int i = 0; i < actions.Length; i++)
            {
                actions[i] = Mathf.Clamp(ints[start + i], -1, 1);
            }

            StatusLine = "LLM: ["
                + string.Join(", ", System.Array.ConvertAll(
                    actions, a => ((int)a).ToString()))
                + "]  (lượt " + (ReplyCount + 1) + ")";

            return true;
        }

        /// <summary>Ghi 8 giá trị liên tục theo dấu của đội.</summary>
        public void WriteActions(ActionSegment<float> actionsOut)
        {
            float sign = team != null ? team.Sign : 1f;

            for (int i = 0; i < actionsOut.Length; i++)
            {
                actionsOut[i] = i < actions.Length ? actions[i] * sign : 0f;
            }
        }

        /// <summary>
        /// Ghi hành động cho môi trường (IManualActionSource). Nếu brain đang ở chế
        /// độ rời rạc thì helper của gói môi trường tự lượng tử hoá về ba mức, nên
        /// chế độ này dùng được cả với bản scene dành cho DQN.
        /// </summary>
        public void WriteActions(in ActionBuffers actionsOut)
        {
            WriteActions(new ActionSegment<float>(buffer));
            ManualActionSource.Write(actionsOut, buffer);
        }
    }
}
