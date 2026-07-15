using UnityEngine;

namespace GameHub
{
    /// <summary>
    /// Sơ đồ phím cho PuzzleAgent (Capture The Flag) ở chế độ người chơi.
    /// Cho phép 2 người chơi trên cùng bàn phím: WASD và phím mũi tên.
    /// </summary>
    public class PuzzleHumanInput : MonoBehaviour
    {
        public enum Scheme
        {
            WASD,
            Arrows
        }

        public Scheme scheme = Scheme.WASD;

        /// <summary>
        /// Trả về action rời rạc theo sơ đồ phím:
        /// 0 = đứng yên, 1 = tiến, 2 = lùi, 3 = xoay phải, 4 = xoay trái,
        /// 5 = ngang trái, 6 = ngang phải.
        /// </summary>
        public int GetAction()
        {
            if (scheme == Scheme.WASD)
            {
                if (Input.GetKey(KeyCode.W)) return 1;
                if (Input.GetKey(KeyCode.S)) return 2;
                if (Input.GetKey(KeyCode.D)) return 3;
                if (Input.GetKey(KeyCode.A)) return 4;
                if (Input.GetKey(KeyCode.Q)) return 5;
                if (Input.GetKey(KeyCode.E)) return 6;
            }
            else
            {
                if (Input.GetKey(KeyCode.UpArrow)) return 1;
                if (Input.GetKey(KeyCode.DownArrow)) return 2;
                if (Input.GetKey(KeyCode.RightArrow)) return 3;
                if (Input.GetKey(KeyCode.LeftArrow)) return 4;
                if (Input.GetKey(KeyCode.RightBracket)) return 6;
                if (Input.GetKey(KeyCode.LeftBracket)) return 5;
            }

            return 0;
        }
    }
}
