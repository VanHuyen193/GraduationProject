using UnityEngine;

namespace GameHub
{
    // Các môi trường có thể chơi
    public enum GameEnvironment
    {
        CrossTheRoad,
        CaptureTheFlag,
        Football
    }

    // Các chế độ chơi
    public enum PlayMode
    {
        Player,          // Người chơi tự điều khiển
        Agent,           // Agent tự chơi (inference bằng model đã train)
        PlayerWithAgent, // Người chơi cùng / đấu với agent
        AgentVsLLM       // Agent đã train đấu / phối hợp với LLM (ChatGPT, Gemini)
    }

    /// <summary>
    /// Lưu lựa chọn của người dùng từ Menu, tồn tại xuyên suốt các scene.
    /// </summary>
    public static class GameModeSelection
    {
        public const string MenuSceneName = "MainMenu";

        // Đã chọn từ menu hay chưa (nếu chưa thì các scene giữ nguyên setup training)
        public static bool HasSelection;

        public static GameEnvironment Environment = GameEnvironment.CrossTheRoad;
        public static PlayMode Mode = PlayMode.Player;

        // Tên model chính (agent duy nhất / agent thứ nhất / agent đối thủ, đồng đội)
        public static string ModelA;

        // Tên model thứ hai (chỉ dùng cho Football chế độ Agent vs Agent - đội Đỏ)
        public static string ModelB;

        // LLM được chọn cho chế độ AgentVsLLM
        public static LLMOption LLM;

        // Model đã chọn dùng action rời rạc (DQN). Chỉ có ý nghĩa với Football:
        // các thuật toán khác trên môi trường này xuất model liên tục, còn Cross
        // The Road và Capture The Flag vốn đã rời rạc cho cả năm thuật toán.
        public static bool DiscreteActions;

        /// <summary>Scene gốc dùng để huấn luyện môi trường.</summary>
        public static string SceneNameFor(GameEnvironment env)
        {
            switch (env)
            {
                case GameEnvironment.CrossTheRoad: return "CrossTheRoad";
                case GameEnvironment.CaptureTheFlag: return "CaptureTheFlag";
                case GameEnvironment.Football: return "Football";
                default: return null;
            }
        }

        /// <summary>
        /// Scene thực sự được nạp cho lựa chọn hiện tại. Không gian hành động được
        /// "nướng" vào Behavior Parameters của scene và ML-Agents dựng bộ truyền
        /// động ngay trong OnEnable, tức trước khi ứng dụng kịp can thiệp — nên
        /// model DQN của Football phải chạy trên bản sao rời rạc của scene
        /// (sinh bởi Tools ▸ Training ▸ Make FootballDiscrete Scene).
        /// </summary>
        public static string SceneToLoad()
        {
            if (Environment == GameEnvironment.Football && DiscreteActions)
            {
                return "FootballDiscrete";
            }

            return SceneNameFor(Environment);
        }

        public static string DisplayNameFor(GameEnvironment env)
        {
            switch (env)
            {
                case GameEnvironment.CrossTheRoad: return "Cross The Road";
                case GameEnvironment.CaptureTheFlag: return "Capture The Flag";
                case GameEnvironment.Football: return "Football Table";
                default: return env.ToString();
            }
        }

        public static string DisplayNameFor(PlayMode mode)
        {
            switch (mode)
            {
                case PlayMode.Player: return "Người chơi";
                case PlayMode.Agent: return "Agent tự chơi";
                case PlayMode.PlayerWithAgent: return "Chơi với Agent";
                case PlayMode.AgentVsLLM: return "Agent đấu LLM";
                default: return mode.ToString();
            }
        }

        /// <summary>Thư mục Resources chứa model ONNX của môi trường.</summary>
        public static string ModelFolderFor(GameEnvironment env)
        {
            return "AgentModels/" + env;
        }

        public static void Clear()
        {
            HasSelection = false;
            ModelA = null;
            ModelB = null;
            LLM = null;
            DiscreteActions = false;
        }
    }
}
