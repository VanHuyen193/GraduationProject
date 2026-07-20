from typing import Dict
import attr

from mlagents.torch_utils import torch
from mlagents.trainers.buffer import AgentBuffer, BufferKey, RewardSignalUtil
from mlagents_envs.timers import timed
from mlagents.trainers.policy.torch_policy import TorchPolicy
from mlagents.trainers.settings import TrainerSettings
from mlagents.trainers.exception import UnityTrainerException
from mlagents.trainers.poca.optimizer_torch import TorchPOCAOptimizer, POCASettings
from mlagents.trainers.torch_entities.agent_action import AgentAction
from mlagents.trainers.torch_entities.action_log_probs import ActionLogProbs
from mlagents.trainers.torch_entities.utils import ModelUtils
from mlagents.trainers.trajectory import ObsUtil, GroupObsUtil


@attr.s(auto_attribs=True)
class MAPPOSettings(POCASettings):
    """MAPPO dùng cùng bộ hyperparameter với PPO/POCA (beta, epsilon, lambd, num_epoch)."""

    pass


class MAPPOOptimizer(TorchPOCAOptimizer):
    """
    MAPPO (Multi-Agent PPO, Yu et al. 2022): PPO with a centralized value
    function conditioned on ALL agents' observations.

    Reuses POCA's MultiAgentNetworkBody critic, but unlike MA-POCA the
    counterfactual baseline is NOT used: advantages are computed against the
    centralized value estimate (see MAPPOTrainer), and the baseline term is
    dropped from the loss.
    """

    def __init__(self, policy: TorchPolicy, trainer_settings: TrainerSettings):
        super().__init__(policy, trainer_settings)

        if policy.use_recurrent:
            raise UnityTrainerException(
                "The MAPPO plugin does not support memory/LSTM "
                "(network_settings.memory). Remove the memory section."
            )

    @timed
    def update(self, batch: AgentBuffer, num_sequences: int) -> Dict[str, float]:
        """
        Same PPO-style update as POCA, minus everything related to the
        counterfactual baseline.
        """
        decay_lr = self.decay_learning_rate.get_value(self.policy.get_current_step())
        decay_eps = self.decay_epsilon.get_value(self.policy.get_current_step())
        decay_bet = self.decay_beta.get_value(self.policy.get_current_step())
        returns = {}
        old_values = {}
        for name in self.reward_signals:
            old_values[name] = ModelUtils.list_to_tensor(
                batch[RewardSignalUtil.value_estimates_key(name)]
            )
            returns[name] = ModelUtils.list_to_tensor(
                batch[RewardSignalUtil.returns_key(name)]
            )

        n_obs = len(self.policy.behavior_spec.observation_specs)
        current_obs = ObsUtil.from_buffer(batch, n_obs)
        current_obs = [ModelUtils.list_to_tensor(obs) for obs in current_obs]
        groupmate_obs = GroupObsUtil.from_buffer(batch, n_obs)
        groupmate_obs = [
            [ModelUtils.list_to_tensor(obs) for obs in _groupmate_obs]
            for _groupmate_obs in groupmate_obs
        ]

        act_masks = ModelUtils.list_to_tensor(batch[BufferKey.ACTION_MASK])
        actions = AgentAction.from_buffer(batch)

        memories = [
            ModelUtils.list_to_tensor(batch[BufferKey.MEMORY][i])
            for i in range(0, len(batch[BufferKey.MEMORY]), self.policy.sequence_length)
        ]
        if len(memories) > 0:
            memories = torch.stack(memories).unsqueeze(0)
        value_memories = [
            ModelUtils.list_to_tensor(batch[BufferKey.CRITIC_MEMORY][i])
            for i in range(
                0, len(batch[BufferKey.CRITIC_MEMORY]), self.policy.sequence_length
            )
        ]
        if len(value_memories) > 0:
            value_memories = torch.stack(value_memories).unsqueeze(0)

        run_out = self.policy.actor.get_stats(
            current_obs,
            actions,
            masks=act_masks,
            memories=memories,
            sequence_length=self.policy.sequence_length,
        )

        log_probs = run_out["log_probs"]
        entropy = run_out["entropy"]

        all_obs = [current_obs] + groupmate_obs
        values, _ = self.critic.critic_pass(
            all_obs,
            memories=value_memories,
            sequence_length=self.policy.sequence_length,
        )

        old_log_probs = ActionLogProbs.from_buffer(batch).flatten()
        log_probs = log_probs.flatten()
        loss_masks = ModelUtils.list_to_tensor(batch[BufferKey.MASKS], dtype=torch.bool)

        value_loss = ModelUtils.trust_region_value_loss(
            values, old_values, returns, decay_eps, loss_masks
        )
        policy_loss = ModelUtils.trust_region_policy_loss(
            ModelUtils.list_to_tensor(batch[BufferKey.ADVANTAGES]),
            log_probs,
            old_log_probs,
            loss_masks,
            decay_eps,
        )

        loss = (
            policy_loss
            + 0.5 * value_loss
            - decay_bet * ModelUtils.masked_mean(entropy, loss_masks)
        )

        ModelUtils.update_learning_rate(self.optimizer, decay_lr)
        self.optimizer.zero_grad()
        loss.backward()
        self.optimizer.step()

        update_stats = {
            "Losses/Policy Loss": torch.abs(policy_loss).item(),
            "Losses/Value Loss": value_loss.item(),
            "Policy/Learning Rate": decay_lr,
            "Policy/Epsilon": decay_eps,
            "Policy/Beta": decay_bet,
        }

        return update_stats
