using UnityEngine;
using Unity.MLAgents;
using Unity.MLAgents.Sensors;
using Unity.MLAgents.Actuators;

namespace TableFootball
{
    /// <summary>
    /// Agent điều khiển toàn bộ team (foosball)
    /// </summary>
    public class FootballAgent : Agent
    {
        // ID của agent
        public int ID { get; private set; }

        // Thống kê (reward tracking, debug)
        public AgentStats Stats { get; private set; }

        // Số trận đã chơi
        public int GameCount { get; private set; }

        // Tiến độ episode (0 → 1)
        public float Progress => StepCount / (float)MaxStep;

        [Header("References")]
        [SerializeField] Team agentTeam;
        [SerializeField] Team opponentTeam;
        [SerializeField] Ball ball;

        [Header("Observation")]
        [Tooltip("Chỉ dùng XZ thay vì full 3D")]
        [SerializeField] bool use2DBallObs;

        [Header("Reward")]
        [SerializeField] float goalScoredReward = 1f;
        [SerializeField] float goalConcededPenalty = 1f;

        [SerializeField] float shotRewardMultiplier = 0.1f;
        bool useShotReward;

        [SerializeField] float maxSpinPenalty = 0.01f;
        bool useSpinPenalty;

        // =========================
        // INIT
        // =========================
        public override void Initialize()
        {
            ID = gameObject.GetInstanceID();

            Stats = new AgentStats(agentTeam.transform.name);

            // Subscribe event từ Ball
            ball.AutoKickEventHandler += OnAutoKick;
            ball.PlayerContactEventHandler += OnPlayerContact;
            ball.GoalEventHandler += OnGoal;

            useShotReward = shotRewardMultiplier > 0;
            useSpinPenalty = maxSpinPenalty > 0;
        }

        // =========================
        // RESET EPISODE
        // =========================
        public override void OnEpisodeBegin()
        {
            GameCount++;

            agentTeam.ReSet();
            Stats.Reset();
            ball.ReSet();
        }

        // =========================
        // ACTION (Agent output)
        // =========================
        public override void OnActionReceived(ActionBuffers actions)
        {
            float[] act = actions.ContinuousActions.Array;

            // Điều khiển các rod
            agentTeam.StepUpdate(act);

            // Reward nên đặt ở đây (KHÔNG phải CollectObservations)
            if (useShotReward)
                AddShotReward();

            if (useSpinPenalty)
                AddSpinPenalty();
        }

        // =========================
        // OBSERVATION (input cho AI)
        // =========================
        public override void CollectObservations(VectorSensor sensor)
        {
            // ===== BALL =====
            if (use2DBallObs)
            {
                sensor.AddObservation(ball.GetNormalizedVelocity2D() * agentTeam.Sign);

                Vector2 np = ball.GetNormalizedPosition2D() * agentTeam.Sign;

                sensor.AddObservation(Util.SplitDecimalPlaces(np.x, 4));
                sensor.AddObservation(Util.SplitDecimalPlaces(np.y, 4));
            }
            else
            {
                Vector3 nv = ball.GetNormalizedVelocity3D();

                sensor.AddObservation(nv.x * agentTeam.Sign);
                sensor.AddObservation(nv.y);
                sensor.AddObservation(nv.z * agentTeam.Sign);

                Vector3 np = ball.GetNormalizedPosition3D();

                sensor.AddObservation(Util.SplitDecimalPlaces(np.x * agentTeam.Sign, 4));
                sensor.AddObservation(np.y);
                sensor.AddObservation(Util.SplitDecimalPlaces(np.z * agentTeam.Sign, 4));
            }

            // ===== TEAM =====
            float spinSum = 0;

            foreach (PlayerPosition pp in agentTeam.Positions)
            {
                sensor.AddObservation(pp.GetNormalizedVelocity());

                float spin = pp.GetNormalizedAngularVelocity();
                spinSum += Mathf.Abs(spin);

                sensor.AddObservation(spin);

                sensor.AddObservation(Util.SplitDecimalPlaces(pp.GetNormalizedPosition(), 3));
                sensor.AddObservation(Util.SplitDecimalPlaces(pp.GetNormalizedAngle(), 3));
            }

            // ===== OPPONENT =====
            sensor.AddObservation(opponentTeam.GetNormalizedObs());
        }

        // =========================
        // REWARD SYSTEM
        // =========================

        /// <summary>
        /// Reward khi đá bóng về phía goal đối phương
        /// </summary>
        void AddShotReward()
        {
            if (Stats.HasBall)
            {
                Vector3 bp = ball.transform.position;

                Vector3 delta = opponentTeam.Goal.transform.position - bp;

                float reward = shotRewardMultiplier *
                               Vector3.Dot(delta.normalized, ball.Velocity);

                AddReward(reward);
                Stats.AddReward(AgentStats.SHOT_REWARD, reward);
            }
        }

        /// <summary>
        /// Phạt quay thanh quá nhiều
        /// </summary>
        void AddSpinPenalty()
        {
            float spinSum = 0;

            foreach (var pp in agentTeam.Positions)
            {
                spinSum += Mathf.Abs(pp.GetNormalizedAngularVelocity());
            }

            float penalty = maxSpinPenalty * spinSum * 0.25f;

            AddReward(-penalty);
            Stats.AddReward(AgentStats.SPIN_PENALTY, -penalty);
        }

        // =========================
        // EVENT HANDLERS
        // =========================

        void OnAutoKick(object sender, BallEvent e)
        {
            Stats.OnAutoKick();
        }

        void OnPlayerContact(object sender, BallEvent e)
        {
            if (e.State == BallEvent.CollisionState.Exit)
            {
                bool isAgentTeam = e.Team == agentTeam.gameObject;
                Stats.OnPlayerContact(isAgentTeam);
            }
        }

        void OnGoal(object sender, BallEvent e)
        {
            bool hasScored = e.Object == opponentTeam.Goal;

            Stats.OnGoal(hasScored);

            // Reward chính
            AddReward(hasScored ? goalScoredReward : -goalConcededPenalty);

            if (hasScored)
            {
                agentTeam.HighlightGoal();
            }

            // Kết thúc episode
            EndEpisode();
        }

        // =========================
        // CLEANUP (QUAN TRỌNG)
        // =========================
        void OnDestroy()
        {
            ball.AutoKickEventHandler -= OnAutoKick;
            ball.PlayerContactEventHandler -= OnPlayerContact;
            ball.GoalEventHandler -= OnGoal;
        }
    }
}
