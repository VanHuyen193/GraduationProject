using System.IO;
using System.Linq;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;

public class SceneSwitcher : EditorWindow
{
    [MenuItem("Open Scene/CrossTheRoad")]
    private static void OpenCrossTheRoad()
    {
        EditorSceneManager.OpenScene(
            "Assets/CrossTheRoad/Scenes/CrossTheRoad.unity"
        );
    }

    [MenuItem("Open Scene/Collab")]
    private static void OpenColab()
    {
        EditorSceneManager.OpenScene(
            "Assets/Collaboration/Scenes/CaptureTheFlag.unity"
        );
    }

    [MenuItem("Open Scene/Football")]
    private static void OpenFootball()
    {
        EditorSceneManager.OpenScene(
            "Assets/Football/Football.unity"
        );
    }
}