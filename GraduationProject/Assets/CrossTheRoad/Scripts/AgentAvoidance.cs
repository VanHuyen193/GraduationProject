using TMPro;
using Unity.MLAgents.Actuators;
using Unity.MLAgents.Sensors;
using UnityEngine;

public class AgentAvoidance : BaseAgent
{
    [SerializeField]
    private float speed = 50.0f;

    [SerializeField]
    private Vector3 idlePosition = Vector3.zero;

    [SerializeField]
    private Vector3 leftPosition = Vector3.zero;

    [SerializeField]
    private Vector3 rightPosition = Vector3.zero;

    [SerializeField]
    private TextMeshProUGUI rewardValue = null;

    [SerializeField]
    private TextMeshProUGUI episodesValue = null;

    [SerializeField]
    private TextMeshProUGUI stepValue = null;

    private TargetMoving targetMoving;

    private float overallReward;
    private float overallSteps;

    private Vector3 moveTo;
    private Vector3 prevPosition;

    private int punishCounter;

    private void Awake()
    {
        targetMoving =
            transform.parent.GetComponentInChildren<TargetMoving>();
    }

    public override void OnEpisodeBegin()
    {
        transform.localPosition = idlePosition;

        moveTo = idlePosition;
        prevPosition = idlePosition;
        punishCounter = 0;
    }

    public override void CollectObservations(VectorSensor sensor)
    {
        // 3 observations: x, y, z
        sensor.AddObservation(transform.localPosition);

        // 3 observations: x, y, z
        sensor.AddObservation(targetMoving.transform.localPosition);
    }

    public override void OnActionReceived(ActionBuffers actions)
    {
        ActionSegment<int> discreteActions =
            actions.DiscreteActions;

        prevPosition = moveTo;

        int direction = discreteActions[0];

        switch (direction)
        {
            case 0:
                moveTo = idlePosition;
                break;

            case 1:
                moveTo = leftPosition;
                break;

            case 2:
                moveTo = rightPosition;
                break;

            default:
                moveTo = idlePosition;
                break;
        }

        transform.localPosition = Vector3.MoveTowards(
            transform.localPosition,
            moveTo,
            Time.fixedDeltaTime * speed
        );

        if (prevPosition == moveTo)
        {
            punishCounter++;
        }
        else
        {
            punishCounter = 0;
        }

        if (punishCounter > 3)
        {
            AddReward(-0.01f);
            punishCounter = 0;
        }
    }

    public override void Heuristic(in ActionBuffers actionsOut)
    {
        ActionSegment<int> discreteActions =
            actionsOut.DiscreteActions;

        // Mặc định đứng yên
        discreteActions[0] = 0;

        if (Input.GetKey(KeyCode.LeftArrow))
        {
            discreteActions[0] = 1;
        }
        else if (Input.GetKey(KeyCode.RightArrow))
        {
            discreteActions[0] = 2;
        }
        else if (Input.GetKey(KeyCode.DownArrow))
        {
            discreteActions[0] = 0;
        }
    }

    public void TakeAwayPoints()
    {
        AddReward(-0.01f);

        UpdateStats();

        targetMoving.ResetTarget();

        StartCoroutine(
            SwapGroundMaterial(failureMaterial, 0.5f)
        );

        EndEpisode();
    }

    public void GivePoints()
    {
        AddReward(1.0f);

        UpdateStats();

        targetMoving.ResetTarget();

        StartCoroutine(
            SwapGroundMaterial(successMaterial, 0.5f)
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