using System.Collections.Generic;
using UnityEngine;
using UnityEngine.SceneManagement;
using UnityEngine.UI;

namespace GameHub
{
    /// <summary>
    /// Menu chính: chọn môi trường, chế độ chơi và model cho agent.
    /// Toàn bộ UI được dựng bằng code khi scene MainMenu chạy.
    /// </summary>
    public class MainMenuUI : MonoBehaviour
    {
        private static readonly Color BgColor = new Color32(14, 21, 32, 255);
        private static readonly Color PanelColor = new Color32(22, 32, 46, 255);
        private static readonly Color ButtonColor = new Color32(52, 73, 94, 255);
        private static readonly Color SelectedColor = new Color32(46, 134, 222, 255);
        private static readonly Color PlayColor = new Color32(39, 174, 96, 255);
        private static readonly Color TextColor = new Color32(236, 240, 241, 255);
        private static readonly Color MutedColor = new Color32(149, 165, 166, 255);
        private static readonly Color WarnColor = new Color32(231, 76, 60, 255);

        private GameEnvironment selectedEnv = GameEnvironment.CrossTheRoad;
        private PlayMode selectedMode = PlayMode.Player;

        private readonly Dictionary<GameEnvironment, Image> envButtons =
            new Dictionary<GameEnvironment, Image>();

        private readonly Dictionary<PlayMode, Image> modeButtons =
            new Dictionary<PlayMode, Image>();

        // Model đang chọn cho từng slot (tối đa 2)
        private readonly int[] modelIndex = { 0, 0 };
        private string[] availableModels = new string[0];

        // LLM đang chọn (chế độ AgentVsLLM — slot thứ hai)
        private int llmIndex;

        /// <summary>Slot 1 là bộ chọn LLM thay vì model?</summary>
        private bool IsLLMSlot(int slot)
        {
            return selectedMode == PlayMode.AgentVsLLM && slot == 1;
        }

        private RectTransform modelPanel;
        private readonly Text[] slotLabels = new Text[2];
        private readonly Text[] slotValues = new Text[2];
        private readonly RectTransform[] slotRows = new RectTransform[2];

        private Text descriptionText;
        private Text warningText;
        private Button playButton;

        private void Start()
        {
            Time.timeScale = 1f;
            GameModeSelection.Clear();

            UIBuilder.EnsureEventSystem();
            BuildUI();
            Refresh();
        }

        // =====================================================
        // DỰNG UI
        // =====================================================
        private void BuildUI()
        {
            Canvas canvas = UIBuilder.CreateCanvas("MenuCanvas");
            canvas.transform.SetParent(transform, false);

            RectTransform bg = UIBuilder.CreatePanel(
                canvas.transform, "Background", BgColor);
            UIBuilder.Stretch(bg);

            // ===== Tiêu đề =====
            Text title = UIBuilder.CreateText(
                bg, "Title",
                "REINFORCEMENT LEARNING PLAYGROUND",
                52, TextColor, TextAnchor.MiddleCenter, FontStyle.Bold);
            UIBuilder.Place((RectTransform)title.transform,
                new Vector2(0.5f, 1f), new Vector2(0, -70), new Vector2(1600, 70));

            Text subtitle = UIBuilder.CreateText(
                bg, "Subtitle",
                "Chọn môi trường, chế độ chơi và model cho agent",
                26, MutedColor);
            UIBuilder.Place((RectTransform)subtitle.transform,
                new Vector2(0.5f, 1f), new Vector2(0, -125), new Vector2(1600, 40));

            // ===== Chọn môi trường =====
            Text envLabel = UIBuilder.CreateText(
                bg, "EnvLabel", "MÔI TRƯỜNG", 28, MutedColor,
                TextAnchor.MiddleCenter, FontStyle.Bold);
            UIBuilder.Place((RectTransform)envLabel.transform,
                new Vector2(0.5f, 1f), new Vector2(0, -190), new Vector2(1200, 40));

            RectTransform envRow = UIBuilder.CreateGroup(bg, "EnvRow");
            UIBuilder.Place(envRow,
                new Vector2(0.5f, 1f), new Vector2(0, -265), new Vector2(1300, 90));
            UIBuilder.AddHorizontalLayout(envRow, 25);

            foreach (GameEnvironment env in
                System.Enum.GetValues(typeof(GameEnvironment)))
            {
                GameEnvironment captured = env;

                Button button = UIBuilder.CreateButton(
                    envRow, "Env_" + env,
                    GameModeSelection.DisplayNameFor(env),
                    30, ButtonColor, TextColor,
                    () => { selectedEnv = captured; Refresh(); });

                envButtons[env] = button.GetComponent<Image>();
            }

            // ===== Chọn chế độ chơi =====
            Text modeLabel = UIBuilder.CreateText(
                bg, "ModeLabel", "CHẾ ĐỘ CHƠI", 28, MutedColor,
                TextAnchor.MiddleCenter, FontStyle.Bold);
            UIBuilder.Place((RectTransform)modeLabel.transform,
                new Vector2(0.5f, 1f), new Vector2(0, -365), new Vector2(1200, 40));

            RectTransform modeRow = UIBuilder.CreateGroup(bg, "ModeRow");
            UIBuilder.Place(modeRow,
                new Vector2(0.5f, 1f), new Vector2(0, -440), new Vector2(1300, 90));
            UIBuilder.AddHorizontalLayout(modeRow, 25);

            foreach (PlayMode mode in System.Enum.GetValues(typeof(PlayMode)))
            {
                PlayMode captured = mode;

                Button button = UIBuilder.CreateButton(
                    modeRow, "Mode_" + mode,
                    GameModeSelection.DisplayNameFor(mode),
                    30, ButtonColor, TextColor,
                    () => { selectedMode = captured; Refresh(); });

                modeButtons[mode] = button.GetComponent<Image>();
            }

            // ===== Panel chọn model =====
            modelPanel = UIBuilder.CreatePanel(bg, "ModelPanel", PanelColor);
            UIBuilder.Place(modelPanel,
                new Vector2(0.5f, 1f), new Vector2(0, -595), new Vector2(1300, 190));

            Text modelTitle = UIBuilder.CreateText(
                modelPanel, "ModelTitle", "MODEL CHO AGENT", 26, MutedColor,
                TextAnchor.MiddleCenter, FontStyle.Bold);
            UIBuilder.Place((RectTransform)modelTitle.transform,
                new Vector2(0.5f, 1f), new Vector2(0, -28), new Vector2(1200, 36));

            for (int i = 0; i < 2; i++)
            {
                slotRows[i] = BuildModelSlot(modelPanel, i);
            }

            // ===== Mô tả chế độ =====
            RectTransform descPanel = UIBuilder.CreatePanel(
                bg, "DescPanel", PanelColor);
            UIBuilder.Place(descPanel,
                new Vector2(0.5f, 1f), new Vector2(0, -790), new Vector2(1300, 150));

            descriptionText = UIBuilder.CreateText(
                descPanel, "Description", "", 26, TextColor);
            UIBuilder.Stretch((RectTransform)descriptionText.transform);

            // ===== Cảnh báo (thiếu model) =====
            warningText = UIBuilder.CreateText(
                bg, "Warning", "", 24, WarnColor);
            UIBuilder.Place((RectTransform)warningText.transform,
                new Vector2(0.5f, 0f), new Vector2(0, 175), new Vector2(1300, 40));

            // ===== Nút chơi =====
            playButton = UIBuilder.CreateButton(
                bg, "PlayButton", "BẮT ĐẦU", 40, PlayColor, Color.white, Play);
            UIBuilder.Place((RectTransform)playButton.transform,
                new Vector2(0.5f, 0f), new Vector2(0, 95), new Vector2(420, 95));
        }

        private RectTransform BuildModelSlot(RectTransform parent, int slot)
        {
            RectTransform row = UIBuilder.CreateGroup(parent, "ModelSlot" + slot);
            UIBuilder.Place(row,
                new Vector2(0.5f, 1f),
                new Vector2(0, -85 - slot * 55),
                new Vector2(1200, 50));

            slotLabels[slot] = UIBuilder.CreateText(
                row, "SlotLabel", "", 26, TextColor, TextAnchor.MiddleRight);
            UIBuilder.Place((RectTransform)slotLabels[slot].transform,
                new Vector2(0.5f, 0.5f), new Vector2(-330, 0), new Vector2(520, 50));

            Button prev = UIBuilder.CreateButton(
                row, "Prev", "<", 30, ButtonColor, TextColor,
                () => CycleModel(slot, -1));
            UIBuilder.Place((RectTransform)prev.transform,
                new Vector2(0.5f, 0.5f), new Vector2(-20, 0), new Vector2(55, 50));

            slotValues[slot] = UIBuilder.CreateText(
                row, "SlotValue", "", 28, SelectedColor,
                TextAnchor.MiddleCenter, FontStyle.Bold);
            UIBuilder.Place((RectTransform)slotValues[slot].transform,
                new Vector2(0.5f, 0.5f), new Vector2(190, 0), new Vector2(350, 50));

            Button next = UIBuilder.CreateButton(
                row, "Next", ">", 30, ButtonColor, TextColor,
                () => CycleModel(slot, +1));
            UIBuilder.Place((RectTransform)next.transform,
                new Vector2(0.5f, 0.5f), new Vector2(400, 0), new Vector2(55, 50));

            return row;
        }

        // =====================================================
        // LOGIC
        // =====================================================

        /// <summary>Số slot model và nhãn theo môi trường + chế độ.</summary>
        private string[] GetModelSlotLabels()
        {
            if (selectedMode == PlayMode.Player)
            {
                return new string[0];
            }

            if (selectedMode == PlayMode.AgentVsLLM)
            {
                switch (selectedEnv)
                {
                    case GameEnvironment.CrossTheRoad:
                        return new[] { "Model agent RL:", "LLM đua cùng:" };
                    case GameEnvironment.CaptureTheFlag:
                        return new[] { "Model agent RL:", "LLM đồng đội:" };
                    default:
                        return new[] { "Model đội Xanh:", "LLM đội Đỏ:" };
                }
            }

            switch (selectedEnv)
            {
                case GameEnvironment.CrossTheRoad:
                    return selectedMode == PlayMode.Agent
                        ? new[] { "Model cho agent:" }
                        : new[] { "Model agent đua cùng:" };

                case GameEnvironment.CaptureTheFlag:
                    return selectedMode == PlayMode.Agent
                        ? new[] { "Model cho cả 2 agent:" }
                        : new[] { "Model agent đồng đội:" };

                case GameEnvironment.Football:
                    return selectedMode == PlayMode.Agent
                        ? new[] { "Model đội Xanh:", "Model đội Đỏ:" }
                        : new[] { "Model đội đối thủ (Đỏ):" };

                default:
                    return new string[0];
            }
        }

        private void CycleModel(int slot, int delta)
        {
            if (IsLLMSlot(slot))
            {
                int count = LLMConfig.Options.Length;
                llmIndex = (llmIndex + delta + count) % count;
                Refresh();
                return;
            }

            if (availableModels.Length == 0)
            {
                return;
            }

            modelIndex[slot] =
                (modelIndex[slot] + delta + availableModels.Length)
                % availableModels.Length;

            Refresh();
        }

        private void Refresh()
        {
            // Highlight nút môi trường / chế độ đang chọn
            foreach (var pair in envButtons)
            {
                pair.Value.color =
                    pair.Key == selectedEnv ? SelectedColor : ButtonColor;
            }

            foreach (var pair in modeButtons)
            {
                pair.Value.color =
                    pair.Key == selectedMode ? SelectedColor : ButtonColor;
            }

            // Danh sách model của môi trường đang chọn
            availableModels = ModelRegistry.GetModelNames(selectedEnv);

            for (int i = 0; i < 2; i++)
            {
                if (modelIndex[i] >= availableModels.Length)
                {
                    modelIndex[i] = 0;
                }
            }

            // Panel model
            string[] slotNames = GetModelSlotLabels();
            bool needModels = slotNames.Length > 0;
            bool hasModels = availableModels.Length > 0;

            modelPanel.gameObject.SetActive(needModels);

            for (int i = 0; i < 2; i++)
            {
                bool active = i < slotNames.Length;
                slotRows[i].gameObject.SetActive(active);

                if (!active)
                {
                    continue;
                }

                slotLabels[i].text = slotNames[i];

                slotValues[i].text = IsLLMSlot(i)
                    ? LLMConfig.Options[llmIndex].DisplayName
                    : hasModels
                        ? availableModels[modelIndex[i]]
                        : "(chưa có model)";
            }

            // Mô tả + trạng thái nút chơi
            descriptionText.text = GetDescription();

            bool canPlay = !needModels || hasModels;
            string warning = canPlay
                ? ""
                : "Chưa có model nào trong Assets/GameHub/Resources/AgentModels/"
                  + selectedEnv + " — hãy thêm file .onnx vào đó.";

            // Chế độ LLM: cần thêm API key của nhà cung cấp đã chọn
            if (canPlay && selectedMode == PlayMode.AgentVsLLM)
            {
                LLMOption option = LLMConfig.Options[llmIndex];

                if (!LLMConfig.HasApiKey(option.Provider))
                {
                    canPlay = false;
                    warning = "Thiếu API key cho " + option.Provider
                        + " — thêm vào Assets/StreamingAssets/llm_config.json"
                        + " (xem llm_config.example.json).";
                }
            }

            playButton.interactable = canPlay;
            warningText.text = warning;
        }

        private string GetDescription()
        {
            switch (selectedEnv)
            {
                case GameEnvironment.CrossTheRoad:
                    switch (selectedMode)
                    {
                        case PlayMode.Player:
                            return "Điều khiển nhân vật băng qua đường, tránh xe và tới đích.\n"
                                 + "Phím: ← → ↑ (hoặc A / D / W).";
                        case PlayMode.Agent:
                            return "Agent tự chơi trên cả 9 khu vực bằng model đã huấn luyện.";
                        case PlayMode.AgentVsLLM:
                            return "Agent RL (trái) đua với LLM (phải): LLM nhận mô tả trạng thái"
                                 + " bằng text và chọn hành động qua API.\nAi qua đường giỏi hơn?";
                        default:
                            return "Đua với agent: bạn ở khu vực bên trái, agent ở khu vực bên cạnh.\n"
                                 + "Phím: ← → ↑ (hoặc A / D / W).";
                    }

                case GameEnvironment.CaptureTheFlag:
                    switch (selectedMode)
                    {
                        case PlayMode.Player:
                            return "Điều khiển 2 nhân vật phối hợp: đứng lên nút để mở cửa, đẩy block và cùng tới checkpoint.\n"
                                 + "Người 1: W A S D (Q / E đi ngang)  —  Người 2: phím mũi tên ( [ ] đi ngang).";
                        case PlayMode.Agent:
                            return "Hai agent tự phối hợp vượt màn bằng model đã huấn luyện.";
                        case PlayMode.AgentVsLLM:
                            return "Agent RL phối hợp cùng LLM: một nhân vật do model điều khiển,"
                                 + " nhân vật kia do LLM quyết định qua API.\n"
                                 + "LLM có hợp tác tốt như agent RL không?";
                        default:
                            return "Bạn điều khiển 1 nhân vật (W A S D, Q / E đi ngang), agent điều khiển nhân vật còn lại.\n"
                                 + "Phối hợp cùng nhau để qua màn!";
                    }

                default: // Football
                    switch (selectedMode)
                    {
                        case PlayMode.Player:
                            return "Bạn (đội Xanh) đấu với bot cơ bản (đội Đỏ).\n"
                                 + "Q / E hoặc 1-4: chọn thanh  —  W / S: trượt thanh  —  A / D: xoay sút.";
                        case PlayMode.Agent:
                            return "Model vs Model: hai đội do hai model điều khiển — quan sát và so sánh.";
                        case PlayMode.AgentVsLLM:
                            return "Đội Xanh (model RL) đấu với đội Đỏ (LLM điều khiển 4 thanh qua API).\n"
                                 + "RL phản xạ từng frame, LLM suy nghĩ ~1-2 giây/lượt — ai thắng?";
                        default:
                            return "Bạn (đội Xanh) đấu với agent (đội Đỏ).\n"
                                 + "Q / E hoặc 1-4: chọn thanh  —  W / S: trượt thanh  —  A / D: xoay sút.";
                    }
            }
        }

        private void Play()
        {
            GameModeSelection.Environment = selectedEnv;
            GameModeSelection.Mode = selectedMode;
            GameModeSelection.HasSelection = true;

            bool hasModels = availableModels.Length > 0;

            GameModeSelection.ModelA =
                hasModels ? availableModels[modelIndex[0]] : null;

            GameModeSelection.ModelB =
                hasModels ? availableModels[modelIndex[1]] : null;

            GameModeSelection.LLM =
                selectedMode == PlayMode.AgentVsLLM
                    ? LLMConfig.Options[llmIndex]
                    : null;

            Time.timeScale = 1f;

            SceneManager.LoadScene(
                GameModeSelection.SceneNameFor(selectedEnv));
        }
    }
}
