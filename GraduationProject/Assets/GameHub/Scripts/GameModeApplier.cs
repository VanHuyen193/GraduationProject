using System.Linq;
using TableFootball;
using Unity.InferenceEngine;
using Unity.MLAgents;
using Unity.MLAgents.Policies;
using UnityEngine;
using UnityEngine.SceneManagement;

namespace GameHub
{
    /// <summary>
    /// Khi một scene môi trường được mở từ Menu, class này cấu hình lại các agent
    /// (Heuristic cho người chơi / Inference với model đã chọn) và tạo HUD.
    /// Nếu mở scene trực tiếp (không qua Menu) thì giữ nguyên setup training.
    /// </summary>
    public static class GameModeApplier
    {
        [RuntimeInitializeOnLoadMethod(RuntimeInitializeLoadType.BeforeSceneLoad)]
        private static void Init()
        {
            SceneManager.sceneLoaded -= OnSceneLoaded;
            SceneManager.sceneLoaded += OnSceneLoaded;
        }

        private static void OnSceneLoaded(Scene scene, LoadSceneMode loadMode)
        {
            if (!GameModeSelection.HasSelection)
            {
                return;
            }

            string expected = GameModeSelection.SceneNameFor(
                GameModeSelection.Environment);

            if (scene.name != expected)
            {
                return;
            }

            switch (GameModeSelection.Environment)
            {
                case GameEnvironment.CrossTheRoad:
                    ApplyCrossTheRoad();
                    break;

                case GameEnvironment.CaptureTheFlag:
                    ApplyCaptureTheFlag();
                    break;

                case GameEnvironment.Football:
                    ApplyFootball();
                    break;
            }
        }

        // =====================================================
        // HELPERS
        // =====================================================

        /// <summary>
        /// Đặt chế độ hoạt động cho một agent:
        /// model != null → InferenceOnly với model; ngược lại HeuristicOnly.
        /// decisionPeriod > 0 → chỉnh DecisionRequester (1 = phản hồi tức thì).
        /// </summary>
        private static void Configure(
            Agent agent, ModelAsset model, int decisionPeriod = 0)
        {
            var behavior = agent.GetComponent<BehaviorParameters>();

            if (model != null)
            {
                agent.SetModel(behavior.BehaviorName, model);
                behavior.BehaviorType = BehaviorType.InferenceOnly;
            }
            else
            {
                behavior.BehaviorType = BehaviorType.HeuristicOnly;
            }

            if (decisionPeriod > 0)
            {
                var requester = agent.GetComponent<DecisionRequester>();

                if (requester != null)
                {
                    requester.DecisionPeriod = decisionPeriod;
                }
            }
        }

        private static ModelAsset LoadModel(string name)
        {
            return ModelRegistry.Load(GameModeSelection.Environment, name);
        }

        private static string ModeInfo()
        {
            return GameModeSelection.DisplayNameFor(GameModeSelection.Environment)
                + "  —  "
                + GameModeSelection.DisplayNameFor(GameModeSelection.Mode);
        }

        /// <summary>Đưa camera chính về khung nhìn bao trọn các khu vực còn hoạt động.</summary>
        private static void FrameCamera(GameObject[] areas)
        {
            CameraFramer.FrameWhenReady(areas);
        }

        // =====================================================
        // CROSS THE ROAD
        // =====================================================
        private static void ApplyCrossTheRoad()
        {
            // Mỗi khu vực (prefab CrossTheRoadArea) chứa 1 agent, sắp theo trục X
            CrossTheRoadAgent[] agents = Object
                .FindObjectsByType<CrossTheRoadAgent>(FindObjectsSortMode.None)
                .OrderBy(a => a.transform.root.position.x)
                .ThenBy(a => a.transform.root.position.z)
                .ToArray();

            GameObject[] areas = agents
                .Select(a => a.transform.root.gameObject)
                .ToArray();

            PlayMode mode = GameModeSelection.Mode;
            string info = ModeInfo();
            string help = null;
            LLMDriverBase llmDriver = null;

            switch (mode)
            {
                case PlayMode.Player:
                {
                    KeepAreas(areas, 1);
                    SetupHumanCrossRoad(agents[0]);
                    FrameCamera(new[] { areas[0] });

                    help = "← → ↑ (hoặc A / D / W) để di chuyển — băng qua đường tới đích!";
                    break;
                }

                case PlayMode.Agent:
                {
                    ModelAsset model = LoadModel(GameModeSelection.ModelA);

                    foreach (CrossTheRoadAgent agent in agents)
                    {
                        Configure(agent, model);
                    }

                    FrameCamera(areas);

                    info += "  |  Model: " + GameModeSelection.ModelA;
                    break;
                }

                case PlayMode.PlayerWithAgent:
                {
                    KeepAreas(areas, 2);

                    SetupHumanCrossRoad(agents[0]);
                    Configure(agents[1], LoadModel(GameModeSelection.ModelA));

                    FrameCamera(new[] { areas[0], areas[1] });

                    info += "  |  Agent: " + GameModeSelection.ModelA;
                    help = "Bạn: khu vực bên trái (← → ↑) — Agent: khu vực bên phải. Ai qua đường giỏi hơn?";
                    break;
                }

                case PlayMode.AgentVsLLM:
                {
                    KeepAreas(areas, 2);

                    Configure(agents[0], LoadModel(GameModeSelection.ModelA));

                    llmDriver = agents[1].gameObject
                        .AddComponent<LLMCrossRoadDriver>();
                    Configure(agents[1], null, 1);

                    FrameCamera(new[] { areas[0], areas[1] });

                    info += "  |  RL: " + GameModeSelection.ModelA
                          + "  vs  LLM: " + GameModeSelection.LLM.DisplayName;
                    help = "Agent RL: khu vực bên trái — LLM: khu vực bên phải. Ai qua đường giỏi hơn?";
                    break;
                }
            }

            InGameHUD hud = InGameHUD.Spawn(info, help);
            hud.TrackLLM(llmDriver);
        }

        private static void KeepAreas(GameObject[] areas, int keepCount)
        {
            for (int i = keepCount; i < areas.Length; i++)
            {
                areas[i].SetActive(false);
            }
        }

        private static void SetupHumanCrossRoad(CrossTheRoadAgent agent)
        {
            agent.gameObject.AddComponent<CrossRoadHumanInput>();
            Configure(agent, null, 1);
        }

        // =====================================================
        // CAPTURE THE FLAG
        // =====================================================
        private static void ApplyCaptureTheFlag()
        {
            PuzzleAgent[] agents = Object
                .FindObjectsByType<PuzzleAgent>(FindObjectsSortMode.None)
                .OrderBy(a => a.name)
                .ToArray();

            if (agents.Length < 2)
            {
                Debug.LogError("[GameHub] CaptureTheFlag cần 2 agent trong scene.");
                return;
            }

            PlayMode mode = GameModeSelection.Mode;
            string info = ModeInfo();
            string help = null;
            LLMDriverBase llmDriver = null;

            switch (mode)
            {
                case PlayMode.Player:
                {
                    SetupHumanPuzzle(agents[0], PuzzleHumanInput.Scheme.WASD);
                    SetupHumanPuzzle(agents[1], PuzzleHumanInput.Scheme.Arrows);

                    help = "Người 1: W A S D (Q/E đi ngang) — Người 2: ← ↑ ↓ → ([ ] đi ngang). "
                         + "Đứng lên nút để mở cửa, cùng tới checkpoint!";
                    break;
                }

                case PlayMode.Agent:
                {
                    ModelAsset model = LoadModel(GameModeSelection.ModelA);

                    Configure(agents[0], model);
                    Configure(agents[1], model);

                    info += "  |  Model: " + GameModeSelection.ModelA;
                    break;
                }

                case PlayMode.PlayerWithAgent:
                {
                    SetupHumanPuzzle(agents[0], PuzzleHumanInput.Scheme.WASD);
                    Configure(agents[1], LoadModel(GameModeSelection.ModelA));

                    info += "  |  Đồng đội: " + GameModeSelection.ModelA;
                    help = "Bạn: W A S D (Q/E đi ngang) — Agent đồng đội tự chơi. "
                         + "Phối hợp đứng lên nút để mở cửa!";
                    break;
                }

                case PlayMode.AgentVsLLM:
                {
                    Configure(agents[0], LoadModel(GameModeSelection.ModelA));

                    llmDriver = agents[1].gameObject
                        .AddComponent<LLMPuzzleDriver>();
                    Configure(agents[1], null, 1);

                    info += "  |  RL: " + GameModeSelection.ModelA
                          + "  +  LLM: " + GameModeSelection.LLM.DisplayName;
                    help = "Agent RL và LLM phối hợp: đứng lên nút mở cửa, cùng tới checkpoint.";
                    break;
                }
            }

            InGameHUD hud = InGameHUD.Spawn(info, help);
            hud.TrackLLM(llmDriver);
        }

        private static void SetupHumanPuzzle(
            PuzzleAgent agent, PuzzleHumanInput.Scheme scheme)
        {
            var input = agent.gameObject.AddComponent<PuzzleHumanInput>();
            input.scheme = scheme;

            Configure(agent, null, 1);
        }

        // =====================================================
        // FOOTBALL TABLE
        // =====================================================
        private static void ApplyFootball()
        {
            FootballAgent[] agents = Object
                .FindObjectsByType<FootballAgent>(FindObjectsSortMode.None)
                .ToArray();

            if (agents.Length < 2)
            {
                Debug.LogError("[GameHub] Football cần 2 agent trong scene.");
                return;
            }

            FootballAgent blue =
                agents.FirstOrDefault(a => a.name.Contains("Blue")) ?? agents[0];

            FootballAgent red = agents.First(a => a != blue);

            PlayMode mode = GameModeSelection.Mode;
            string info = ModeInfo();
            string help = null;
            FootballHumanInput humanInput = null;
            LLMDriverBase llmDriver = null;

            switch (mode)
            {
                case PlayMode.Player:
                {
                    humanInput = SetupHumanFootball(blue);
                    SetupFootballBot(red);

                    help = "Q/E hoặc 1-4: chọn thanh — W/S: trượt — A/D: xoay sút. "
                         + "Bạn là đội Xanh, đối thủ là bot.";
                    break;
                }

                case PlayMode.Agent:
                {
                    Configure(blue, LoadModel(GameModeSelection.ModelA));
                    Configure(red, LoadModel(GameModeSelection.ModelB));

                    info += "  |  Xanh: " + GameModeSelection.ModelA
                          + "  vs  Đỏ: " + GameModeSelection.ModelB;
                    break;
                }

                case PlayMode.PlayerWithAgent:
                {
                    humanInput = SetupHumanFootball(blue);
                    Configure(red, LoadModel(GameModeSelection.ModelA));

                    info += "  |  Đối thủ: " + GameModeSelection.ModelA;
                    help = "Q/E hoặc 1-4: chọn thanh — W/S: trượt — A/D: xoay sút. "
                         + "Bạn là đội Xanh, agent là đội Đỏ.";
                    break;
                }

                case PlayMode.AgentVsLLM:
                {
                    Configure(blue, LoadModel(GameModeSelection.ModelA));

                    var footballLLM = red.gameObject
                        .AddComponent<LLMFootballDriver>();
                    footballLLM.team = red.AgentTeam;
                    footballLLM.ball = Object.FindFirstObjectByType<Ball>();
                    llmDriver = footballLLM;

                    Configure(red, null, 1);

                    info += "  |  Xanh (RL): " + GameModeSelection.ModelA
                          + "  vs  Đỏ (LLM): " + GameModeSelection.LLM.DisplayName;
                    help = "Đội Xanh: model RL — Đội Đỏ: " + GameModeSelection.LLM.DisplayName
                         + " quyết định qua API (~1-2s/lượt).";
                    break;
                }
            }

            InGameHUD hud = InGameHUD.Spawn(info, help);

            if (humanInput != null)
            {
                hud.TrackFootballInput(humanInput);
            }

            hud.TrackLLM(llmDriver);
        }

        private static FootballHumanInput SetupHumanFootball(FootballAgent agent)
        {
            var input = agent.gameObject.AddComponent<FootballHumanInput>();
            input.team = agent.AgentTeam;

            Configure(agent, null, 1);

            return input;
        }

        /// <summary>
        /// Đội do bot script (DumbHeuristic) điều khiển ở chế độ người chơi:
        /// tắt quyết định của agent, bật DumbHeuristic đúng team.
        /// </summary>
        private static void SetupFootballBot(FootballAgent agent)
        {
            // Agent không tự ra quyết định nữa (không có model, không heuristic)
            var behavior = agent.GetComponent<BehaviorParameters>();
            behavior.BehaviorType = BehaviorType.HeuristicOnly;

            var requester = agent.GetComponent<DecisionRequester>();

            if (requester != null)
            {
                requester.enabled = false;
            }

            // Không cho episode tự kết thúc theo bước (đội người chơi quản lý reset)
            agent.MaxStep = 0;

            // Bật bot điều khiển đúng team này
            DumbHeuristic bot = Object
                .FindObjectsByType<DumbHeuristic>(
                    FindObjectsInactive.Include, FindObjectsSortMode.None)
                .FirstOrDefault(b =>
                    b.Team == agent.AgentTeam ||
                    b.gameObject == agent.gameObject);

            if (bot != null)
            {
                bot.enabled = true;
            }
            else
            {
                Debug.LogWarning(
                    "[GameHub] Không tìm thấy DumbHeuristic cho đội bot.");
            }
        }
    }
}
