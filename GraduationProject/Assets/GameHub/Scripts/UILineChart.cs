using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UI;

namespace GameHub
{
    /// <summary>
    /// Biểu đồ đường vẽ bằng mesh (uGUI Graphic): lưới nền + nhiều chuỗi đường cong.
    /// Toạ độ dữ liệu được ánh xạ theo khoảng [xMin,xMax] x [yMin,yMax] vào RectTransform.
    /// </summary>
    public class UILineChart : MaskableGraphic
    {
        public class Series
        {
            public Color color;
            public Vector2[] points;   // toạ độ theo không gian dữ liệu (step, value)
            public float thickness = 3f;
            public bool isDashed = false;
        }

        private readonly List<Series> series = new List<Series>();
        private float xMin, xMax, yMin, yMax = 1f;
        private int gridCols = 4;
        private int gridRows = 4;

        private static readonly Color GridColor = new Color(1f, 1f, 1f, 0.06f);
        private static readonly Color AxisColor = new Color(1f, 1f, 1f, 0.16f);

        public void SetRange(float xmin, float xmax, float ymin, float ymax)
        {
            xMin = xmin;
            xMax = xmax;
            yMin = ymin;
            yMax = ymax;
        }

        public void SetGrid(int cols, int rows)
        {
            gridCols = Mathf.Max(1, cols);
            gridRows = Mathf.Max(1, rows);
        }

        public void ClearSeries()
        {
            series.Clear();
        }

        public void AddSeries(Color color, Vector2[] points, float thickness = 3f, bool isDashed = false)
        {
            series.Add(new Series { color = color, points = points, thickness = thickness, isDashed = isDashed });
        }

        public void Rebuild()
        {
            SetVerticesDirty();
        }

        protected override void OnPopulateMesh(VertexHelper vh)
        {
            vh.Clear();
            Rect r = GetPixelAdjustedRect();

            // Lưới dọc
            for (int i = 0; i <= gridCols; i++)
            {
                float x = r.xMin + (float)i / gridCols * r.width;
                AddLine(vh, new Vector2(x, r.yMin), new Vector2(x, r.yMax),
                    1.5f, i == 0 ? AxisColor : GridColor);
            }

            // Lưới ngang
            for (int j = 0; j <= gridRows; j++)
            {
                float y = r.yMin + (float)j / gridRows * r.height;
                AddLine(vh, new Vector2(r.xMin, y), new Vector2(r.xMax, y),
                    1.5f, j == 0 ? AxisColor : GridColor);
            }

            // Các đường cong
            foreach (Series s in series)
            {
                if (s.points == null || s.points.Length < 2)
                {
                    continue;
                }

                Vector2 prev = DataToLocal(s.points[0], r);
                for (int k = 1; k < s.points.Length; k++)
                {
                    Vector2 cur = DataToLocal(s.points[k], r);
                    if (s.isDashed)
                    {
                        AddDashedLine(vh, prev, cur, s.thickness, s.color, 10f, 6f);
                    }
                    else
                    {
                        AddLine(vh, prev, cur, s.thickness, s.color);
                    }
                    prev = cur;
                }
            }
        }

        private Vector2 DataToLocal(Vector2 p, Rect r)
        {
            float nx = Mathf.Approximately(xMax, xMin)
                ? 0.5f : Mathf.Clamp01((p.x - xMin) / (xMax - xMin));
            float ny = Mathf.Approximately(yMax, yMin)
                ? 0.5f : Mathf.Clamp01((p.y - yMin) / (yMax - yMin));
            return new Vector2(r.xMin + nx * r.width, r.yMin + ny * r.height);
        }

        private static void AddDashedLine(
            VertexHelper vh, Vector2 a, Vector2 b, float thickness, Color color, float dashLen = 10f, float gapLen = 6f)
        {
            Vector2 dir = b - a;
            float dist = dir.magnitude;
            if (dist < 1e-4f) return;
            dir /= dist;

            float current = 0f;
            while (current < dist)
            {
                float next = Mathf.Min(current + dashLen, dist);
                Vector2 p1 = a + dir * current;
                Vector2 p2 = a + dir * next;
                AddLine(vh, p1, p2, thickness, color);
                current = next + gapLen;
            }
        }

        private static void AddLine(
            VertexHelper vh, Vector2 a, Vector2 b, float thickness, Color color)
        {
            Vector2 dir = b - a;
            if (dir.sqrMagnitude < 1e-6f)
            {
                return;
            }

            dir.Normalize();
            Vector2 n = new Vector2(-dir.y, dir.x) * (thickness * 0.5f);

            int idx = vh.currentVertCount;
            UIVertex v = UIVertex.simpleVert;
            v.color = color;

            v.position = a - n; vh.AddVert(v);
            v.position = a + n; vh.AddVert(v);
            v.position = b + n; vh.AddVert(v);
            v.position = b - n; vh.AddVert(v);

            vh.AddTriangle(idx, idx + 1, idx + 2);
            vh.AddTriangle(idx + 2, idx + 3, idx);
        }
    }
}
