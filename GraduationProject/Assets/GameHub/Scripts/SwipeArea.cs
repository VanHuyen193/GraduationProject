using System;
using UnityEngine;
using UnityEngine.EventSystems;

namespace GameHub
{
    /// <summary>
    /// Bắt thao tác kéo/lướt ngang trên một vùng UI (cần có Graphic raycastTarget).
    /// Gọi onSwipe(+1) khi lướt sang trái (xem mục kế), onSwipe(-1) khi lướt sang phải.
    /// </summary>
    public class SwipeArea : MonoBehaviour,
        IBeginDragHandler, IDragHandler, IEndDragHandler
    {
        public Action<int> onSwipe;
        public float threshold = 70f;

        private float startX;
        private bool fired;

        public void OnBeginDrag(PointerEventData e)
        {
            startX = e.position.x;
            fired = false;
        }

        public void OnDrag(PointerEventData e)
        {
            if (fired)
            {
                return;
            }

            float dx = e.position.x - startX;
            if (Mathf.Abs(dx) >= threshold)
            {
                fired = true;
                onSwipe?.Invoke(dx < 0 ? 1 : -1);
            }
        }

        public void OnEndDrag(PointerEventData e)
        {
        }
    }
}
