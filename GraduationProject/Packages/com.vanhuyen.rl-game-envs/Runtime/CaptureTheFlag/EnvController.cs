using System;
using System.Collections.Generic;
using Unity.MLAgents;
using UnityEngine;

public class EnvController : MonoBehaviour
{
    // Lưu thông tin của từng agent trong môi trường
    [System.Serializable]
    public class AgentInfo
    {
        // Reference tới PuzzleAgent
        public PuzzleAgent agent;

        // Vị trí ban đầu của agent
        [HideInInspector]
        public Vector3 StartingPos;

        // Rotation ban đầu của agent
        [HideInInspector]
        public Quaternion StartingRot;

        // Rigidbody của agent
        [HideInInspector]
        public Rigidbody Rb;

        // Khoảng cách từ agent tới pressure plate 0
        [HideInInspector]
        public float distanceToPlate0;

        // Khoảng cách từ agent tới pressure plate 1
        [HideInInspector]
        public float distanceToPlate1;

        // Khoảng cách tới checkpoint ở step trước (dùng cho reward shaping theo khoảng cách)
        [HideInInspector]
        public float prevDistToCheckpoint;

        // Trạng thái ThisAgentLeft ở step trước (để phát hiện thời điểm VỪA vượt cổng)
        [HideInInspector]
        public bool prevLeft;

        // Đã được thưởng handoff trong episode này chưa (mỗi agent tối đa 1 lần)
        [HideInInspector]
        public bool handoffCredited;
    }

    // Danh sách tất cả agent trong environment
    public List<AgentInfo> agents = new List<AgentInfo>();

    // Bộ đếm số bước của environment
    private int resetTimer;

    // Số bước tối đa trước khi reset episode
    public int MaxEnvironmentSteps = 50000;

    // Nhóm multi-agent dùng để training cooperative
    public SimpleMultiAgentGroup agentGroup;

    // Block cần được đẩy
    private GameObject block;

    // Vị trí ban đầu của block
    private Vector3 blockStartingPos;

    // Rotation ban đầu của block
    private Quaternion blockStartingRot;

    // ============================================================
    // Reward shaping (mục a) — các hệ số để tinh chỉnh trong Inspector
    // ============================================================

    // (mục 2) Hệ số thưởng theo mức GIẢM khoảng cách tới checkpoint.
    // KHÔNG chia cho MaxEnvironmentSteps: reward này tự giới hạn theo tổng quãng
    // đường (dạng potential-based) nên không bị "farm" khi đi tới-lui.
    public float distanceRewardScale = 0.01f;

    // (mục 1 — DIET FARMING) Thưởng MỘT LẦN cho mỗi agent khi vượt được cổng ĐANG KHÓA
    // (chỉ có thể nhờ đồng đội giữ cửa). Không lặp trong episode nên KHÔNG farm được,
    // thay cho handoff bonus mỗi-step cũ (vốn có thể farm tới ~+2).
    public float handoffReward = 0.5f;

    // Thưởng nhỏ khi agent đứng trên plate (khuyến khích tương tác với plate).
    public float platePresenceBonus = 0.5f;

    // Phạt thời gian nhẹ (Hurry Up) — nhỏ hơn nhiều bản gốc để không lấn át tín hiệu dẫn đường.
    public float timePenalty = 0.1f;

    // Ngưỡng khoảng cách để coi là "đang đứng trên plate".
    public float onPlateRadius = 2.25f;

    // Transform của checkpoint (đích đến) — tìm trong Start.
    private Transform checkpoint;

    // 2 cánh cửa (Left Side / Right Side). Curriculum có thể tắt để "mở cửa sẵn" ở bài học đầu.
    private GameObject[] doorLeaves = new GameObject[0];

    // Cửa hiện có đang khóa không (Lesson >=1). Chỉ thưởng handoff khi cửa khóa —
    // lúc đó việc vượt cổng mới thực sự cần đồng đội giữ cửa.
    private bool doorLocked = true;

    // (mục b) Tên tham số curriculum điều khiển cửa: 1 = khóa (bắt buộc handoff), 0 = mở sẵn.
    private const string HANDOFF_PARAM = "handoff_required";

    // Start được gọi trước frame đầu tiên
    void Start()
    {
        // Khởi tạo group cho multi-agent
        agentGroup = new SimpleMultiAgentGroup();

        // Lưu thông tin ban đầu của từng agent
        foreach (AgentInfo agent in agents)
        {
            // Lưu vị trí spawn
            agent.StartingPos = agent.agent.transform.position;

            // Lưu rotation ban đầu
            agent.StartingRot = agent.agent.transform.rotation;

            // Lấy Rigidbody
            agent.Rb = agent.agent.GetComponent<Rigidbody>();

            // Đăng ký agent vào group
            agentGroup.RegisterAgent(agent.agent);
        }

        // Tìm object Block là child của environment
        block = transform.Find("Block").gameObject;

        if (block != null)
        {
            // Lưu trạng thái ban đầu của block
            blockStartingPos = block.transform.position;
            blockStartingRot = block.transform.rotation;
        }
        else
        {
            Debug.LogError("Block not found in the environment hierarchy.");
        }

        // Tìm checkpoint (đích) để tính reward shaping theo khoảng cách
        checkpoint = FindChildByTag(transform, "checkpoint");
        if (checkpoint == null)
        {
            Debug.LogError("Checkpoint not found in the environment hierarchy.");
        }

        // Tìm 2 cánh cửa (Left Side / Right Side) để curriculum có thể mở sẵn cửa
        Transform doorRoot = FindChildByName(transform, "Door");
        if (doorRoot != null)
        {
            List<GameObject> leaves = new List<GameObject>();
            Transform ls = FindChildByName(doorRoot, "Left Side");
            Transform rs = FindChildByName(doorRoot, "Right Side");
            if (ls != null) leaves.Add(ls.gameObject);
            if (rs != null) leaves.Add(rs.gameObject);
            doorLeaves = leaves.ToArray();
        }

        // Khởi tạo khoảng cách tham chiếu tới checkpoint cho từng agent
        InitPrevDistances();

        // Áp dụng curriculum cửa ngay từ đầu (bài học hiện tại)
        ApplyDoorCurriculum();
    }

    void FixedUpdate()
    {
        // Tăng số bước của environment
        resetTimer += 1;

        // Nếu vượt quá số bước tối đa thì kết thúc episode
        if (resetTimer >= MaxEnvironmentSteps && MaxEnvironmentSteps > 0)
        {
            agentGroup.GroupEpisodeInterrupted();
            ResetScene();
            return;
        }

        // Trạng thái "đang đứng trên plate" của từng agent trong step này
        bool[] onPlate = new bool[agents.Count];

        // Duyệt qua tất cả agent
        for (int i = 0; i < agents.Count; i++)
        {
            // Tính khoảng cách tới plate 0
            agents[i].distanceToPlate0 =
                Vector3.Distance(
                    agents[i].agent.transform.position,
                    agents[i].agent.pressurePlates[0].transform.position
                );

            // Tính khoảng cách tới plate 1
            agents[i].distanceToPlate1 =
                Vector3.Distance(
                    agents[i].agent.transform.position,
                    agents[i].agent.pressurePlates[1].transform.position
                );

            // Agent có đang đứng trên (gần) một plate nào đó không
            onPlate[i] =
                agents[i].distanceToPlate0 < onPlateRadius ||
                agents[i].distanceToPlate1 < onPlateRadius;

            // (mục 2) REWARD SHAPING THEO KHOẢNG CÁCH tới checkpoint:
            // thưởng khi lại gần, phạt khi ra xa. Đây là gradient dẫn đường xuyên suốt
            // bản đồ (spawn -> cổng -> checkpoint), lấp các đoạn trước đây không có tín hiệu.
            // Agent đứng yên giữ plate => chênh lệch ~0 => KHÔNG bị phạt.
            if (checkpoint != null)
            {
                float d = Vector3.Distance(
                    agents[i].agent.transform.position,
                    checkpoint.position
                );
                agents[i].agent.AddReward(
                    distanceRewardScale * (agents[i].prevDistToCheckpoint - d)
                );
                agents[i].prevDistToCheckpoint = d;
            }

            // Thưởng nhỏ khi agent đứng trên plate (khuyến khích dùng plate để mở cửa)
            if (onPlate[i])
            {
                agents[i].agent.AddReward(
                    platePresenceBonus / MaxEnvironmentSteps
                );
            }

        }

        // (mục 1 — DIET FARMING) THƯỞNG HANDOFF MỘT LẦN:
        // Khi một agent VỪA vượt cổng (prevLeft=false -> ThisAgentLeft=true) trong lúc
        // cửa đang KHÓA, việc vượt được chỉ có thể nhờ đồng đội giữ cửa (hoặc grace
        // period ngắn sau khi đồng đội rời plate). Thưởng nhóm MỘT LẦN cho mỗi agent
        // (không lặp trong episode) => tín hiệu hợp tác mạnh mà KHÔNG farm được.
        for (int i = 0; i < agents.Count; i++)
        {
            bool justCrossed =
                !agents[i].prevLeft && agents[i].agent.ThisAgentLeft;

            if (justCrossed && !agents[i].handoffCredited && doorLocked)
            {
                agentGroup.AddGroupReward(handoffReward);
                agents[i].handoffCredited = true;
            }

            agents[i].prevLeft = agents[i].agent.ThisAgentLeft;
        }

        // Phạt thời gian nhẹ (Hurry Up Penalty) — nhỏ để không lấn át tín hiệu dẫn đường.
        agentGroup.AddGroupReward(
            -timePenalty / MaxEnvironmentSteps
        );
    }

    void Update()
    {

    }

    // Reset toàn bộ environment
    private void ResetScene()
    {
        // Reset step counter
        resetTimer = 0;

        // Reset từng agent
        foreach (AgentInfo agent in agents)
        {
            // Reset vị trí
            agent.agent.transform.position =
                agent.StartingPos;

            // Reset rotation
            agent.agent.transform.rotation =
                agent.StartingRot;

            // Reset velocity
            agent.Rb.linearVelocity = Vector3.zero;

            // Reset angular velocity
            agent.Rb.angularVelocity = Vector3.zero;

            // Reset trạng thái
            agent.agent.ThisAgentLeft = false;
            agent.agent.FoundCheckpoint = false;

            // Reset trạng thái phục vụ reward handoff một-lần
            agent.prevLeft = false;
            agent.handoffCredited = false;
        }

        // Reset block
        if (block != null)
        {
            // Reset vị trí
            block.transform.position = blockStartingPos;

            // Reset rotation
            block.transform.rotation = blockStartingRot;

            // Reset rigidbody của block
            Rigidbody blockRb = block.GetComponent<Rigidbody>();

            if (blockRb != null)
            {
                blockRb.linearVelocity = Vector3.zero;
                blockRb.angularVelocity = Vector3.zero;
            }
        }

        // Reset khoảng cách tham chiếu cho reward shaping (sau khi agent đã về vị trí spawn)
        InitPrevDistances();

        // Cập nhật trạng thái cửa theo curriculum của bài học hiện tại
        ApplyDoorCurriculum();
    }

    // Được gọi khi agent tìm thấy checkpoint
    public void FoundCheckpoint(Collider cpCol, float reward)
    {
        // Kiểm tra tất cả agent đã tới checkpoint chưa
        bool allFound = true;

        foreach (AgentInfo agent in agents)
        {
            if (!agent.agent.FoundCheckpoint)
            {
                allFound = false;
                break;
            }
        }

        // Nếu tất cả agent đã tới checkpoint
        if (allFound)
        {
            Debug.Log("All agents found checkpoint");

            // Thưởng cho group
            agentGroup.AddGroupReward(reward);

            // Kết thúc episode
            agentGroup.EndGroupEpisode();

            // Reset environment
            ResetScene();
        }
    }

    // Được gọi khi agent đẩy block
    public void PushingBlock(Collision col)
    {
        // Debug.Log("Pushing Block");

        // Thưởng agent đang đẩy block
        col.gameObject
            .GetComponent<PuzzleAgent>()
            .AddReward(0.25f / MaxEnvironmentSteps);
    }

    // ============================================================
    // Helper
    // ============================================================

    // Khởi tạo / reset khoảng cách tham chiếu tới checkpoint cho từng agent
    private void InitPrevDistances()
    {
        if (checkpoint == null) return;

        foreach (AgentInfo agent in agents)
        {
            agent.prevDistToCheckpoint = Vector3.Distance(
                agent.agent.transform.position,
                checkpoint.position
            );
        }
    }

    // (mục b) Bật/tắt 2 cánh cửa theo tham số curriculum:
    //   handoff_required >= 0.5  -> cửa TỒN TẠI (khóa) -> bắt buộc học handoff
    //   handoff_required <  0.5  -> tắt cánh cửa (mở sẵn) -> chỉ cần đi tới checkpoint
    private void ApplyDoorCurriculum()
    {
        float locked = 1f;
        if (Academy.IsInitialized)
        {
            locked = Academy.Instance.EnvironmentParameters
                .GetWithDefault(HANDOFF_PARAM, 1f);
        }

        bool doorActive = locked >= 0.5f;
        doorLocked = doorActive;

        if (doorLeaves == null || doorLeaves.Length == 0) return;

        foreach (GameObject leaf in doorLeaves)
        {
            if (leaf != null && leaf.activeSelf != doorActive)
            {
                leaf.SetActive(doorActive);
            }
        }
    }

    // Tìm con (kể cả cháu) đầu tiên có đúng tag
    private Transform FindChildByTag(Transform root, string tg)
    {
        foreach (Transform t in root.GetComponentsInChildren<Transform>(true))
        {
            if (t != root && t.CompareTag(tg)) return t;
        }
        return null;
    }

    // Tìm con (kể cả cháu) đầu tiên có đúng tên
    private Transform FindChildByName(Transform root, string n)
    {
        foreach (Transform t in root.GetComponentsInChildren<Transform>(true))
        {
            if (t != root && t.name == n) return t;
        }
        return null;
    }
}
