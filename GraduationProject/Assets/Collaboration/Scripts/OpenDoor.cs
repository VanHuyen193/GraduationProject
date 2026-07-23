using UnityEngine;

public class OpenDoor : MonoBehaviour
{
    public GameObject door;
    private Animator anim;

    public bool isPressed = false;

    // (fix 2) Cửa mở NÁN LẠI bao lâu (giây mô phỏng) sau khi agent rời plate.
    // Tạo khoảng đệm cho pha bàn giao (handoff) — agent giữ Plate0 có thể rời ra và
    // cửa vẫn mở đủ lâu để đồng đội kịp lên Plate1 giữ tiếp.
    // Cố ý để NGẮN: 1 agent KHÔNG thể tự chạy từ Plate0 (Z=-47) qua cổng (Z=-28, ~19
    // unit) trước khi cửa đóng, nên vẫn bắt buộc hai agent hợp tác.
    public float graceSeconds = 1.0f;

    // Đếm ngược đóng cửa; < 0 nghĩa là không đếm (đang có agent trên plate).
    private float releaseTimer = -1f;

    void Start()
    {
        anim = door.GetComponent<Animator>();
    }

    void OnTriggerStay(Collider other)
    {
        if (other.tag == "Agent")
        {
            anim.SetBool("Opening", true);
            isPressed = true;
            // Có agent trên plate -> hủy mọi đếm ngược đóng cửa
            releaseTimer = -1f;
        }
    }

    void OnTriggerExit(Collider other)
    {
        if (other.tag == "Agent")
        {
            // Không đóng ngay: bắt đầu đếm ngược grace period.
            // (Nếu agent khác vẫn đứng trên plate, OnTriggerStay sẽ đặt lại -1 ở step sau.)
            if (releaseTimer < 0f)
            {
                releaseTimer = graceSeconds;
            }
        }
    }

    void FixedUpdate()
    {
        if (releaseTimer > 0f)
        {
            releaseTimer -= Time.fixedDeltaTime;
            if (releaseTimer <= 0f)
            {
                releaseTimer = -1f;
                isPressed = false;
                anim.SetBool("Opening", false);
            }
        }
    }
}
