using Unity.MLAgents.Actuators;
using Unity.MLAgents.Sensors;
using UnityEngine;

public class PlayerAgent : BaseAgent
{
    #region Exposed Instance Variables

    [SerializeField]
    private float speed = 10.0f;

    [SerializeField]
    private GameObject target;

    [SerializeField]
    private float distanceRequired = 1.5f;

    #endregion

    #region Private Instance Variables

    private Rigidbody playerRigidbody;

    private Vector3 originalPosition;
    private Vector3 originalTargetPosition;

    #endregion

    public override void Initialize()
    {
        playerRigidbody = GetComponent<Rigidbody>();
        originalPosition = transform.localPosition;

        if (target != null)
        {
            originalTargetPosition = target.transform.localPosition;
        }
    }

    public override void OnEpisodeBegin()
    {
        // Reset vận tốc để Agent không giữ quán tính từ episode trước
        playerRigidbody.linearVelocity = Vector3.zero;
        playerRigidbody.angularVelocity = Vector3.zero;

        if (target != null)
        {
            target.transform.localPosition = originalTargetPosition;
        }

        transform.localPosition = new Vector3(
            Random.Range(-4.0f, 4.0f),
            originalPosition.y,
            originalPosition.z
        );

        if (target != null)
        {
            transform.LookAt(target.transform);
        }
    }

    public override void CollectObservations(VectorSensor sensor)
    {
        // 3 observations: x, y, z
        sensor.AddObservation(transform.localPosition);

        // 3 observations: x, y, z
        sensor.AddObservation(target.transform.localPosition);

        // 2 observations: vận tốc x và z
        sensor.AddObservation(playerRigidbody.linearVelocity.x);
        sensor.AddObservation(playerRigidbody.linearVelocity.z);
    }

    public override void OnActionReceived(ActionBuffers actions)
    {
        ActionSegment<float> continuousActions =
            actions.ContinuousActions;

        float moveX = Mathf.Clamp(
            continuousActions[0],
            -1.0f,
            1.0f
        );

        float moveZ = Mathf.Clamp(
            continuousActions[1],
            -1.0f,
            1.0f
        );

        Vector3 vectorForce = new Vector3(
            moveX,
            0.0f,
            moveZ
        );

        playerRigidbody.AddForce(vectorForce * speed);

        float distanceFromTarget = Vector3.Distance(
            transform.localPosition,
            target.transform.localPosition
        );

        // Agent đến được mục tiêu
        if (distanceFromTarget < distanceRequired)
        {
            AddReward(1.0f);

            StartCoroutine(
                SwapGroundMaterial(successMaterial, 0.5f)
            );

            EndEpisode();
            return;
        }

        // Agent rơi khỏi mặt đất
        if (transform.localPosition.y < 0.0f)
        {
            AddReward(-1.0f);

            StartCoroutine(
                SwapGroundMaterial(failureMaterial, 0.5f)
            );

            EndEpisode();
        }
    }

    public override void Heuristic(in ActionBuffers actionsOut)
    {
        ActionSegment<float> continuousActions =
            actionsOut.ContinuousActions;

        continuousActions[0] = Input.GetAxis("Horizontal");
        continuousActions[1] = Input.GetAxis("Vertical");
    }
}