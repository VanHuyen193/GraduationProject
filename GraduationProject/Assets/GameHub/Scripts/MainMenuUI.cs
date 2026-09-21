using System.Collections.Generic;
using UnityEngine;
using UnityEngine.SceneManagement;
using UnityEngine.UI;

namespace GameHub
{
    /// <summary>
    /// Menu chính: xem trước môi trường 3D tương tác (carousel), chọn chế độ chơi &
    /// model, xem thông số huấn luyện thật và so sánh năm thuật toán
    /// (PPO / SAC / MA-POCA / MAPPO / DQN) trên cả ba môi trường.
    /// </summary>
    public class MainMenuUI : MonoBehaviour
    {
        private enum View { Play, Stats, Compare }

        // ===== Bảng màu =====
        private static readonly Color BgTop = new Color32(12, 16, 28, 255);
        private static readonly Color BgBottom = new Color32(21, 28, 46, 255);
        private static readonly Color PanelColor = new Color32(23, 32, 51, 255);
        private static readonly Color PanelBorder = new Color32(44, 58, 84, 255);
        private static readonly Color ScreenColor = new Color32(9, 13, 22, 255);
        private static readonly Color FieldColor = new Color32(15, 21, 34, 255);
        private static readonly Color ButtonColor = new Color32(34, 46, 68, 255);
        private static readonly Color ButtonBorder = new Color32(54, 70, 100, 255);
        private static readonly Color SelectedColor = new Color32(59, 130, 246, 255);
        private static readonly Color PlayColor = new Color32(34, 178, 107, 255);
        private static readonly Color PlayBorder = new Color32(60, 214, 145, 255);
        private static readonly Color TextColor = new Color32(238, 242, 247, 255);
        private static readonly Color MutedColor = new Color32(140, 154, 176, 255);
        private static readonly Color AccentColor = new Color32(96, 165, 250, 255);
        private static readonly Color WarnColor = new Color32(255, 107, 94, 255);
        private static readonly Color GlowColor = new Color32(46, 110, 240, 55);

        // ===== Trạng thái =====
        private View currentView = View.Play;
        private GameEnvironment selectedEnv = GameEnvironment.CrossTheRoad;
        private PlayMode selectedMode = PlayMode.Player;

        private readonly int[] modelIndex = { 0, 0 };
        private string[] availableModels = new string[0];
        private int llmIndex;

        // ===== Tham chiếu UI =====
        private readonly Dictionary<View, Image> tabButtons = new Dictionary<View, Image>();
        private RectTransform playView, statsView, compareView;

        // Preview 3D
        private Preview3D preview3D;
        private Text previewName, previewTagline, previewAbout;
        private readonly Image[] dots = new Image[3];

        // Chọn chơi
        private readonly Dictionary<PlayMode, Image> modeButtons =
            new Dictionary<PlayMode, Image>();
        private RectTransform modelPanel, descPanel;
        private readonly Text[] slotLabels = new Text[2];
        private readonly Text[] slotValues = new Text[2];
        private readonly RectTransform[] slotRows = new RectTransform[2];
        private Text descriptionText, warningText;
        private Button playButton;

        // Thông số (biểu đồ 2D)
        private readonly Dictionary<GameEnvironment, Image> statsChips =
            new Dictionary<GameEnvironment, Image>();
        private Text statsTitle, statsYMax, statsYMin, statsXMax, statsEmpty;
        private UILineChart chart;
        private RectTransform legendRow;
        // 6 hàng x 6 cột = 1 hàng tiêu đề + 5 thuật toán (PPO/SAC/MA-POCA/MAPPO/DQN)
        private readonly Text[] tableCells = new Text[36];

        private readonly GameEnvironment[] allEnvs =
        {
            GameEnvironment.CrossTheRoad,
            GameEnvironment.CaptureTheFlag,
            GameEnvironment.Football,
        };

        /// <summary>
        /// Các chế độ được chào trong menu. <see cref="PlayMode.AgentVsLLM"/> nằm
        /// ngoài phạm vi bản trình diễn nên không xuất hiện ở lưới chọn chế độ, dù
        /// phần mã điều khiển bằng LLM vẫn còn trong nguồn.
        /// </summary>
        private static readonly PlayMode[] SelectableModes =
        {
            PlayMode.Player,
            PlayMode.Agent,
            PlayMode.PlayerWithAgent,
        };

        private void Start()
        {
            Time.timeScale = 1f;
            GameModeSelection.Clear();

            UIBuilder.EnsureEventSystem();
            BuildUI();
            SelectEnv(selectedEnv);
            ShowView(View.Play);
        }

        private void Update()
        {
            if (currentView == View.Compare)
            {
                return;
            }

            if (Input.GetKeyDown(KeyCode.RightArrow))
            {
                CycleEnv(1);
            }
            else if (Input.GetKeyDown(KeyCode.LeftArrow))
            {
                CycleEnv(-1);
            }
        }

        // =====================================================
        // DỰNG UI
        // =====================================================
        private void BuildUI()
        {
            Canvas canvas = UIBuilder.CreateCanvas("MenuCanvas");
            canvas.transform.SetParent(transform, false);

            RectTransform bg = UIBuilder.CreateGradientBackground(
                canvas.transform, "Background", BgTop, BgBottom);

            Image titleGlow = UIBuilder.CreateGlow(bg, "TitleGlow", GlowColor);
            UIBuilder.Place((RectTransform)titleGlow.transform,
                new Vector2(0.5f, 1f), new Vector2(0, -120), new Vector2(1500, 480));

            Text title = UIBuilder.CreateText(
                bg, "Title",
                "REINFORCEMENT LEARNING <color=#3B82F6>PLAYGROUND</color>",
                44, TextColor, TextAnchor.MiddleCenter, FontStyle.Bold);
            UIBuilder.Place((RectTransform)title.transform,
                new Vector2(0.5f, 1f), new Vector2(0, -52), new Vector2(1700, 58));

            RectTransform underline = UIBuilder.CreateRoundedPanel(
                bg, "TitleUnderline", AccentColor, 2);
            UIBuilder.Place(underline,
                new Vector2(0.5f, 1f), new Vector2(0, -84), new Vector2(240, 4));

            BuildTabs(bg);

            playView = UIBuilder.CreateGroup(bg, "PlayView");
            UIBuilder.Stretch(playView);
            statsView = UIBuilder.CreateGroup(bg, "StatsView");
            UIBuilder.Stretch(statsView);
            compareView = UIBuilder.CreateGroup(bg, "CompareView");
            UIBuilder.Stretch(compareView);

            preview3D = CreatePreview3D(
                "EnvPreview3D", new Vector3(0f, -1000f, 0f), 1040, 616);

            BuildPlayView();
            BuildStatsView();
            BuildCompareView();

            Text footer = UIBuilder.CreateText(
                bg, "Footer",
                "Đồ án tốt nghiệp  •  So sánh PPO / SAC / MA-POCA / MAPPO / DQN "
                + "trên 3 môi trường Unity ML-Agents  •  15 model đã huấn luyện",
                17, MutedColor);
            UIBuilder.Place((RectTransform)footer.transform,
                new Vector2(0.5f, 0f), new Vector2(0, 26), new Vector2(1700, 26));
        }

        private Preview3D CreatePreview3D(string name, Vector3 origin, int w, int h)
        {
            var go = new GameObject(name);
            go.transform.SetParent(transform, false);
            Preview3D p = go.AddComponent<Preview3D>();
            p.Init(w, h, origin, new Color(0.05f, 0.07f, 0.12f, 1f));
            p.SetRendering(false);
            return p;
        }

        private void BuildTabs(RectTransform parent)
        {
            RectTransform row = UIBuilder.CreateGroup(parent, "Tabs");
            UIBuilder.Place(row,
                new Vector2(0.5f, 1f), new Vector2(0, -132), new Vector2(720, 56));
            UIBuilder.AddHorizontalLayout(row, 12);

            AddTab(row, View.Play, "CHƠI");
            AddTab(row, View.Stats, "THÔNG SỐ");
            AddTab(row, View.Compare, "SO SÁNH");
        }

        private void AddTab(RectTransform row, View view, string label)
        {
            Button b = UIBuilder.CreateRoundedButton(
                row, "Tab_" + view, label, 24, ButtonColor, TextColor, 14,
                () => ShowView(view), ButtonBorder);
            tabButtons[view] = b.GetComponent<Image>();
        }

        private void ShowView(View view)
        {
            currentView = view;
            playView.gameObject.SetActive(view == View.Play);
            statsView.gameObject.SetActive(view == View.Stats);
            compareView.gameObject.SetActive(view == View.Compare);

            foreach (var pair in tabButtons)
            {
                pair.Value.color = pair.Key == view ? SelectedColor : ButtonColor;
            }

            preview3D.SetRendering(view == View.Play);

            if (view == View.Stats)
            {
                RefreshStats();
            }
        }

        // =====================================================
        // TAB CHƠI: preview 3D + chọn chế độ/model
        // =====================================================
        private void BuildPlayView()
        {
            // ----- Cột trái: xem trước môi trường 3D -----
            const float lx = -430f;

            RectTransform frame = UIBuilder.CreateRoundedPanel(
                playView, "Preview", ScreenColor, 16);
            UIBuilder.Place(frame,
                new Vector2(0.5f, 1f), new Vector2(lx, -410), new Vector2(780, 460));

            var viewGo = new GameObject("PreviewView",
                typeof(RectTransform), typeof(CanvasRenderer), typeof(RawImage));
            viewGo.transform.SetParent(frame, false);
            var ri = viewGo.GetComponent<RawImage>();
            ri.texture = preview3D.Texture;
            var vrt = (RectTransform)viewGo.transform;
            vrt.anchorMin = Vector2.zero;
            vrt.anchorMax = Vector2.one;
            vrt.offsetMin = new Vector2(4, 4);
            vrt.offsetMax = new Vector2(-4, -4);
            var orbit = viewGo.AddComponent<OrbitInput>();
            orbit.onOrbit = preview3D.Orbit;
            orbit.onZoom = preview3D.Zoom;

            RectTransform border = UIBuilder.CreateRoundedPanel(
                playView, "PreviewBorder", new Color(0, 0, 0, 0), 16, PanelBorder);
            UIBuilder.Place(border,
                new Vector2(0.5f, 1f), new Vector2(lx, -410), new Vector2(780, 460));
            border.GetComponent<Image>().raycastTarget = false;

            Text hint = UIBuilder.CreateText(
                frame, "Hint", "Kéo để xoay  •  lăn chuột để phóng to", 14,
                new Color(1f, 1f, 1f, 0.5f), TextAnchor.MiddleCenter);
            var hrt = (RectTransform)hint.transform;
            hrt.anchorMin = hrt.anchorMax = new Vector2(0.5f, 0f);
            hrt.pivot = new Vector2(0.5f, 0f);
            hrt.anchoredPosition = new Vector2(0, 10);
            hrt.sizeDelta = new Vector2(420, 22);
            hint.raycastTarget = false;

            Button prev = UIBuilder.CreateRoundedButton(
                playView, "EnvPrev", "‹", 40, new Color32(12, 18, 30, 210),
                TextColor, 24, () => CycleEnv(-1), ButtonBorder);
            UIBuilder.Place((RectTransform)prev.transform,
                new Vector2(0.5f, 1f), new Vector2(lx - 330, -410), new Vector2(56, 84));

            Button next = UIBuilder.CreateRoundedButton(
                playView, "EnvNext", "›", 40, new Color32(12, 18, 30, 210),
                TextColor, 24, () => CycleEnv(1), ButtonBorder);
            UIBuilder.Place((RectTransform)next.transform,
                new Vector2(0.5f, 1f), new Vector2(lx + 330, -410), new Vector2(56, 84));

            previewName = UIBuilder.CreateText(
                playView, "PreviewName", "", 34, TextColor,
                TextAnchor.MiddleCenter, FontStyle.Bold);
            UIBuilder.Place((RectTransform)previewName.transform,
                new Vector2(0.5f, 1f), new Vector2(lx, -672), new Vector2(780, 42));

            previewTagline = UIBuilder.CreateText(
                playView, "PreviewTagline", "", 20, AccentColor);
            UIBuilder.Place((RectTransform)previewTagline.transform,
                new Vector2(0.5f, 1f), new Vector2(lx, -706), new Vector2(780, 30));

            RectTransform dotRow = UIBuilder.CreateGroup(playView, "Dots");
            UIBuilder.Place(dotRow,
                new Vector2(0.5f, 1f), new Vector2(lx, -742), new Vector2(120, 18));
            UIBuilder.AddHorizontalLayout(dotRow, 12);
            for (int i = 0; i < 3; i++)
            {
                RectTransform d = UIBuilder.CreateRoundedPanel(
                    dotRow, "Dot" + i, MutedColor, 7);
                dots[i] = d.GetComponent<Image>();
            }

            previewAbout = UIBuilder.CreateText(
                playView, "PreviewAbout", "", 20, MutedColor);
            UIBuilder.Place((RectTransform)previewAbout.transform,
                new Vector2(0.5f, 1f), new Vector2(lx, -810), new Vector2(800, 110));

            // ----- Cột phải: chọn chế độ + model -----
            const float rx = 470f;

            Text modeLabel = UIBuilder.CreateText(
                playView, "ModeLabel", "CHẾ ĐỘ CHƠI", 22, AccentColor,
                TextAnchor.MiddleCenter, FontStyle.Bold);
            UIBuilder.Place((RectTransform)modeLabel.transform,
                new Vector2(0.5f, 1f), new Vector2(rx, -196), new Vector2(752, 30));

            RectTransform grid = UIBuilder.CreateGroup(playView, "ModeGrid");
            UIBuilder.Place(grid,
                new Vector2(0.5f, 1f), new Vector2(rx, -262), new Vector2(752, 62));
            // Ba chế độ xếp trên một hàng để lưới không bị lẻ một ô ở hàng dưới
            var g = grid.gameObject.AddComponent<GridLayoutGroup>();
            g.cellSize = new Vector2(240, 62);
            g.spacing = new Vector2(16, 14);
            g.childAlignment = TextAnchor.MiddleCenter;
            g.constraint = GridLayoutGroup.Constraint.FixedColumnCount;
            g.constraintCount = SelectableModes.Length;

            foreach (PlayMode mode in SelectableModes)
            {
                PlayMode captured = mode;
                Button b = UIBuilder.CreateRoundedButton(
                    grid, "Mode_" + mode, GameModeSelection.DisplayNameFor(mode),
                    24, ButtonColor, TextColor, 14,
                    () => { selectedMode = captured; Refresh(); }, ButtonBorder);
                modeButtons[mode] = b.GetComponent<Image>();
            }

            modelPanel = UIBuilder.CreateRoundedPanel(
                playView, "ModelPanel", PanelColor, 16, PanelBorder);
            UIBuilder.Place(modelPanel,
                new Vector2(0.5f, 1f), new Vector2(rx, -486), new Vector2(752, 202));

            Text modelTitle = UIBuilder.CreateText(
                modelPanel, "ModelTitle", "MODEL CHO AGENT", 20, MutedColor,
                TextAnchor.MiddleCenter, FontStyle.Bold);
            UIBuilder.Place((RectTransform)modelTitle.transform,
                new Vector2(0.5f, 1f), new Vector2(0, -28), new Vector2(700, 30));

            for (int i = 0; i < 2; i++)
            {
                slotRows[i] = BuildModelSlot(modelPanel, i);
            }

            descPanel = UIBuilder.CreateRoundedPanel(
                playView, "DescPanel", PanelColor, 16, PanelBorder);
            UIBuilder.Place(descPanel,
                new Vector2(0.5f, 1f), new Vector2(rx, -650), new Vector2(752, 96));
            descriptionText = UIBuilder.CreateText(
                descPanel, "Description", "", 20, TextColor);
            UIBuilder.Place((RectTransform)descriptionText.transform,
                new Vector2(0.5f, 0.5f), Vector2.zero, new Vector2(700, 80));

            warningText = UIBuilder.CreateText(
                playView, "Warning", "", 19, WarnColor);
            UIBuilder.Place((RectTransform)warningText.transform,
                new Vector2(0.5f, 1f), new Vector2(rx, -716), new Vector2(752, 54));

            Image playGlow = UIBuilder.CreateGlow(
                playView, "PlayGlow", new Color32(34, 178, 107, 70));
            UIBuilder.Place((RectTransform)playGlow.transform,
                new Vector2(0.5f, 1f), new Vector2(rx, -778), new Vector2(560, 220));

            playButton = UIBuilder.CreateRoundedButton(
                playView, "PlayButton", "BẮT ĐẦU", 32,
                PlayColor, Color.white, 16, Play, PlayBorder);
            UIBuilder.Place((RectTransform)playButton.transform,
                new Vector2(0.5f, 1f), new Vector2(rx, -778), new Vector2(440, 84));
        }

        private RectTransform BuildModelSlot(RectTransform parent, int slot)
        {
            RectTransform row = UIBuilder.CreateGroup(parent, "ModelSlot" + slot);
            UIBuilder.Place(row,
                new Vector2(0.5f, 1f), new Vector2(0, -92 - slot * 54),
                new Vector2(710, 50));

            // Nhãn model gồm cả tên thuật toán ("MA-POCA · Football_POCA_01") nên ô
            // giá trị rộng hơn phần nhãn mô tả bên trái.
            slotLabels[slot] = UIBuilder.CreateText(
                row, "SlotLabel", "", 20, TextColor, TextAnchor.MiddleRight);
            UIBuilder.Place((RectTransform)slotLabels[slot].transform,
                new Vector2(0.5f, 0.5f), new Vector2(-215, 0), new Vector2(250, 50));

            Button prev = UIBuilder.CreateRoundedButton(
                row, "Prev", "‹", 28, ButtonColor, TextColor, 9,
                () => CycleModel(slot, -1), ButtonBorder);
            UIBuilder.Place((RectTransform)prev.transform,
                new Vector2(0.5f, 0.5f), new Vector2(-52, 0), new Vector2(46, 46));

            RectTransform valueField = UIBuilder.CreateRoundedPanel(
                row, "ValueField", FieldColor, 9, ButtonBorder);
            UIBuilder.Place(valueField,
                new Vector2(0.5f, 0.5f), new Vector2(140, 0), new Vector2(320, 46));
            slotValues[slot] = UIBuilder.CreateText(
                valueField, "SlotValue", "", 19, AccentColor,
                TextAnchor.MiddleCenter, FontStyle.Bold);
            UIBuilder.Place((RectTransform)slotValues[slot].transform,
                new Vector2(0.5f, 0.5f), Vector2.zero, new Vector2(300, 42));

            Button next = UIBuilder.CreateRoundedButton(
                row, "Next", "›", 28, ButtonColor, TextColor, 9,
                () => CycleModel(slot, 1), ButtonBorder);
            UIBuilder.Place((RectTransform)next.transform,
                new Vector2(0.5f, 0.5f), new Vector2(330, 0), new Vector2(46, 46));

            return row;
        }

        // =====================================================
        // TAB THÔNG SỐ (biểu đồ 2D)
        // =====================================================
        private void BuildStatsView()
        {
            RectTransform chipRow = UIBuilder.CreateGroup(statsView, "StatsChips");
            UIBuilder.Place(chipRow,
                new Vector2(0.5f, 1f), new Vector2(0, -196), new Vector2(780, 52));
            UIBuilder.AddHorizontalLayout(chipRow, 14);
            foreach (GameEnvironment env in allEnvs)
            {
                GameEnvironment captured = env;
                Button b = UIBuilder.CreateRoundedButton(
                    chipRow, "Chip_" + env, GameModeSelection.DisplayNameFor(env),
                    22, ButtonColor, TextColor, 12,
                    () => SelectEnv(captured), ButtonBorder);
                statsChips[env] = b.GetComponent<Image>();
            }

            RectTransform panel = UIBuilder.CreateRoundedPanel(
                statsView, "ChartPanel", PanelColor, 16, PanelBorder);
            UIBuilder.Place(panel,
                new Vector2(0.5f, 1f), new Vector2(0, -496), new Vector2(1520, 500));

            var swipe = panel.gameObject.AddComponent<SwipeArea>();
            swipe.onSwipe = CycleEnv;

            statsTitle = UIBuilder.CreateText(
                panel, "ChartTitle", "Cumulative Reward", 22, TextColor,
                TextAnchor.MiddleLeft, FontStyle.Bold);
            var titleRt = (RectTransform)statsTitle.transform;
            titleRt.anchorMin = titleRt.anchorMax = new Vector2(0f, 1f);
            titleRt.pivot = new Vector2(0f, 1f);
            titleRt.anchoredPosition = new Vector2(40, -22);
            titleRt.sizeDelta = new Vector2(900, 32);
            statsTitle.raycastTarget = false;

            legendRow = UIBuilder.CreateGroup(panel, "Legend");
            legendRow.anchorMin = legendRow.anchorMax = new Vector2(1f, 1f);
            legendRow.pivot = new Vector2(1f, 1f);
            legendRow.anchoredPosition = new Vector2(-30, -22);
            var lhl = legendRow.gameObject.AddComponent<HorizontalLayoutGroup>();
            lhl.spacing = 24;
            lhl.childAlignment = TextAnchor.MiddleRight;
            lhl.childForceExpandWidth = false;
            lhl.childForceExpandHeight = false;
            lhl.childControlWidth = true;
            lhl.childControlHeight = true;
            var lfit = legendRow.gameObject.AddComponent<ContentSizeFitter>();
            lfit.horizontalFit = ContentSizeFitter.FitMode.PreferredSize;
            lfit.verticalFit = ContentSizeFitter.FitMode.PreferredSize;

            var chartGo = new GameObject("Chart",
                typeof(RectTransform), typeof(CanvasRenderer));
            chartGo.transform.SetParent(panel, false);
            chart = chartGo.AddComponent<UILineChart>();
            chart.raycastTarget = false;
            UIBuilder.Place((RectTransform)chartGo.transform,
                new Vector2(0.5f, 0.5f), new Vector2(28, -18), new Vector2(1380, 380));

            statsYMax = MakeAxisLabel(panel, TextAnchor.MiddleRight);
            UIBuilder.Place((RectTransform)statsYMax.transform,
                new Vector2(0f, 0.5f), new Vector2(44, 172), new Vector2(80, 26));
            statsYMin = MakeAxisLabel(panel, TextAnchor.MiddleRight);
            UIBuilder.Place((RectTransform)statsYMin.transform,
                new Vector2(0f, 0.5f), new Vector2(44, -196), new Vector2(80, 26));

            Text x0 = MakeAxisLabel(panel, TextAnchor.MiddleLeft);
            x0.text = "0";
            UIBuilder.Place((RectTransform)x0.transform,
                new Vector2(0f, 0f), new Vector2(92, 22), new Vector2(120, 24));
            statsXMax = MakeAxisLabel(panel, TextAnchor.MiddleRight);
            UIBuilder.Place((RectTransform)statsXMax.transform,
                new Vector2(1f, 0f), new Vector2(-40, 22), new Vector2(160, 24));

            Text xTitle = MakeAxisLabel(panel, TextAnchor.MiddleCenter);
            xTitle.text = "Số bước huấn luyện (steps)  →";
            UIBuilder.Place((RectTransform)xTitle.transform,
                new Vector2(0.5f, 0f), new Vector2(28, 22), new Vector2(500, 24));

            statsEmpty = UIBuilder.CreateText(
                panel, "Empty", "Chưa có dữ liệu huấn luyện cho môi trường này.",
                22, MutedColor);
            UIBuilder.Place((RectTransform)statsEmpty.transform,
                new Vector2(0.5f, 0.5f), new Vector2(28, 0), new Vector2(800, 40));
            statsEmpty.gameObject.SetActive(false);

            BuildStatsTable();
        }

        private Text MakeAxisLabel(RectTransform parent, TextAnchor anchor)
        {
            Text t = UIBuilder.CreateText(parent, "Axis", "", 17, MutedColor, anchor);
            t.raycastTarget = false;
            return t;
        }

        private void BuildStatsTable()
        {
            RectTransform panel = UIBuilder.CreateRoundedPanel(
                statsView, "StatsTable", PanelColor, 16, PanelBorder);
            UIBuilder.Place(panel,
                new Vector2(0.5f, 1f), new Vector2(0, -880), new Vector2(1520, 230));

            // Cột thuật toán rộng hơn vì còn kèm mã lần chạy ở cỡ chữ nhỏ.
            string[] headers = { "Thuật toán / lần chạy", "Reward cuối", "Tốt nhất",
                "Mean (10% cuối)", "Hội tụ (step)", "Tổng steps" };
            float[] cx = { -560, -240, -20, 230, 470, 670 };
            float[] cw = { 400, 200, 200, 240, 200, 180 };

            for (int row = 0; row < 6; row++)
            {
                float y = -26 - row * 34;
                bool header = row == 0;
                for (int col = 0; col < 6; col++)
                {
                    Text t = UIBuilder.CreateText(
                        panel, "Cell", header ? headers[col] : "",
                        header ? 18 : 17, header ? MutedColor : TextColor,
                        col == 0 ? TextAnchor.MiddleLeft : TextAnchor.MiddleCenter,
                        header ? FontStyle.Bold : FontStyle.Normal);
                    UIBuilder.Place((RectTransform)t.transform,
                        new Vector2(0.5f, 1f), new Vector2(cx[col], y),
                        new Vector2(cw[col], 32));
                    tableCells[row * 6 + col] = t;
                }
            }
        }

        // =====================================================
        // TAB SO SÁNH (cột 2D)
        // =====================================================
        private void BuildCompareView()
        {
            Text title = UIBuilder.CreateText(
                compareView, "CompareTitle",
                "Đối chiếu reward cuối (mean 10% cuối) theo môi trường",
                24, TextColor, TextAnchor.MiddleCenter, FontStyle.Bold);
            UIBuilder.Place((RectTransform)title.transform,
                new Vector2(0.5f, 1f), new Vector2(0, -200), new Vector2(1700, 34));

            Text note = UIBuilder.CreateText(
                compareView, "CompareNote",
                "Kết quả một seed; DQN* trên Football là tham chiếu riêng, không self-play.",
                15, MutedColor, TextAnchor.MiddleCenter);
            UIBuilder.Place((RectTransform)note.transform,
                new Vector2(0.5f, 1f), new Vector2(0, -236), new Vector2(1700, 26));

            float[] px = { -520f, 0f, 520f };
            for (int i = 0; i < allEnvs.Length; i++)
            {
                BuildCompareCard(allEnvs[i], px[i]);
            }

            BuildRankingTable();
        }

        private void BuildCompareCard(GameEnvironment env, float x)
        {
            RectTransform card = UIBuilder.CreateRoundedPanel(
                compareView, "Cmp_" + env, PanelColor, 16, PanelBorder);
            UIBuilder.Place(card,
                new Vector2(0.5f, 1f), new Vector2(x, -452), new Vector2(490, 400));

            Text name = UIBuilder.CreateText(
                card, "Name", GameModeSelection.DisplayNameFor(env), 22, TextColor,
                TextAnchor.MiddleCenter, FontStyle.Bold);
            UIBuilder.Place((RectTransform)name.transform,
                new Vector2(0.5f, 1f), new Vector2(0, -30), new Vector2(460, 30));

            EnvTraining data = TrainingDataStore.ForEnv(env);
            if (data == null || data.algorithms == null || data.algorithms.Length == 0)
            {
                return;
            }

            float hi = 0.0001f;
            foreach (var a in data.algorithms)
            {
                if (a != null && a.found && !IsStandaloneReference(env, a))
                {
                    hi = Mathf.Max(hi, a.meanLast10);
                }
            }

            const float baseY = 80f;
            const float maxH = 210f;
            int count = data.algorithms.Length;
            float totalWidth = 360f;
            float stepX = count > 1 ? totalWidth / (count - 1) : 0f;
            float startX = count > 1 ? -totalWidth / 2f : 0f;

            for (int i = 0; i < count; i++)
            {
                AlgoTraining a = data.algorithms[i];
                if (a == null)
                {
                    continue;
                }

                bool standalone = IsStandaloneReference(env, a);
                bool ok = a.found && !standalone;
                Color col = standalone ? MutedColor : TrainingDataStore.ColorFor(a.algo);
                float posX = startX + i * stepX;

                float val = ok ? a.meanLast10 : 0f;
                float h = ok ? Mathf.Clamp(val / hi, 0.02f, 1f) * maxH : 3f;

                RectTransform bar = UIBuilder.CreateRoundedPanel(
                    card, "Bar_" + a.algo, ok ? col : new Color32(60, 70, 90, 255), 6);
                UIBuilder.Place(bar,
                    new Vector2(0.5f, 0.5f), new Vector2(posX, baseY - maxH + h / 2f),
                    new Vector2(Mathf.Min(80, 320 / count), h));

                // Bề rộng ô chữ bám theo khoảng cách cột để năm thuật toán không đè nhau
                float cellW = count > 1 ? stepX - 6f : 120f;

                Text valText = UIBuilder.CreateText(
                    card, "V_" + a.algo,
                    standalone ? "Riêng" : (ok ? a.meanLast10.ToString("0.00") : "N/A"),
                    16, ok ? TextColor : MutedColor,
                    TextAnchor.MiddleCenter, FontStyle.Bold);
                UIBuilder.Place((RectTransform)valText.transform,
                    new Vector2(0.5f, 0.5f), new Vector2(posX, baseY - maxH + h + 22),
                    new Vector2(cellW, 26));

                Text algoText = UIBuilder.CreateText(
                    card, "A_" + a.algo, standalone ? a.algo + "*" : a.algo, 14, col,
                    TextAnchor.MiddleCenter, FontStyle.Bold);
                UIBuilder.Place((RectTransform)algoText.transform,
                    new Vector2(0.5f, 0.5f), new Vector2(posX, baseY - maxH - 24),
                    new Vector2(cellW, 24));
            }
        }

        private void BuildRankingTable()
        {
            RectTransform panel = UIBuilder.CreateRoundedPanel(
                compareView, "Ranking", PanelColor, 16, PanelBorder);
            UIBuilder.Place(panel,
                new Vector2(0.5f, 1f), new Vector2(0, -800), new Vector2(1560, 236));

            // Liệt kê đủ vị trí quan sát; riêng DQN/Football bị loại khỏi RankFor.
            string[] headers = { "Môi trường", "Hạng nhất", "Hạng nhì", "Hạng ba",
                "Hạng tư", "Hạng năm" };
            float[] cx = { -630, -360, -120, 120, 360, 600 };
            float[] cw = { 300, 240, 240, 240, 240, 240 };
            int places = headers.Length - 1;

            for (int col = 0; col < headers.Length; col++)
            {
                Text h = UIBuilder.CreateText(
                    panel, "H", headers[col], 18, MutedColor,
                    col == 0 ? TextAnchor.MiddleLeft : TextAnchor.MiddleCenter,
                    FontStyle.Bold);
                UIBuilder.Place((RectTransform)h.transform,
                    new Vector2(0.5f, 1f), new Vector2(cx[col], -34), new Vector2(cw[col], 34));
            }

            for (int r = 0; r < allEnvs.Length; r++)
            {
                GameEnvironment env = allEnvs[r];
                float y = -84 - r * 46;

                Text envCell = UIBuilder.CreateText(
                    panel, "E", GameModeSelection.DisplayNameFor(env), 19, TextColor,
                    TextAnchor.MiddleLeft);
                UIBuilder.Place((RectTransform)envCell.transform,
                    new Vector2(0.5f, 1f), new Vector2(cx[0], y), new Vector2(cw[0], 40));

                List<KeyValuePair<string, float>> ranking = RankFor(env);
                for (int p = 0; p < places; p++)
                {
                    string text = "—";
                    Color c = MutedColor;
                    if (p < ranking.Count)
                    {
                        text = ranking[p].Key + "  (" + ranking[p].Value.ToString("0.00") + ")";
                        c = TrainingDataStore.ColorFor(ranking[p].Key);
                    }

                    Text cell = UIBuilder.CreateText(
                        panel, "R", text, 18, c,
                        TextAnchor.MiddleCenter,
                        p == 0 ? FontStyle.Bold : FontStyle.Normal);
                    UIBuilder.Place((RectTransform)cell.transform,
                        new Vector2(0.5f, 1f), new Vector2(cx[p + 1], y),
                        new Vector2(cw[p + 1], 40));
                }
            }
        }

        private List<KeyValuePair<string, float>> RankFor(GameEnvironment env)
        {
            var list = new List<KeyValuePair<string, float>>();
            EnvTraining data = TrainingDataStore.ForEnv(env);
            if (data != null && data.algorithms != null)
            {
                foreach (var a in data.algorithms)
                {
                    if (a != null && a.found && !IsStandaloneReference(env, a))
                    {
                        list.Add(new KeyValuePair<string, float>(a.algo, a.meanLast10));
                    }
                }
            }
            list.Sort((p, q) => q.Value.CompareTo(p.Value));
            return list;
        }

        /// <summary>
        /// DQN trên Football dùng scene rời rạc và không có self-play, nên chỉ là
        /// tham chiếu độc lập; không đưa vào cột so sánh hay bảng xếp hạng self-play.
        /// </summary>
        private static bool IsStandaloneReference(GameEnvironment env, AlgoTraining data)
        {
            return env == GameEnvironment.Football
                && data != null
                && data.algo == "DQN";
        }

        // =====================================================
        // CHỌN MÔI TRƯỜNG (dùng chung mọi tab)
        // =====================================================
        private void CycleEnv(int delta)
        {
            int i = System.Array.IndexOf(allEnvs, selectedEnv);
            i = (i + delta + allEnvs.Length) % allEnvs.Length;
            SelectEnv(allEnvs[i]);
        }

        private void SelectEnv(GameEnvironment env)
        {
            selectedEnv = env;

            preview3D.Show(env.ToString());
            previewName.text = GameModeSelection.DisplayNameFor(env);
            previewTagline.text = EnvTagline(env);
            previewAbout.text = EnvAbout(env);

            int idx = System.Array.IndexOf(allEnvs, env);
            for (int i = 0; i < dots.Length; i++)
            {
                dots[i].color = i == idx ? AccentColor : MutedColor;
            }

            foreach (var pair in statsChips)
            {
                pair.Value.color = pair.Key == env ? SelectedColor : ButtonColor;
            }

            Refresh();

            if (currentView == View.Stats)
            {
                RefreshStats();
            }
        }

        // =====================================================
        // LOGIC CHỌN CHƠI
        // =====================================================
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

        private bool IsLLMSlot(int slot)
        {
            return selectedMode == PlayMode.AgentVsLLM && slot == 1;
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
            foreach (var pair in modeButtons)
            {
                pair.Value.color =
                    pair.Key == selectedMode ? SelectedColor : ButtonColor;
            }

            availableModels = ModelRegistry.GetModelNames(selectedEnv);
            for (int i = 0; i < 2; i++)
            {
                if (modelIndex[i] >= availableModels.Length)
                {
                    modelIndex[i] = 0;
                }
            }

            string[] slotNames = GetModelSlotLabels();
            bool needModels = slotNames.Length > 0;
            bool hasModels = availableModels.Length > 0;

            modelPanel.gameObject.SetActive(needModels);

            Vector2 descPos = descPanel.anchoredPosition;
            descPos.y = needModels ? -650f : -520f;
            descPanel.anchoredPosition = descPos;
            warningText.gameObject.SetActive(true);

            for (int i = 0; i < 2; i++)
            {
                bool active = i < slotNames.Length;
                slotRows[i].gameObject.SetActive(active);
                if (!active)
                {
                    continue;
                }

                slotLabels[i].text = slotNames[i];

                if (IsLLMSlot(i))
                {
                    slotValues[i].text = LLMConfig.Options[llmIndex].DisplayName;
                    slotValues[i].color = AccentColor;
                }
                else if (hasModels)
                {
                    string model = availableModels[modelIndex[i]];
                    AlgoTraining run = TrainingDataStore.RunOf(selectedEnv, model);
                    slotValues[i].text = TrainingDataStore.LabelFor(selectedEnv, model);
                    slotValues[i].color = run != null
                        ? TrainingDataStore.ColorFor(run.algo)
                        : AccentColor;
                }
                else
                {
                    slotValues[i].text = "(chưa có model)";
                    slotValues[i].color = MutedColor;
                }
            }

            descriptionText.text = GetDescription();

            bool canPlay = !needModels || hasModels;
            string warning = canPlay
                ? ""
                : "Chưa có model trong Assets/GameHub/Resources/AgentModels/"
                  + selectedEnv + " — thêm file .onnx vào đó.";

            if (canPlay && needModels)
            {
                warning = ActionSpaceWarning(slotNames.Length);
                canPlay = warning.Length == 0;
            }

            if (canPlay && selectedMode == PlayMode.AgentVsLLM)
            {
                LLMOption option = LLMConfig.Options[llmIndex];
                if (!LLMConfig.HasApiKey(option.Provider))
                {
                    canPlay = false;
                    warning = "Thiếu API key cho " + option.Provider
                        + " — thêm vào Assets/StreamingAssets/llm_config.json.";
                }
            }

            playButton.interactable = canPlay;
            warningText.text = warning;
        }

        /// <summary>
        /// Model DQN của Football xuất action rời rạc nên phải chạy trên scene
        /// FootballDiscrete, bốn thuật toán còn lại dùng scene liên tục. Một trận
        /// chỉ nạp được một scene, vì vậy hai ô model phải cùng loại action.
        /// Trả về chuỗi rỗng nếu lựa chọn hợp lệ.
        /// </summary>
        private string ActionSpaceWarning(int slotCount)
        {
            // Ô thứ hai là LLM thì không có model để so — LLM chơi được cả hai loại.
            bool comparable = slotCount > 1 && !IsLLMSlot(1);

            if (comparable && NeedsDiscreteScene(0) != NeedsDiscreteScene(1))
            {
                return "Không ghép được model rời rạc (DQN) với model liên tục "
                     + "trong cùng một trận — chọn DQN cho cả hai đội hoặc bỏ DQN.";
            }

            return "";
        }

        /// <summary>
        /// Model ở ô này đòi hỏi bản scene rời rạc hay không. Cross The Road và
        /// Capture The Flag vốn đã rời rạc cho cả năm thuật toán nên luôn là false.
        /// </summary>
        private bool NeedsDiscreteScene(int slot)
        {
            if (selectedEnv != GameEnvironment.Football
                || IsLLMSlot(slot) || availableModels.Length == 0)
            {
                return false;
            }

            AlgoTraining run = TrainingDataStore.RunOf(
                selectedEnv, availableModels[modelIndex[slot]]);

            return run != null && run.IsDiscrete;
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
                                 + " bằng text và chọn hành động qua API.";
                        default:
                            return "Đua với agent: bạn ở khu vực bên trái, agent ở khu vực bên cạnh.\n"
                                 + "Phím: ← → ↑ (hoặc A / D / W).";
                    }

                case GameEnvironment.CaptureTheFlag:
                    switch (selectedMode)
                    {
                        case PlayMode.Player:
                            return "Điều khiển 2 nhân vật phối hợp: đứng lên nút mở cửa, đẩy block, cùng tới đích.\n"
                                 + "Người 1: W A S D (Q/E ngang) — Người 2: mũi tên ([ ] ngang).";
                        case PlayMode.Agent:
                            return "Hai agent tự phối hợp vượt màn bằng model đã huấn luyện.";
                        case PlayMode.AgentVsLLM:
                            return "Agent RL phối hợp cùng LLM: một nhân vật do model điều khiển,"
                                 + " nhân vật kia do LLM quyết định qua API.";
                        default:
                            return "Bạn điều khiển 1 nhân vật (W A S D, Q/E ngang), agent điều khiển nhân vật còn lại.";
                    }

                default: // Football
                    switch (selectedMode)
                    {
                        case PlayMode.Player:
                            return "Bạn (đội Xanh) đấu với bot cơ bản (đội Đỏ).\n"
                                 + "Q/E hoặc 1-4: chọn thanh — W/S: trượt — A/D: xoay sút.";
                        case PlayMode.Agent:
                            return "Model vs Model: hai đội do hai model điều khiển — quan sát và so sánh.";
                        case PlayMode.AgentVsLLM:
                            return "Đội Xanh (model RL) đấu đội Đỏ (LLM điều khiển 4 thanh qua API).";
                        default:
                            return "Bạn (đội Xanh) đấu với agent (đội Đỏ).\n"
                                 + "Q/E hoặc 1-4: chọn thanh — W/S: trượt — A/D: xoay sút.";
                    }
            }
        }

        private static string EnvTagline(GameEnvironment env)
        {
            switch (env)
            {
                case GameEnvironment.CrossTheRoad: return "Điều hướng • 1 agent • rời rạc";
                case GameEnvironment.CaptureTheFlag: return "Hợp tác • 2 agent • group reward";
                case GameEnvironment.Football: return "Đối kháng • 1 vs 1 • liên tục";
                default: return "";
            }
        }

        private static string EnvAbout(GameEnvironment env)
        {
            switch (env)
            {
                case GameEnvironment.CrossTheRoad:
                    return "Băng qua nhiều làn xe để tới đích. Không gian rời rạc 4 hành động, "
                         + "một agent, phần thưởng thưa — phù hợp so sánh khả năng khám phá.";
                case GameEnvironment.CaptureTheFlag:
                    return "Giải đố hợp tác: hai nhân vật cùng đứng nút mở cửa, đẩy khối và tới đích chung. "
                         + "Phần thưởng nhóm (group reward) — lý tưởng cho MA-POCA.";
                default:
                    return "Bi lắc đối kháng 1v1: điều khiển 4 thanh cầu thủ ghi bàn. "
                         + "Không gian liên tục 8 hành động, tự chơi (self-play) cạnh tranh.";
            }
        }

        // =====================================================
        // CẬP NHẬT TAB THÔNG SỐ (2D)
        // =====================================================
        // =====================================================
        // =====================================================
        // CẬP NHẬT TAB THÔNG SỐ (2D)
        // =====================================================
        private void RefreshStats()
        {
            EnvTraining data = TrainingDataStore.ForEnv(selectedEnv);

            foreach (Transform child in legendRow)
            {
                Destroy(child.gameObject);
            }
            for (int i = 6; i < tableCells.Length; i++)
            {
                tableCells[i].text = "";
            }

            chart.ClearSeries();

            float yMin = float.MaxValue, yMax = float.MinValue;
            int xMax = 0;
            bool any = false;

            if (data != null && data.algorithms != null)
            {
                for (int r = 0; r < data.algorithms.Length; r++)
                {
                    AlgoTraining a = data.algorithms[r];
                    int row = r + 1;
                    if (row * 6 >= tableCells.Length)
                    {
                        break;
                    }

                    if (a == null || !a.found || a.cs == null || a.cs.Length == 0)
                    {
                        tableCells[row * 6 + 0].text = a != null ? a.algo : "N/A";
                        tableCells[row * 6 + 0].color = MutedColor;
                        for (int c = 1; c < 6; c++)
                        {
                            tableCells[row * 6 + c].text = "N/A";
                            tableCells[row * 6 + c].color = MutedColor;
                        }
                        continue;
                    }

                    any = true;
                    Color col = TrainingDataStore.ColorFor(a.algo);

                    int envMaxSteps = a.maxEnvSteps > 0 ? a.maxEnvSteps : a.cs[a.cs.Length - 1];
                    xMax = Mathf.Max(xMax, envMaxSteps);

                    // Chuỗi điểm liên tục (nét liền)
                    var pts = new Vector2[a.cs.Length];
                    for (int i = 0; i < a.cs.Length; i++)
                    {
                        pts[i] = new Vector2(a.cs[i], a.cv[i]);
                        yMin = Mathf.Min(yMin, a.cv[i]);
                        yMax = Mathf.Max(yMax, a.cv[i]);
                    }
                    chart.AddSeries(col, pts, 3f);

                    AddLegend(a.algo, col);

                    // Kèm mã lần chạy (= tên file ONNX trong menu CHƠI) để mỗi dòng
                    // truy vết được về đúng model đã sinh ra con số đó.
                    tableCells[row * 6 + 0].text = string.IsNullOrEmpty(a.runId)
                        ? a.algo
                        : a.algo + "  <size=13><color=#8C9AB0>" + a.runId + "</color></size>";
                    tableCells[row * 6 + 0].color = col;
                    tableCells[row * 6 + 1].text = a.final.ToString("0.000");
                    tableCells[row * 6 + 2].text = a.max.ToString("0.000");
                    tableCells[row * 6 + 3].text = a.meanLast10.ToString("0.000");
                    tableCells[row * 6 + 4].text = FormatSteps(a.convergeStep);
                    tableCells[row * 6 + 5].text = FormatSteps(a.steps);
                    for (int c = 1; c < 6; c++)
                    {
                        tableCells[row * 6 + c].color = TextColor;
                    }
                }
            }

            statsTitle.text = "Cumulative Reward — " + GameModeSelection.DisplayNameFor(selectedEnv);
            statsEmpty.gameObject.SetActive(!any);

            if (!any)
            {
                chart.ClearSeries();
                chart.Rebuild();
                statsYMax.text = "";
                statsYMin.text = "";
                statsXMax.text = "";
                return;
            }

            float pad = Mathf.Max(0.05f, (yMax - yMin) * 0.1f);
            yMin -= pad;
            yMax += pad;
            chart.SetRange(0, Mathf.Max(1, xMax), yMin, yMax);
            chart.SetGrid(5, 4);
            chart.Rebuild();

            statsYMax.text = yMax.ToString("0.00");
            statsYMin.text = yMin.ToString("0.00");
            statsXMax.text = FormatSteps(xMax);
        }

        private void AddLegend(string algo, Color col)
        {
            RectTransform item = UIBuilder.CreateGroup(legendRow, "L_" + algo);
            var hl = item.gameObject.AddComponent<HorizontalLayoutGroup>();
            hl.spacing = 8;
            hl.childAlignment = TextAnchor.MiddleCenter;
            hl.childForceExpandWidth = false;
            hl.childForceExpandHeight = false;
            hl.childControlWidth = true;
            hl.childControlHeight = true;
            var fit = item.gameObject.AddComponent<ContentSizeFitter>();
            fit.horizontalFit = ContentSizeFitter.FitMode.PreferredSize;
            fit.verticalFit = ContentSizeFitter.FitMode.PreferredSize;

            RectTransform dot = UIBuilder.CreateRoundedPanel(item, "d", col, 8);
            dot.GetComponent<Image>().raycastTarget = false;
            var le = dot.gameObject.AddComponent<LayoutElement>();
            le.preferredWidth = 18;
            le.preferredHeight = 18;

            var t = UIBuilder.CreateText(item, "t", algo, 18, TextColor,
                TextAnchor.MiddleLeft, FontStyle.Bold);
            t.raycastTarget = false;
            var te = t.gameObject.AddComponent<LayoutElement>();
            te.preferredWidth = algo.Length * 13 + 14; // đủ rộng để tên không bị xuống dòng
            te.preferredHeight = 24;
        }

        private static string FormatSteps(int steps)
        {
            if (steps >= 1_000_000)
            {
                return (steps / 1_000_000f).ToString("0.##") + "M";
            }
            if (steps >= 1_000)
            {
                return (steps / 1_000f).ToString("0.#") + "K";
            }
            return steps.ToString();
        }

        // =====================================================
        // BẮT ĐẦU CHƠI
        // =====================================================
        private void Play()
        {
            GameModeSelection.Environment = selectedEnv;
            GameModeSelection.Mode = selectedMode;
            GameModeSelection.HasSelection = true;

            bool hasModels = availableModels.Length > 0;
            GameModeSelection.ModelA = hasModels ? availableModels[modelIndex[0]] : null;
            GameModeSelection.ModelB = hasModels ? availableModels[modelIndex[1]] : null;
            GameModeSelection.LLM = selectedMode == PlayMode.AgentVsLLM
                ? LLMConfig.Options[llmIndex]
                : null;

            // Model rời rạc (DQN trên Football) cần bản scene có Behavior Parameters
            // rời rạc; Refresh() đã chặn tổ hợp hai ô khác loại action.
            int slotCount = GetModelSlotLabels().Length;
            GameModeSelection.DiscreteActions =
                slotCount > 0
                && (NeedsDiscreteScene(0) || (slotCount > 1 && NeedsDiscreteScene(1)));

            Time.timeScale = 1f;
            SceneManager.LoadScene(GameModeSelection.SceneToLoad());
        }
    }
}
