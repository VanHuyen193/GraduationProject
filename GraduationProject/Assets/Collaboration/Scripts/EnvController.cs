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
        }

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

            // Nếu agent đứng trên 1 pressure plate thì thưởng nhỏ
            if (agents[i].distanceToPlate0 < 2.25f ||
                agents[i].distanceToPlate1 < 2.25f)
            {
                agents[i].agent.AddReward(
                    0.25f / MaxEnvironmentSteps
                );
            }

            // Nếu agent đã rời phòng đầu tiên thì thưởng nhỏ
            if (agents[i].agent.ThisAgentLeft)
            {
                agents[i].agent.AddReward(
                    0.5f / MaxEnvironmentSteps
                );
            }

            // Nếu agent hiện tại đang đứng trên plate
            // nhưng agent còn lại chưa rời phòng
            if (
                !agents[1 - i].agent.ThisAgentLeft &&
                (
                    agents[i].distanceToPlate0 < 2.25f ||
                    agents[i].distanceToPlate1 < 2.25f
                )
            )
            {
                // Trừ reward của cả nhóm
                agentGroup.AddGroupReward(
                    -2 / MaxEnvironmentSteps
                );

                // Trừ reward của agent còn lại
                agents[1 - i].agent.AddReward(
                    -0.5f / MaxEnvironmentSteps
                );

                // Debug.Log("Other agent still in the room while this agent is on the plate");
            }

            // Nếu agent kia đã ra ngoài nhưng agent hiện tại vẫn ở trong phòng
            else if (
                agents[1 - i].agent.ThisAgentLeft &&
                !agents[i].agent.ThisAgentLeft
            )
            {
                // Phạt group
                agentGroup.AddGroupReward(
                    -4 / MaxEnvironmentSteps
                );

                // Phạt agent hiện tại
                agents[i].agent.AddReward(
                    -1 / MaxEnvironmentSteps
                );

                // Debug.Log("Other agent left the room and this one is still in the room");
            }
        }

        // Nếu cả 2 agent đều đã rời phòng
        if (
            agents[0].agent.ThisAgentLeft &&
            agents[1].agent.ThisAgentLeft
        )
        {
            // Thưởng group
            agentGroup.AddGroupReward(
                0.5f / MaxEnvironmentSteps
            );

            // Debug.Log("Both agents left the room");
        }

        // Phạt theo thời gian để agent hoàn thành nhiệm vụ nhanh hơn
        // Hurry Up Penalty
        agentGroup.AddGroupReward(
            -0.25f / MaxEnvironmentSteps
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
}