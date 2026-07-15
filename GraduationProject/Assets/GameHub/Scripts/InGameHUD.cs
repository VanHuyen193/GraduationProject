using UnityEngine;
using UnityEngine.SceneManagement;
using UnityEngine.UI;

namespace GameHub
{
    /// <summary>
    /// HUD hiển thị trong các scene môi trường khi vào từ Menu:
    /// nút quay về menu (Esc), thông tin chế độ/model và hướng dẫn phím.
    /// </summary>
    public class InGameHUD : MonoBehaviour
    {
        private static readonly Color BarColor = new Color(0f, 0f, 0f, 0.55f);
        private static readonly Color TextColor = new Color32(236, 240, 241, 255);
        private static readonly Color AccentColor = new Color32(46, 134, 222, 255);

        private string infoLine;
        private string helpLine;

        private Text rodText;
        private TableFootball.FootballHumanInput footballInput;

        public static InGameHUD Spawn(string info, string help)
        {
            var go = new GameObject("GameHubHUD");
            var hud = go.AddComponent<InGameHUD>();
            hud.infoLine = info;
            hud.helpLine = help;
            return hud;
        }

        /// <summary>Gắn hiển thị thanh đang chọn (Football, chế độ người chơi).</summary>
        public void TrackFootballInput(TableFootball.FootballHumanInput input)
        {
            footballInput = input;
        }

        private void Start()
        {
            UIBuilder.EnsureEventSystem();

            Canvas canvas = UIBuilder.CreateCanvas("HUDCanvas", 100);
            canvas.transform.SetParent(transform, false);

            // ===== Thanh trên: nút menu + thông tin chế độ =====
            RectTransform topBar = UIBuilder.CreatePanel(
                canvas.transform, "TopBar", BarColor);
            topBar.anchorMin = new Vector2(0f, 1f);
            topBar.anchorMax = new Vector2(1f, 1f);
            topBar.pivot = new Vector2(0.5f, 1f);
            topBar.anchoredPosition = Vector2.zero;
            topBar.sizeDelta = new Vector2(0, 60);

            Button menuButton = UIBuilder.CreateButton(
                topBar, "MenuButton", "≡  Menu (Esc)", 24,
                AccentColor, Color.white, BackToMenu);
            UIBuilder.Place((RectTransform)menuButton.transform,
                new Vector2(0f, 0.5f), new Vector2(110, 0), new Vector2(190, 44));

            Text info = UIBuilder.CreateText(
                topBar, "Info", infoLine, 24, TextColor);
            UIBuilder.Place((RectTransform)info.transform,
                new Vector2(0.5f, 0.5f), Vector2.zero, new Vector2(1100, 50));

            // ===== Dòng trợ giúp phía dưới =====
            if (!string.IsNullOrEmpty(helpLine))
            {
                RectTransform bottomBar = UIBuilder.CreatePanel(
                    canvas.transform, "BottomBar", BarColor);
                bottomBar.anchorMin = new Vector2(0f, 0f);
                bottomBar.anchorMax = new Vector2(1f, 0f);
                bottomBar.pivot = new Vector2(0.5f, 0f);
                bottomBar.anchoredPosition = Vector2.zero;
                bottomBar.sizeDelta = new Vector2(0, 46);

                Text help = UIBuilder.CreateText(
                    bottomBar, "Help", helpLine, 22, TextColor);
                UIBuilder.Stretch((RectTransform)help.transform);
            }

            // ===== Thanh đang chọn (Football) =====
            if (footballInput != null)
            {
                rodText = UIBuilder.CreateText(
                    canvas.transform, "RodText", "", 26, AccentColor,
                    TextAnchor.MiddleLeft, FontStyle.Bold);
                UIBuilder.Place((RectTransform)rodText.transform,
                    new Vector2(0f, 1f), new Vector2(180, -95), new Vector2(340, 40));
            }
        }

        private void Update()
        {
            if (Input.GetKeyDown(KeyCode.Escape))
            {
                BackToMenu();
            }

            if (rodText != null && footballInput != null)
            {
                rodText.text = "Thanh: " + footballInput.SelectedRodName;
            }
        }

        private void BackToMenu()
        {
            Time.timeScale = 1f;
            GameModeSelection.Clear();
            SceneManager.LoadScene(GameModeSelection.MenuSceneName);
        }
    }
}
