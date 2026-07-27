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

        /// <summary>Đảm bảo scene có đúng một EventSystem để bấm được nút.</summary>
        public static void EnsureEventSystem()
        {
            EventSystem[] systems = Object.FindObjectsByType<EventSystem>(
                FindObjectsSortMode.None);

            // Một số scene môi trường (CaptureTheFlag) đã có sẵn EventSystem
            // riêng — bỏ các bản dư để Unity không cảnh báo "2 event systems".
            for (int i = 1; i < systems.Length; i++)
            {
                Object.Destroy(systems[i].gameObject);
            }

            if (systems.Length > 0)
            {
                return;
            }

            // Không DontDestroyOnLoad: mỗi scene tự gọi EnsureEventSystem,
            // nếu giữ lại qua scene sẽ chồng lên EventSystem của scene mới.
            new GameObject(
                "EventSystem",
                typeof(EventSystem),
                typeof(StandaloneInputModule)
            );
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

        // =====================================================
        // Bo góc / gradient / glow — sinh texture bằng code
        // để giao diện mềm mại, hiện đại hơn (không cần asset ngoài).
        // =====================================================

        private static readonly System.Collections.Generic.Dictionary<int, Sprite> RoundedCache =
            new System.Collections.Generic.Dictionary<int, Sprite>();

        private static readonly System.Collections.Generic.Dictionary<long, Sprite> RingCache =
            new System.Collections.Generic.Dictionary<long, Sprite>();

        /// <summary>Signed distance tới biên hình chữ nhật bo góc (âm = bên trong).</summary>
        private static float RoundedSdf(float fx, float fy, float half, float r)
        {
            float dx = Mathf.Abs(fx - half) - (half - r);
            float dy = Mathf.Abs(fy - half) - (half - r);
            float ax = Mathf.Max(dx, 0f);
            float ay = Mathf.Max(dy, 0f);
            float outDist = Mathf.Sqrt(ax * ax + ay * ay);
            float inDist = Mathf.Min(Mathf.Max(dx, dy), 0f);
            return outDist + inDist - r;
        }

        /// <summary>Sprite chữ nhật bo góc (trắng, 9-slice) — tô màu qua Image.color.</summary>
        public static Sprite RoundedSprite(int radius)
        {
            radius = Mathf.Max(1, radius);
            if (RoundedCache.TryGetValue(radius, out Sprite cached))
            {
                return cached;
            }

            const int pad = 6;
            const int ss = 4;
            int n = radius * 2 + pad;
            float half = n / 2f;

            var tex = new Texture2D(n, n, TextureFormat.RGBA32, false)
            {
                wrapMode = TextureWrapMode.Clamp,
                filterMode = FilterMode.Bilinear
            };

            var px = new Color32[n * n];
            for (int y = 0; y < n; y++)
            {
                for (int x = 0; x < n; x++)
                {
                    int inside = 0;
                    for (int sy = 0; sy < ss; sy++)
                    {
                        for (int sx = 0; sx < ss; sx++)
                        {
                            float fx = x + (sx + 0.5f) / ss;
                            float fy = y + (sy + 0.5f) / ss;
                            if (RoundedSdf(fx, fy, half, radius) <= 0f)
                            {
                                inside++;
                            }
                        }
                    }

                    byte a = (byte)(255 * inside / (ss * ss));
                    px[y * n + x] = new Color32(255, 255, 255, a);
                }
            }

            tex.SetPixels32(px);
            tex.Apply();

            var sprite = Sprite.Create(
                tex, new Rect(0, 0, n, n), new Vector2(0.5f, 0.5f), 100f, 0,
                SpriteMeshType.FullRect,
                new Vector4(radius, radius, radius, radius));

            RoundedCache[radius] = sprite;
            return sprite;
        }

        /// <summary>Sprite viền bo góc (chỉ nét, giữa trong suốt) — 9-slice.</summary>
        public static Sprite RingSprite(int radius, int thickness)
        {
            radius = Mathf.Max(1, radius);
            thickness = Mathf.Max(1, thickness);
            long key = ((long)radius << 8) | (uint)thickness;
            if (RingCache.TryGetValue(key, out Sprite cached))
            {
                return cached;
            }

            const int pad = 6;
            const int ss = 4;
            int n = radius * 2 + pad;
            float half = n / 2f;

            var tex = new Texture2D(n, n, TextureFormat.RGBA32, false)
            {
                wrapMode = TextureWrapMode.Clamp,
                filterMode = FilterMode.Bilinear
            };

            var px = new Color32[n * n];
            for (int y = 0; y < n; y++)
            {
                for (int x = 0; x < n; x++)
                {
                    int band = 0;
                    for (int sy = 0; sy < ss; sy++)
                    {
                        for (int sx = 0; sx < ss; sx++)
                        {
                            float fx = x + (sx + 0.5f) / ss;
                            float fy = y + (sy + 0.5f) / ss;
                            float sdf = RoundedSdf(fx, fy, half, radius);
                            if (sdf <= 0f && sdf > -thickness)
                            {
                                band++;
                            }
                        }
                    }

                    byte a = (byte)(255 * band / (ss * ss));
                    px[y * n + x] = new Color32(255, 255, 255, a);
                }
            }

            tex.SetPixels32(px);
            tex.Apply();

            var sprite = Sprite.Create(
                tex, new Rect(0, 0, n, n), new Vector2(0.5f, 0.5f), 100f, 0,
                SpriteMeshType.FullRect,
                new Vector4(radius, radius, radius, radius));

            RingCache[key] = sprite;
            return sprite;
        }

        /// <summary>Sprite tròn mờ dần (glow) — tô màu qua Image.color.</summary>
        public static Sprite RadialSprite()
        {
            const int n = 128;
            float c = (n - 1) / 2f;

            var tex = new Texture2D(n, n, TextureFormat.RGBA32, false)
            {
                wrapMode = TextureWrapMode.Clamp,
                filterMode = FilterMode.Bilinear
            };

            var px = new Color32[n * n];
            for (int y = 0; y < n; y++)
            {
                for (int x = 0; x < n; x++)
                {
                    float d = Mathf.Sqrt((x - c) * (x - c) + (y - c) * (y - c)) / c;
                    float a = Mathf.Clamp01(1f - d);
                    a *= a;
                    px[y * n + x] = new Color32(255, 255, 255, (byte)(a * 255));
                }
            }

            tex.SetPixels32(px);
            tex.Apply();

            return Sprite.Create(
                tex, new Rect(0, 0, n, n), new Vector2(0.5f, 0.5f));
        }

        /// <summary>Sprite gradient dọc (top ở trên, bottom ở dưới).</summary>
        public static Sprite VerticalGradientSprite(Color top, Color bottom)
        {
            const int h = 256;

            var tex = new Texture2D(1, h, TextureFormat.RGBA32, false)
            {
                wrapMode = TextureWrapMode.Clamp,
                filterMode = FilterMode.Bilinear
            };

            var px = new Color32[h];
            for (int y = 0; y < h; y++)
            {
                float t = y / (float)(h - 1);
                px[y] = Color.Lerp(bottom, top, t);
            }

            tex.SetPixels32(px);
            tex.Apply();

            return Sprite.Create(
                tex, new Rect(0, 0, 1, h), new Vector2(0.5f, 0.5f));
        }

        /// <summary>Nền gradient dọc phủ kín parent.</summary>
        public static RectTransform CreateGradientBackground(
            Transform parent, string name, Color top, Color bottom)
        {
            var go = new GameObject(name, typeof(RectTransform), typeof(Image));
            go.transform.SetParent(parent, false);

            var img = go.GetComponent<Image>();
            img.sprite = VerticalGradientSprite(top, bottom);
            img.type = Image.Type.Simple;

            var rect = (RectTransform)go.transform;
            Stretch(rect);
            return rect;
        }

        /// <summary>Quầng sáng tròn (đặt vị trí bằng Place ở nơi gọi).</summary>
        public static Image CreateGlow(Transform parent, string name, Color color)
        {
            var go = new GameObject(name, typeof(RectTransform), typeof(Image));
            go.transform.SetParent(parent, false);

            var img = go.GetComponent<Image>();
            img.sprite = RadialSprite();
            img.color = color;
            img.raycastTarget = false;
            return img;
        }

        private static void AddBorder(
            RectTransform target, Color color, int radius, int thickness)
        {
            var go = new GameObject("Border", typeof(RectTransform), typeof(Image));
            go.transform.SetParent(target, false);

            var img = go.GetComponent<Image>();
            img.sprite = RingSprite(radius, thickness);
            img.type = Image.Type.Sliced;
            img.color = color;
            img.raycastTarget = false;

            Stretch((RectTransform)go.transform);
        }

        /// <summary>Panel bo góc, tuỳ chọn có viền.</summary>
        public static RectTransform CreateRoundedPanel(
            Transform parent, string name, Color fill, int radius,
            Color? border = null, int borderThickness = 2)
        {
            var go = new GameObject(name, typeof(RectTransform), typeof(Image));
            go.transform.SetParent(parent, false);

            var img = go.GetComponent<Image>();
            img.sprite = RoundedSprite(radius);
            img.type = Image.Type.Sliced;
            img.color = fill;

            var rect = (RectTransform)go.transform;
            if (border.HasValue)
            {
                AddBorder(rect, border.Value, radius, borderThickness);
            }

            return rect;
        }

        /// <summary>
        /// Khung ảnh bo góc: nền (screen) bo góc + Mask cắt ảnh con theo góc bo.
        /// Trả về Image con để gán sprite; đặt vị trí qua transform cha (frame).
        /// </summary>
        public static Image CreatePictureFrame(
            Transform parent, string name, Color screenColor, int radius)
        {
            RectTransform frame = CreateRoundedPanel(parent, name, screenColor, radius);

            var mask = frame.gameObject.AddComponent<Mask>();
            mask.showMaskGraphic = true;

            var picGo = new GameObject("Picture", typeof(RectTransform), typeof(Image));
            picGo.transform.SetParent(frame, false);

            var pic = picGo.GetComponent<Image>();
            pic.preserveAspect = true;
            pic.raycastTarget = false;
            Stretch((RectTransform)picGo.transform);

            return pic;
        }

        /// <summary>
        /// Nút bo góc. Image nền lấy qua GetComponent&lt;Image&gt; (tương thích code cũ
        /// đổi màu chọn/bỏ chọn). Viền vẽ đè bằng sprite nét rỗng ở giữa.
        /// </summary>
        public static Button CreateRoundedButton(
            Transform parent, string name, string label, int fontSize,
            Color background, Color textColor, int radius, UnityAction onClick,
            Color? border = null)
        {
            var go = new GameObject(
                name, typeof(RectTransform), typeof(Image), typeof(Button));
            go.transform.SetParent(parent, false);

            var image = go.GetComponent<Image>();
            image.sprite = RoundedSprite(radius);
            image.type = Image.Type.Sliced;
            image.color = background;

            var button = go.GetComponent<Button>();
            button.targetGraphic = image;

            var colors = button.colors;
            colors.normalColor = Color.white;
            colors.highlightedColor = new Color(1.08f, 1.08f, 1.08f, 1f);
            colors.pressedColor = new Color(0.85f, 0.85f, 0.85f, 1f);
            colors.selectedColor = Color.white;
            colors.disabledColor = new Color(0.5f, 0.5f, 0.5f, 0.55f);
            colors.fadeDuration = 0.1f;
            button.colors = colors;

            if (border.HasValue)
            {
                AddBorder((RectTransform)go.transform, border.Value, radius, 2);
            }

            if (onClick != null)
            {
                button.onClick.AddListener(onClick);
            }

            var text = CreateText(
                go.transform, "Label", label, fontSize, textColor);
            Stretch((RectTransform)text.transform);

            return button;
        }
    }
}
