using System.Collections.Generic;
using System.Linq;
using UnityEngine;
using Unity.MLAgents;
using Unity.MLAgents.Sensors;
using Unity.MLAgents.Actuators;
using Unity.VisualScripting;

public class PuzzleAgent : Agent
{
    // Danh sách các pressure plate trong môi trường
    [HideInInspector]
    public GameObject[] pressurePlates;

    // Rigidbody dùng để điều khiển vật lý của agent
    private Rigidbody rBody;

    // Sensor dùng để thêm observation
    private VectorSensorComponent goalSensor;

    [SerializeField]
    // Tốc độ di chuyển của agent
    private float moveSpeed = 10f;

    // Vị trí ban đầu của agent
    private Vector3 initialPosition;

    // Agent đã tìm thấy checkpoint hay chưa
    [HideInInspector]
    public bool FoundCheckpoint = false;

    // Agent đã rời khỏi khu vực đầu tiên hay chưa
    [HideInInspector]
    public bool ThisAgentLeft = false;

    protected override void Awake()
    {
        base.Awake();

        // Có thể đặt MaxStep = 0 để agent không tự kết thúc episode
        // MaxStep = 0;

        // Lưu vị trí spawn ban đầu
        initialPosition = transform.localPosition;
    }

    public override void Initialize()
    {
        // Lấy Rigidbody của agent
        rBody = GetComponent<Rigidbody>();

        // Lấy sensor component
        goalSensor = GetComponent<VectorSensorComponent>();

        // Lấy object cha của agent
        Transform parent = transform.parent;

        // Tìm tất cả object có tag "plate"
        pressurePlates = parent.GetComponentsInChildren<Transform>()
                        .Where(child => child.CompareTag("plate"))
                        .Select(child => child.gameObject)
                        .OrderBy(plate => plate.name)
                        .ToArray();

        // Kiểm tra xem có đủ pressure plate không
        if (pressurePlates.Length < 2)
        {
            Debug.LogError("Not enough pressure plates found!");
            return;
        }
    }

    public override void OnEpisodeBegin()
    {
        // Reset velocity của agent
        this.rBody.linearVelocity = Vector3.zero;

        // Reset vị trí agent về vị trí ban đầu
        this.transform.localPosition = initialPosition;
    }

    public override void CollectObservations(VectorSensor sensor)
    {
        // Quan sát trạng thái pressure plate thứ nhất
        sensor.AddObservation(
            pressurePlates[0].GetComponent<OpenDoor>().isPressed
        );

        // Quan sát trạng thái pressure plate thứ hai
        sensor.AddObservation(
            pressurePlates[1].GetComponent<OpenDoor>().isPressed
        );

        // Quan sát trạng thái checkpoint
        goalSensor.GetSensor().AddObservation(FoundCheckpoint);
    }

    public override void OnActionReceived(ActionBuffers actionBuffers)
    {
        // Nhận action từ neural network
        MoveAgent(actionBuffers.DiscreteActions);
    }

    public void MoveAgent(ActionSegment<int> act)
    {
        // Vector di chuyển
        var dirToGo = Vector3.zero;

        // Vector xoay
        var rotateDir = Vector3.zero;

        // Action được chọn
        var action = act[0];

        switch (action)
        {
            // Đi tới
            case 1:
                dirToGo = transform.forward * 1f;
                break;

            // Đi lùi
            case 2:
                dirToGo = transform.forward * -1f;
                break;

            // Xoay phải
            case 3:
                rotateDir = transform.up * 1f;
                break;

            // Xoay trái
            case 4:
                rotateDir = transform.up * -1f;
                break;

            // Đi ngang trái
            case 5:
                dirToGo = transform.right * -0.75f;
                break;

            // Đi ngang phải
            case 6:
                dirToGo = transform.right * 0.75f;
                break;
        }

        // Xoay agent
        transform.Rotate(rotateDir, Time.fixedDeltaTime * 200f);

        // Thêm lực để di chuyển agent
        rBody.AddForce(
            dirToGo * moveSpeed,
            ForceMode.VelocityChange
        );
    }

    public override void Heuristic(in ActionBuffers actionsOut)
    {
        // Điều khiển bằng bàn phím để test agent
        var discreteActionsOut = actionsOut.DiscreteActions;

        // Chế độ LLM (GameHub): action do mô hình ngôn ngữ lớn quyết định,
        // giữ nguyên giữa 2 lần trả lời (di chuyển bằng lực cần bấm giữ)
        var llmDriver = GetComponent<GameHub.LLMPuzzleDriver>();

        if (llmDriver != null)
        {
            discreteActionsOut[0] = llmDriver.CurrentAction;
            return;
        }

        // Chế độ người chơi (GameHub): dùng sơ đồ phím riêng (WASD / mũi tên)
        // để 2 người chơi có thể điều khiển 2 agent trên cùng bàn phím
        var humanInput = GetComponent<GameHub.PuzzleHumanInput>();

        if (humanInput != null)
        {
            discreteActionsOut[0] = humanInput.GetAction();
            return;
        }

        // D -> xoay phải
        if (Input.GetKey(KeyCode.D))
        {
            discreteActionsOut[0] = 3;
        }

        // W -> đi tới
        else if (Input.GetKey(KeyCode.W))
        {
            discreteActionsOut[0] = 1;
        }

        // A -> xoay trái
        else if (Input.GetKey(KeyCode.A))
        {
            discreteActionsOut[0] = 4;
        }

        // S -> đi lùi
        else if (Input.GetKey(KeyCode.S))
        {
            discreteActionsOut[0] = 2;
        }
    }

    // Được gọi khi agent rời khu vực đầu tiên
    public void LeftFirstStage(Collider col, float reward)
    {
        // Kiểm tra collider có phải agent này không
        if (col.gameObject.GetComponent<PuzzleAgent>() == this)
        {
            ThisAgentLeft = true;
        }
    }

    // Được gọi khi agent quay lại khu vực đầu tiên
    public void EnteredFirstStage(Collider col, float reward)
    {
        // Kiểm tra collider có phải agent này không
        if (col.gameObject.GetComponent<PuzzleAgent>() == this)
        {
            ThisAgentLeft = false;
        }
    }
}