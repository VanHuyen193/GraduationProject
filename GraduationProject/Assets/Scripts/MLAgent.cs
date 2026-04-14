using UnityEngine;
using Unity.MLAgents;
using Unity.MLAgents.Sensors;
using Unity.MLAgents.Actuators;
using System.Collections;

public class MLAgent : Agent
{
    [SerializeField] private Transform _goal;
    [SerializeField] private Renderer _groundRenderer;
    [SerializeField] private float _moveSpeed = 1.5f;
    [SerializeField] private float _rotationSpeed = 180f;

    private Renderer _renderer;

    [HideInInspector] public int CurrentEpisode = 0;
    [HideInInspector] public float CumulativeReward = 0f;


    private Color _defaultGroundColor;
    private Coroutine _flashGroundCoroutine;
    public override void Initialize()
    {
        Debug.Log("Initialize()");

        _renderer = GetComponent<Renderer>();
        CurrentEpisode = 0;
        CumulativeReward = 0f;

        if (_groundRenderer != null)
        {
            _defaultGroundColor = _groundRenderer.material.color;
        }
    }

    public override void OnEpisodeBegin()
    {
        Debug.Log("OnEpisodeBegin()");

        if(_groundRenderer != null && CumulativeReward != 0f)
        {
            Color flashColor = (CumulativeReward > 0f) ? Color.green : Color.red;

            if (_flashGroundCoroutine != null)
            {
                StopCoroutine(_flashGroundCoroutine);
            }

            _flashGroundCoroutine = StartCoroutine(FlashGround(flashColor, 3.0f));
        }

        CurrentEpisode++;
        CumulativeReward = 0f;
        _renderer.material.color = Color.blue;

        SpawnObjects();
    }

    private IEnumerator FlashGround(Color targetColor, float duration)
    {
        float elapedTime = 0f;

        _groundRenderer.material.color = targetColor;

        while (elapedTime < duration)
        {
            elapedTime += Time.deltaTime;
            _groundRenderer.material.color = Color.Lerp(targetColor, _defaultGroundColor, elapedTime / duration);
            yield return null;
        }
    }

    private void SpawnObjects()
    {
        transform.localRotation = Quaternion.identity;
        transform.localPosition = new Vector3(0f, 0.15f, 0f);

        float randomAngle = Random.Range(0f, 360f);
        Vector3 randomDirection = Quaternion.Euler(0f, randomAngle, 0f) * Vector3.forward;

        float randomDistance = Random.Range(1f, 2.5f);

        Vector3 goalPosition = transform.localPosition + randomDirection * randomDistance;

        _goal.localPosition = new Vector3(goalPosition.x, 0.3f, goalPosition.z);
    }

    public override void CollectObservations(VectorSensor sensor)
    {
        float goalPosX_normalized = _goal.localPosition.x / 5f;
        float goalPosZ_normalized = _goal.localPosition.z / 5f;

        float agentPosX_normalized = transform.localPosition.x / 5f;
        float agentPosZ_normalized = transform.localPosition.z / 5f;

        float agentRotation_nomalized = (transform.localRotation.eulerAngles.y / 360f) * 2f - 1f;

        sensor.AddObservation(goalPosX_normalized);
        sensor.AddObservation(goalPosZ_normalized);
        sensor.AddObservation(agentPosX_normalized);
        sensor.AddObservation(agentPosZ_normalized);
        sensor.AddObservation(agentRotation_nomalized);
    }

    public override void Heuristic(in ActionBuffers actionsOut)
    {
        var discreteActionsOut = actionsOut.DiscreteActions;
        discreteActionsOut[0] = 0;

        if (Input.GetKey(KeyCode.UpArrow))
        {
            discreteActionsOut[0] = 1;
        }
        else if (Input.GetKey(KeyCode.LeftArrow))
        {
            discreteActionsOut[0] = 2;
        }
        else if (Input.GetKey(KeyCode.RightArrow))
        {
            discreteActionsOut[0] = 3;
        }    

    }

    public override void OnActionReceived(ActionBuffers actions)
    {
        MoveAgent(actions.DiscreteActions);
        AddReward(-2f / MaxStep);
        CumulativeReward = GetCumulativeReward();
    }

    public void MoveAgent(ActionSegment<int> act)
    {
        var action = act[0];

        switch (action)
        {
            case 1:
                transform.position += transform.forward * _moveSpeed * Time.deltaTime;
                break;
            case 2:
                transform.Rotate(0f, -_rotationSpeed * Time.deltaTime, 0f);
                break;
            case 3:
                transform.Rotate(0f, _rotationSpeed * Time.deltaTime, 0f);
                break;
        }
    }

    private void OnTriggerEnter(Collider other)
    {
        if (other.CompareTag("Goal"))
        {
            GoalReached();
        }
    }

    private void GoalReached()
    {
        AddReward(1.0f);
        CumulativeReward = GetCumulativeReward();

        EndEpisode();
    }

    private void OnCollisionEnter(Collision collision)
    {
        if (collision.gameObject.CompareTag("Wall"))
        {
            AddReward(-0.05f);

            if (_renderer != null)
            {
                _renderer.material.color = Color.red;
            }
        }
    }

    private void OnCollisionStay(Collision collision)
    {
        if(collision.gameObject.CompareTag("Wall"))
        {
            AddReward(-0.01f * Time.fixedDeltaTime);
        }
    }

    private void OnCollisionExit(Collision collision)
    {
        if (collision.gameObject.CompareTag("Wall"))
        {
            if (_renderer != null)
            {
                _renderer.material.color = Color.blue;
            }
        }
    }
}

