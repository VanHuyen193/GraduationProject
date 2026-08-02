using System.Text;
using Unity.MLAgents.Actuators;
using UnityEngine;
using VanHuyen.RLGameEnvs;

namespace GameHub
{
    /// <summary>
    /// LLM điều khiển CrossTheRoadAgent: mô tả vị trí agent/đích/xe,
    /// LLM chọn 1 trong 4 action. Agent tiêu thụ action qua Heuristic
    /// (giống CrossRoadHumanInput).
    /// </summary>
    public class LLMCrossRoadDriver : LLMDriverBase, IManualActionSource
    {
        private CrossTheRoadAgent agent;
        private CrossTheRoadCar[] cars;

        private int pendingAction;
        private string lastActionName = "-";

        private static readonly string[] ActionNames =
        {
            "đứng yên", "sang trái", "sang phải", "tiến lên"
        };

        private void Awake()
        {
            requestInterval = 1.0f;

            agent = GetComponent<CrossTheRoadAgent>();
            cars = transform.parent.GetComponentsInChildren<CrossTheRoadCar>();
        }

        protected override string SystemPrompt =>
            "You control a character crossing a busy road in a grid world. "
            + "Coordinates are local (x = sideways, z = toward the goal). "
            + "Each move covers 1 unit. Cars drive along the x axis at the "
            + "given z lanes and kill you on contact. "
            + "Actions: 0 = stay, 1 = move left (x-1), 2 = move right (x+1), "
            + "3 = move forward (z+1). Reach the goal's z as fast as possible "
            + "without being hit. Prefer moving forward when the lane ahead "
            + "is clear or cars are far. "
            + "Reply with ONLY one digit: 0, 1, 2 or 3.";

        protected override string BuildUserPrompt()
        {
            Vector3 me = agent.transform.localPosition;
            Vector3 goal = agent.GoalLocalPosition;

            var sb = new StringBuilder();

            sb.Append("You: x=").Append(me.x.ToString("F1"))
              .Append(", z=").Append(me.z.ToString("F1"))
              .Append(". Goal: x=").Append(goal.x.ToString("F1"))
              .Append(", z=").Append(goal.z.ToString("F1"))
              .Append(". Cars (moving along x):");

            foreach (CrossTheRoadCar car in cars)
            {
                if (car == null || !car.gameObject.activeInHierarchy)
                {
                    continue;
                }

                Vector3 p = car.transform.localPosition;

                sb.Append(" [x=").Append(p.x.ToString("F1"))
                  .Append(", z=").Append(p.z.ToString("F1"))
                  .Append(", dir=").Append(car.MovesTowardNegativeX ? "-x" : "+x")
                  .Append(", speed=").Append(car.Speed.ToString("F1"))
                  .Append("]");
            }

            sb.Append(" Which action (0-3)?");

            return sb.ToString();
        }

        protected override bool TryParseReply(string reply)
        {
            var ints = ExtractInts(reply);

            // Lấy số cuối cùng trong khoảng hợp lệ (phòng khi LLM giải thích thêm)
            for (int i = ints.Count - 1; i >= 0; i--)
            {
                if (ints[i] >= 0 && ints[i] <= 3)
                {
                    pendingAction = ints[i];
                    lastActionName = ActionNames[pendingAction];
                    StatusLine = "LLM: " + lastActionName
                        + "  (lượt " + (ReplyCount + 1) + ")";
                    return true;
                }
            }

            return false;
        }

        /// <summary>
        /// Agent gọi trong Heuristic: trả action đang chờ rồi reset về đứng yên
        /// (không lặp lại một bước đi cũ khi LLM chưa kịp trả lời).
        /// </summary>
        public int ConsumeAction()
        {
            int action = pendingAction;
            pendingAction = 0;
            return action;
        }

        /// <summary>Ghi hành động cho môi trường (IManualActionSource).</summary>
        public void WriteActions(in ActionBuffers actionsOut)
        {
            // ActionSegment là struct bọc mảng: gán qua biến cục bộ vẫn
            // ghi vào đúng mảng gốc.
            var discrete = actionsOut.DiscreteActions;
            discrete[0] = ConsumeAction();
        }
    }
}
