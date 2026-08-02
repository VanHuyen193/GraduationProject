using Unity.MLAgents.Actuators;
using UnityEngine;

namespace VanHuyen.RLGameEnvs
{
    /// <summary>
    /// Nguồn hành động thủ công gắn cùng GameObject với một Agent: bàn phím người
    /// chơi, mô hình ngôn ngữ lớn, kịch bản kiểm thử tự động…
    ///
    /// Ba môi trường trong gói này gọi <see cref="WriteActions"/> ở đầu hàm
    /// <c>Heuristic</c>. Nhờ vậy môi trường không cần biết gì về ứng dụng đang nhúng
    /// nó: muốn thêm một cách điều khiển mới thì viết một MonoBehaviour hiện thực
    /// giao diện này rồi gắn vào cùng GameObject, không phải sửa mã môi trường.
    /// Khi không có thành phần nào hiện thực giao diện, mỗi môi trường quay về sơ
    /// đồ phím mặc định của nó.
    /// </summary>
    public interface IManualActionSource
    {
        /// <summary>Ghi hành động cho bước quyết định hiện tại.</summary>
        void WriteActions(in ActionBuffers actionsOut);
    }

    /// <summary>Tiện ích dùng chung cho các nguồn hành động thủ công.</summary>
    public static class ManualActionSource
    {
        /// <summary>
        /// Tìm nguồn điều khiển thủ công trên GameObject của tác nhân.
        /// Trả về <c>null</c> nếu tác nhân đang chạy tự động.
        /// </summary>
        public static IManualActionSource Find(Component agent)
        {
            return agent != null
                ? agent.GetComponent<IManualActionSource>()
                : null;
        }

        /// <summary>
        /// Ghi một mảng giá trị liên tục vào <paramref name="actionsOut"/>, tự lượng
        /// tử hoá về ba mức <c>{0, 1, 2}</c> khi brain đang ở chế độ rời rạc.
        ///
        /// Cần thiết vì cùng một môi trường có thể chạy ở hai không gian hành động:
        /// PPO/SAC/MA-POCA/MAPPO dùng bản liên tục, còn DQN chỉ định nghĩa được
        /// trên bản rời rạc. Nguồn điều khiển vì thế chỉ cần sinh ra ý định trong
        /// đoạn [-1, 1] và không phải quan tâm brain nào đang chạy.
        /// </summary>
        public static void Write(in ActionBuffers actionsOut, float[] values)
        {
            if (values == null)
            {
                return;
            }

            ActionSegment<int> discrete = actionsOut.DiscreteActions;

            if (discrete.Length > 0)
            {
                for (int i = 0; i < discrete.Length; i++)
                {
                    float v = i < values.Length ? values[i] : 0f;
                    discrete[i] = Mathf.RoundToInt(Mathf.Clamp(v, -1f, 1f)) + 1;
                }

                return;
            }

            ActionSegment<float> continuous = actionsOut.ContinuousActions;

            for (int i = 0; i < continuous.Length; i++)
            {
                continuous[i] = i < values.Length ? values[i] : 0f;
            }
        }
    }
}
