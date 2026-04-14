using Unity.MLAgents;
using UnityEngine;

public class GUI_Agent : MonoBehaviour
{
    [SerializeField] private MLAgent _agent;

    private GUIStyle _defaultStyle = new GUIStyle();
    private GUIStyle _positiveStyle = new GUIStyle();
    private GUIStyle _negativeStyle = new GUIStyle();

    // Start is called once before the first execution of Update after the MonoBehaviour is created
    void Start()
    {
        _defaultStyle.fontSize = 20;
        _defaultStyle.normal.textColor = Color.yellow;

        _positiveStyle.fontSize = 20;
        _positiveStyle.normal.textColor = Color.green;

        _negativeStyle.fontSize = 20;
        _negativeStyle.normal.textColor = Color.red;
        
    }

    private void OnGUI()
    {
        string debugEpisode = "Episode: " + _agent.CurrentEpisode + " - Step: " + _agent.StepCount;
        string debugReward = "Reward: " + _agent.CumulativeReward.ToString();

        GUIStyle rewardStyle = _agent.CumulativeReward < 0 ? _negativeStyle : _positiveStyle;

        GUI.Label(new Rect(20, 20, 500, 30), debugEpisode, _defaultStyle);
        GUI.Label(new Rect(20, 60, 500, 30), debugReward, rewardStyle);
    }

    // Update is called once per frame
    void Update()
    {
        
    }
}
