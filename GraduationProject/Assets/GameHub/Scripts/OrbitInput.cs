using System;
using UnityEngine;
using UnityEngine.EventSystems;

namespace GameHub
{
    /// <summary>
    /// Nhận thao tác kéo (xoay) và lăn chuột (zoom) trên một vùng UI để điều khiển
    /// biểu đồ 3D. Cần Graphic raycastTarget (RawImage).
    /// </summary>
    public class OrbitInput : MonoBehaviour, IDragHandler, IScrollHandler
    {
        public Action<Vector2> onOrbit;
        public Action<float> onZoom;

        public void OnDrag(PointerEventData e)
        {
            onOrbit?.Invoke(e.delta);
        }

        public void OnScroll(PointerEventData e)
        {
            onZoom?.Invoke(e.scrollDelta.y);
        }
    }
}
