using System.IO;
using System.Linq;
using UnityEditor;
using UnityEngine;

namespace VanHuyen.RLGameEnvs.EditorTools
{
    /// <summary>
    /// Chép các tệp cấu hình huấn luyện của gói ra thư mục <c>config/</c> ở gốc dự
    /// án — nơi <c>mlagents-learn</c> thường được gọi tới.
    ///
    /// Vì sao phải chép ra ngoài thay vì trỏ thẳng vào gói: chương trình huấn luyện
    /// là một tiến trình Python nằm ngoài Unity, còn thư mục gói có thể nằm trong
    /// cache toàn cục (đường dẫn dài, có băm phiên bản) hoặc ở chế độ chỉ đọc. Chép
    /// ra <c>config/</c> cho người dùng một chỗ ổn định để sửa siêu tham số.
    /// </summary>
    public static class TrainingConfigInstaller
    {
        private const string SourceDir = "Packages/com.vanhuyen.rl-game-envs/Configs";

        [MenuItem("Tools/RL Game Environments/Cài cấu hình huấn luyện vào config/")]
        public static void Install()
        {
            string source = Path.GetFullPath(SourceDir);

            if (!Directory.Exists(source))
            {
                Debug.LogError($"[RLGameEnvs] Không thấy thư mục cấu hình: {source}");
                return;
            }

            string target = Path.Combine(Directory.GetCurrentDirectory(), "config");
            Directory.CreateDirectory(target);

            string[] files = Directory.GetFiles(source, "*.yaml");
            int copied = 0, skipped = 0;

            foreach (string file in files)
            {
                string dest = Path.Combine(target, Path.GetFileName(file));

                // Không ghi đè: người dùng có thể đã chỉnh siêu tham số của mình
                if (File.Exists(dest))
                {
                    skipped++;
                    continue;
                }

                File.Copy(file, dest);
                copied++;
            }

            Debug.Log($"[RLGameEnvs] Đã chép {copied} tệp cấu hình vào {target}"
                + (skipped > 0 ? $" ({skipped} tệp đã có sẵn nên giữ nguyên)." : "."));

            if (files.Length == 0)
            {
                Debug.LogWarning("[RLGameEnvs] Thư mục Configs của gói đang rỗng.");
            }
        }

        /// <summary>Số tệp cấu hình gói đang mang theo (dùng cho Setup Wizard).</summary>
        public static int AvailableCount()
        {
            string source = Path.GetFullPath(SourceDir);
            return Directory.Exists(source)
                ? Directory.GetFiles(source, "*.yaml").Length
                : 0;
        }
    }
}
