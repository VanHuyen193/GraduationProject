using UnityEngine;
using UnityEngine.Events;
using UnityEngine.EventSystems;
using UnityEngine.UI;

namespace GameHub
{
    /// <summary>
    /// Helper dựng UI (uGUI) bằng code, dùng chung cho Menu và HUD in-game.
    /// </summary>
    public static class UIBuilder
    {
        public static Font DefaultFont =>
            Resources.GetBuiltinResource<Font>("LegacyRuntime.ttf");

        /// <summary>Đảm bảo scene có EventSystem để bấm được nút.</summary>
        public static void EnsureEventSystem()
        {
            if (Object.FindFirstObjectByType<EventSystem>() != null)
            {
                return;
            }

            var go = new GameObject(
                "EventSystem",
                typeof(EventSystem),
                typeof(StandaloneInputModule)
            );

            Object.DontDestroyOnLoad(go);
        }

        public static Canvas CreateCanvas(string name, int sortingOrder = 0)
        {
            var go = new GameObject(
                name,
                typeof(Canvas),
                typeof(CanvasScaler),
                typeof(GraphicRaycaster)
            );

            var canvas = go.GetComponent<Canvas>();
            canvas.renderMode = RenderMode.ScreenSpaceOverlay;
            canvas.sortingOrder = sortingOrder;

            var scaler = go.GetComponent<CanvasScaler>();
            scaler.uiScaleMode = CanvasScaler.ScaleMode.ScaleWithScreenSize;
            scaler.referenceResolution = new Vector2(1920, 1080);
            scaler.matchWidthOrHeight = 0.5f;

            return canvas;
        }

        public static RectTransform CreatePanel(
            Transform parent, string name, Color color)
        {
            var go = new GameObject(name, typeof(RectTransform), typeof(Image));
            go.transform.SetParent(parent, false);
            go.GetComponent<Image>().color = color;
            return (RectTransform)go.transform;
        }

        public static RectTransform CreateGroup(Transform parent, string name)
        {
            var go = new GameObject(name, typeof(RectTransform));
            go.transform.SetParent(parent, false);
            return (RectTransform)go.transform;
        }

        public static Text CreateText(
            Transform parent,
            string name,
            string content,
            int size,
            Color color,
            TextAnchor alignment = TextAnchor.MiddleCenter,
            FontStyle style = FontStyle.Normal)
        {
            var go = new GameObject(name, typeof(RectTransform), typeof(Text));
            go.transform.SetParent(parent, false);

            var text = go.GetComponent<Text>();
            text.font = DefaultFont;
            text.text = content;
            text.fontSize = size;
            text.color = color;
            text.alignment = alignment;
            text.fontStyle = style;
            text.horizontalOverflow = HorizontalWrapMode.Wrap;
            text.verticalOverflow = VerticalWrapMode.Overflow;

            return text;
        }

        public static Button CreateButton(
            Transform parent,
            string name,
            string label,
            int fontSize,
            Color background,
            Color textColor,
            UnityAction onClick)
        {
            var go = new GameObject(
                name, typeof(RectTransform), typeof(Image), typeof(Button));
            go.transform.SetParent(parent, false);

            var image = go.GetComponent<Image>();
            image.color = background;

            var button = go.GetComponent<Button>();
            button.targetGraphic = image;

            var colors = button.colors;
            colors.highlightedColor = new Color(1.1f, 1.1f, 1.1f, 1f);
            colors.pressedColor = new Color(0.8f, 0.8f, 0.8f, 1f);
            button.colors = colors;

            if (onClick != null)
            {
                button.onClick.AddListener(onClick);
            }

            var text = CreateText(
                go.transform, "Label", label, fontSize, textColor);
            Stretch((RectTransform)text.transform);

            return button;
        }

        /// <summary>Kéo dãn RectTransform phủ kín parent.</summary>
        public static void Stretch(RectTransform rect)
        {
            rect.anchorMin = Vector2.zero;
            rect.anchorMax = Vector2.one;
            rect.offsetMin = Vector2.zero;
            rect.offsetMax = Vector2.zero;
        }

        /// <summary>Đặt anchor + kích thước theo toạ độ tương đối tâm màn hình.</summary>
        public static void Place(
            RectTransform rect,
            Vector2 anchor,
            Vector2 anchoredPosition,
            Vector2 size)
        {
            rect.anchorMin = anchor;
            rect.anchorMax = anchor;
            rect.pivot = new Vector2(0.5f, 0.5f);
            rect.anchoredPosition = anchoredPosition;
            rect.sizeDelta = size;
        }

        public static HorizontalLayoutGroup AddHorizontalLayout(
            RectTransform rect, float spacing, RectOffset padding = null)
        {
            var layout = rect.gameObject.AddComponent<HorizontalLayoutGroup>();
            layout.spacing = spacing;
            layout.childAlignment = TextAnchor.MiddleCenter;
            layout.childForceExpandWidth = true;
            layout.childForceExpandHeight = true;
            layout.childControlWidth = true;
            layout.childControlHeight = true;

            if (padding != null)
            {
                layout.padding = padding;
            }

            return layout;
        }
    }
}
