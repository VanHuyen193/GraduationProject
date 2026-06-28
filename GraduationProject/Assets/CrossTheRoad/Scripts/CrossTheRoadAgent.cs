using TMPro;
using Unity.MLAgents.Actuators;
using Unity.MLAgents.Sensors;
using UnityEngine;

public class CrossTheRoadAgent : BaseAgent
{
    [SerializeField]
    private float speed = 50.0f;

    [SerializeField]
    [Tooltip("Khoảng cách Agent di chuyển trong mỗi lần thực hiện action")]
    private float stepAmount = 1.0f;

    [SerializeField]
    private TextMeshProUGUI rewardValue;

    [SerializeField]
    private TextMeshProUGUI episodesValue;

    [SerializeField]
    private TextMeshProUGUI stepValue;

    private CrossTheRoadGoal goal;

    private float overallReward;
    private float overallSteps;

    private Vector3 moveTo;
    private Vector3 originalPosition;

    private Rigidbody agentRigidbody;

    private bool moveInProgress;
    private int direction;

    public enum MoveToDirection
    {
        Idle,
        Left,
        Right,
        Forward
    }

    private MoveToDirection moveToDirection = MoveToDirection.Idle;

    private void Awake()
    {
        goal = transform.parent.GetComponentInChildren<CrossTheRoadGoal>();
        originalPosition = transform.localPosition;
        agentRigidbody = GetComponent<Rigidbody>();
    }

    public override void OnEpisodeBegin()
    {
        transform.localPosition = originalPosition;
        transform.localRotation = Quaternion.identity;

        moveTo = originalPosition;
        moveInProgress = false;
        moveToDirection = MoveToDirection.Idle;
        direction = 0;

        agentRigidbody.linearVelocity = Vector3.zero;
        agentRigidbody.angularVelocity = Vector3.zero;
    }

    public override void CollectObservations(VectorSensor sensor)
    {
        // 3 observations: x, y, z
        sensor.AddObservation(transform.localPosition);

        // 3 observations: x, y, z
        sensor.AddObservation(goal.transform.localPosition);
    }

    private void Update()
    {
        if (!moveInProgress)
        {
            return;
        }

        transform.localPosition = Vector3.MoveTowards(
            transform.localPosition,
            moveTo,
            Time.deltaTime * speed
        );

        if (Vector3.Distance(transform.localPosition, moveTo) <= 0.00001f)
        {
            transform.localPosition = moveTo;
            moveInProgress = false;
        }
    }

    public override void OnActionReceived(ActionBuffers actions)
    {
        if (moveInProgress)
        {
            return;
        }

        direction = actions.DiscreteActions[0];

        Vector3 currentPosition = transform.localPosition;

        switch (direction)
        {
            case 0:
                moveTo = currentPosition;
                moveToDirection = MoveToDirection.Idle;
                break;

            case 1:
                moveTo = new Vector3(
                    currentPosition.x - stepAmount,
                    currentPosition.y,
                    currentPosition.z
                );

                moveToDirection = MoveToDirection.Left;
                moveInProgress = true;
                break;

            case 2:
                moveTo = new Vector3(
                    currentPosition.x + stepAmount,
                    currentPosition.y,
                    currentPosition.z
                );

                moveToDirection = MoveToDirection.Right;
                moveInProgress = true;
                break;

            case 3:
                moveTo = new Vector3(
                    currentPosition.x,
                    currentPosition.y,
                    currentPosition.z + stepAmount
                );

                moveToDirection = MoveToDirection.Forward;
                moveInProgress = true;
                break;

            default:
                moveTo = currentPosition;
                moveToDirection = MoveToDirection.Idle;
                moveInProgress = false;
                break;
        }
    }

    public override void Heuristic(in ActionBuffers actionsOut)
    {
        ActionSegment<int> discreteActions =
            actionsOut.DiscreteActions;

        // Mặc định đứng yên
        discreteActions[0] = 0;

        if (Input.GetKeyDown(KeyCode.LeftArrow))
        {
            discreteActions[0] = 1;
        }
        else if (Input.GetKeyDown(KeyCode.RightArrow))
        {
            discreteActions[0] = 2;
        }
        else if (Input.GetKeyDown(KeyCode.UpArrow))
        {
            discreteActions[0] = 3;
        }
    }

    public void GivePoints()
    {
        AddReward(1.0f);

        UpdateStats();

        StartCoroutine(
            SwapGroundMaterial(successMaterial, 0.5f)
        );

        EndEpisode();
    }

    public void TakeAwayPoints()
    {
        AddReward(-0.025f);

        UpdateStats();

        StartCoroutine(
            SwapGroundMaterial(failureMaterial, 0.5f)
        );

        EndEpisode();
    }

    private void UpdateStats()
    {
        overallReward += GetCumulativeReward();
        overallSteps += StepCount;

        if (rewardValue != null)
        {
            rewardValue.text = overallReward.ToString("F2");
        }

        if (episodesValue != null)
        {
            episodesValue.text = CompletedEpisodes.ToString();
        }

        if (stepValue != null)
        {
            stepValue.text = overallSteps.ToString("F0");
        }
    }
}