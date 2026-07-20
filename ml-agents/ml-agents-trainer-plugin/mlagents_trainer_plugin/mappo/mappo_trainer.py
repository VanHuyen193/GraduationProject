from typing import cast

import numpy as np

from mlagents_envs.logging_util import get_logger
from mlagents_envs.side_channel.stats_side_channel import StatsAggregationMethod
from mlagents.trainers.buffer import BufferKey, RewardSignalUtil
from mlagents.trainers.trainer.trainer_utils import lambda_return
from mlagents.trainers.poca.trainer import POCATrainer
from mlagents.trainers.trajectory import Trajectory

from .mappo_optimizer import MAPPOOptimizer, MAPPOSettings

logger = get_logger(__name__)

TRAINER_NAME = "mappo"


class MAPPOTrainer(POCATrainer):
    """
    MAPPO (Multi-Agent PPO): PPO with a centralized critic over the whole
    group. Identical to MA-POCA except the advantage is computed against the
    centralized VALUE estimate instead of the counterfactual baseline.
    """

    def _process_trajectory(self, trajectory: Trajectory) -> None:
        """
        Copy of POCATrainer._process_trajectory with the counterfactual
        baseline removed: advantage = lambda_return - centralized value.
        """
        # Bỏ qua bản của POCATrainer, chạy phần bookkeeping chung của lớp nền
        super(POCATrainer, self)._process_trajectory(trajectory)

        agent_id = trajectory.agent_id

        agent_buffer_trajectory = trajectory.to_agentbuffer()

        if self.is_training:
            self.policy.actor.update_normalization(agent_buffer_trajectory)
            self.optimizer.critic.update_normalization(agent_buffer_trajectory)

        # Centralized value (baseline của POCA bị bỏ qua)
        (
            value_estimates,
            _baseline_estimates,
            value_next,
            value_memories,
            _baseline_memories,
        ) = self.optimizer.get_trajectory_and_baseline_value_estimates(
            agent_buffer_trajectory,
            trajectory.next_obs,
            trajectory.next_group_obs,
            trajectory.all_group_dones_reached
            and trajectory.done_reached
            and not trajectory.interrupted,
        )

        if value_memories is not None:
            agent_buffer_trajectory[BufferKey.CRITIC_MEMORY].set(value_memories)

        for name, v in value_estimates.items():
            agent_buffer_trajectory[RewardSignalUtil.value_estimates_key(name)].extend(
                v
            )
            self._stats_reporter.add_stat(
                f"Policy/{self.optimizer.reward_signals[name].name.capitalize()} Value Estimate",
                np.mean(v),
            )

        self.collected_rewards["environment"][agent_id] += np.sum(
            agent_buffer_trajectory[BufferKey.ENVIRONMENT_REWARDS]
        )
        self.collected_group_rewards[agent_id] += np.sum(
            agent_buffer_trajectory[BufferKey.GROUP_REWARD]
        )
        for name, reward_signal in self.optimizer.reward_signals.items():
            evaluate_result = (
                reward_signal.evaluate(agent_buffer_trajectory) * reward_signal.strength
            )
            agent_buffer_trajectory[RewardSignalUtil.rewards_key(name)].extend(
                evaluate_result
            )
            self.collected_rewards[name][agent_id] += np.sum(evaluate_result)

        # GAE với centralized value — điểm khác biệt cốt lõi so với POCA
        tmp_advantages = []
        for name in self.optimizer.reward_signals:
            local_rewards = np.array(
                agent_buffer_trajectory[RewardSignalUtil.rewards_key(name)].get_batch(),
                dtype=np.float32,
            )
            v_estimates = agent_buffer_trajectory[
                RewardSignalUtil.value_estimates_key(name)
            ].get_batch()

            lambd_returns = lambda_return(
                r=local_rewards,
                value_estimates=v_estimates,
                gamma=self.optimizer.reward_signals[name].gamma,
                lambd=self.hyperparameters.lambd,
                value_next=value_next[name],
            )

            local_advantage = np.array(lambd_returns) - np.array(v_estimates)

            agent_buffer_trajectory[RewardSignalUtil.returns_key(name)].set(
                lambd_returns
            )
            agent_buffer_trajectory[RewardSignalUtil.advantage_key(name)].set(
                local_advantage
            )
            tmp_advantages.append(local_advantage)

        global_advantages = list(
            np.mean(np.array(tmp_advantages, dtype=np.float32), axis=0)
        )
        agent_buffer_trajectory[BufferKey.ADVANTAGES].set(global_advantages)

        self._append_to_update_buffer(agent_buffer_trajectory)

        if trajectory.done_reached:
            self._update_end_episode_stats(agent_id, self.optimizer)
            if not trajectory.all_group_dones_reached:
                self.collected_group_rewards.pop(agent_id)

        if trajectory.all_group_dones_reached and trajectory.done_reached:
            self.stats_reporter.add_stat(
                "Environment/Group Cumulative Reward",
                self.collected_group_rewards.get(agent_id, 0),
                aggregation=StatsAggregationMethod.HISTOGRAM,
            )
            self.collected_group_rewards.pop(agent_id)

    def create_optimizer(self) -> MAPPOOptimizer:
        return MAPPOOptimizer(self.policy, self.trainer_settings)

    @staticmethod
    def get_settings_type():
        return MAPPOSettings

    @staticmethod
    def get_trainer_name() -> str:
        return TRAINER_NAME


def get_type_and_setting():
    return {MAPPOTrainer.get_trainer_name(): MAPPOTrainer}, {
        MAPPOTrainer.get_trainer_name(): MAPPOTrainer.get_settings_type()
    }
