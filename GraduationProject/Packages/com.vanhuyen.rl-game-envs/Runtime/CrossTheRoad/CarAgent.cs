using Unity.MLAgents.Actuators;
using Unity.MLAgents.Policies;
using Unity.MLAgents.Sensors;
using UnityEngine;
using static CarController;

public class CarAgent : BaseAgent
{
    private Vector3 originalPosition;

    private BehaviorParameters behaviorParameters;
    private CarController carController;
    private Rigidbody carControllerRigidBody;
    private CarSpots carSpots;

    private bool episodeEnding;

    public override void Initialize()
    {
        originalPosition = transform.localPosition;

        behaviorParameters = GetComponent<BehaviorParameters>();
        carController = GetComponent<CarController>();
        carControllerRigidBody = GetComponent<Rigidbody>();
        carSpots = transform.parent.GetComponentInChildren<CarSpots>();

        ResetParkingLotArea();
    }

    public override void OnEpisodeBegin()
    {
        ResetParkingLotArea();
    }

    private void ResetParkingLotArea()
    {
        episodeEnding = false;

        // Default: AI điều khiển
        // Heuristic Only: người chơi điều khiển
        carController.IsAutonomous =
            behaviorParameters.BehaviorType == BehaviorType.Default;

        transform.localPosition = originalPosition;
        transform.localRotation = Quaternion.identity;

        carControllerRigidBody.linearVelocity = Vector3.zero;
        carControllerRigidBody.angularVelocity = Vector3.zero;

        carController.CurrentDirection = Direction.Idle;

        carSpots.Setup();
    }

    private void Update()
    {
        if (!episodeEnding && transform.localPosition.y <= 0f)
        {
            TakeAwayPoints();
        }
    }

    public override void CollectObservations(VectorSensor sensor)
    {
        sensor.AddObservation(transform.localPosition);
        sensor.AddObservation(transform.localRotation);

        sensor.AddObservation(
            carSpots.CarGoal.transform.localPosition
        );

        sensor.AddObservation(
            carSpots.CarGoal.transform.localRotation
        );

        sensor.AddObservation(carControllerRigidBody.linearVelocity);
        sensor.AddObservation(carControllerRigidBody.angularVelocity);
    }

    public override void OnActionReceived(ActionBuffers actions)
    {
        if (episodeEnding)
        {
            return;
        }

        ActionSegment<int> discreteActions =
            actions.DiscreteActions;

        int direction = discreteActions[0];

        switch (direction)
        {
            case 0:
                carController.CurrentDirection = Direction.Idle;
                break;

            case 1:
                carController.CurrentDirection = Direction.MoveForward;
                break;

            case 2:
                carController.CurrentDirection = Direction.MoveBackward;
                break;

            case 3:
                carController.CurrentDirection = Direction.TurnLeft;
                break;

            case 4:
                carController.CurrentDirection = Direction.TurnRight;
                break;

            default:
                carController.CurrentDirection = Direction.Idle;
                break;
        }

        if (MaxStep > 0)
        {
            AddReward(-1f / MaxStep);
        }
    }

    public override void Heuristic(in ActionBuffers actionsOut)
    {
        ActionSegment<int> discreteActions =
            actionsOut.DiscreteActions;

        // Mặc định đứng yên
        discreteActions[0] = 0;

        if (Input.GetKey(KeyCode.UpArrow))
        {
            discreteActions[0] = 1;
        }
        else if (Input.GetKey(KeyCode.DownArrow))
        {
            discreteActions[0] = 2;
        }
        else if (
            Input.GetKey(KeyCode.LeftArrow) &&
            carController.canApplyTorque()
        )
        {
            discreteActions[0] = 3;
        }
        else if (
            Input.GetKey(KeyCode.RightArrow) &&
            carController.canApplyTorque()
        )
        {
            discreteActions[0] = 4;
        }
    }

    public void GivePoints(
        float amount = 1.0f,
        bool isFinal = false
    )
    {
        if (episodeEnding)
        {
            return;
        }

        AddReward(amount);

        if (!isFinal)
        {
            return;
        }

        episodeEnding = true;

        carController.CurrentDirection = Direction.Idle;

        StartCoroutine(
            SwapGroundMaterial(successMaterial, 0.5f)
        );

        EndEpisode();
    }

    public void TakeAwayPoints()
    {
        if (episodeEnding)
        {
            return;
        }

        episodeEnding = true;

        carController.CurrentDirection = Direction.Idle;

        AddReward(-0.01f);

        StartCoroutine(
            SwapGroundMaterial(failureMaterial, 0.5f)
        );

        EndEpisode();
    }
}