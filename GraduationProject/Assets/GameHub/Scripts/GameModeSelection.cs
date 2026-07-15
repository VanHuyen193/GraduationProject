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
        PlayerWithAgent  // Người chơi cùng / đấu với agent
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
        }
    }
}
