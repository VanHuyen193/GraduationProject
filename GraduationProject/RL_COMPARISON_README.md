# RL Algorithm Comparison - GraduationProject

## Overview

This project compares **3 Reinforcement Learning algorithms** across **3 Unity ML-Agents environments**,
resulting in **9 training experiments** and a performance comparison report.

---

## Algorithms

| Algorithm | Trainer Type | Category | Key Feature |
|-----------|-------------|----------|-------------|
| **PPO** | `ppo` | On-policy | Stable, general-purpose; uses Self-Play for Football |
| **SAC** | `sac` | Off-policy | Replay buffer, entropy exploration, sample efficient |
| **MA-POCA** | `poca` | Multi-agent | Centralized critic, credit assignment for cooperative tasks |

All three algorithms are natively supported in **Unity ML-Agents 1.2.0**.

---

## Environments

| Environment | Scene | Behavior Name | Action Space | Agent Setup |
|------------|-------|--------------|-------------|-------------|
| **Football Table** | `Assets/Football/Football.unity` | `Football` | Continuous (8) | Competitive 2-agent |
| **Cross The Road** | `Assets/CrossTheRoad/Scenes/` | `CrossTheRoad` | Discrete (4) | Single agent |
| **Capture The Flag** | `Assets/Collaboration/Collaboration.unity` | `PuzzleBehavior` | Discrete (7) | Cooperative 2-agent |

---

## Training Configs (9 files)

```
config/
  football_ppo.yaml     # Football + PPO (with Self-Play)     - 10M steps
  football_sac.yaml     # Football + SAC                       - 10M steps
  football_poca.yaml    # Football + MA-POCA                   - 10M steps
  ctr_ppo.yaml          # Cross The Road + PPO                 - 2M steps
  ctr_sac.yaml          # Cross The Road + SAC                 - 2M steps
  ctr_poca.yaml         # Cross The Road + MA-POCA             - 2M steps
  ctf_ppo.yaml          # Capture The Flag + PPO               - 5M steps
  ctf_sac.yaml          # Capture The Flag + SAC               - 5M steps
  ctf_poca.yaml         # Capture The Flag + MA-POCA (ideal)   - 5M steps
```

---

## How To Run

### Prerequisites
- Unity ML-Agents 1.2.0 installed in conda env `mlagents`
- Path: `C:\Users\Admin\miniconda3\envs\mlagents\`
- Unity Editor installed with the GraduationProject open

### Step 1: Run All 9 Training Jobs (Sequential)

```batch
REM Open Anaconda Prompt / PowerShell in conda env
C:\Users\Admin\miniconda3\envs\mlagents\python.exe train_all_sequential.py
```

Each training job will prompt you to:
1. Open Unity Editor
2. Load the correct Scene
3. Press Play in Unity Editor
4. Press ENTER in the terminal

**Options:**
```batch
# Resume from checkpoints
python train_all_sequential.py --resume

# Run only one environment
python train_all_sequential.py --only football
python train_all_sequential.py --only crossroad
python train_all_sequential.py --only capture

# Skip specific jobs
python train_all_sequential.py --skip football_sac ctf_poca

# Start from a specific job (skip completed ones)
python train_all_sequential.py --from-job ctr_ppo
```

### Step 2: Run Individual mlagents-learn Commands

You can also run each training job manually:

```batch
REM Football - PPO
C:\Users\Admin\miniconda3\envs\mlagents\Scripts\mlagents-learn.exe config\football_ppo.yaml --run-id=football_ppo_v1 --results-dir=results --time-scale=20

REM Football - SAC
C:\Users\Admin\miniconda3\envs\mlagents\Scripts\mlagents-learn.exe config\football_sac.yaml --run-id=football_sac_v1 --results-dir=results --time-scale=20

REM Football - MA-POCA
C:\Users\Admin\miniconda3\envs\mlagents\Scripts\mlagents-learn.exe config\football_poca.yaml --run-id=football_poca_v1 --results-dir=results --time-scale=20

REM Cross The Road - PPO
C:\Users\Admin\miniconda3\envs\mlagents\Scripts\mlagents-learn.exe config\ctr_ppo.yaml --run-id=ctr_ppo_v1 --results-dir=results --time-scale=20

REM Cross The Road - SAC
C:\Users\Admin\miniconda3\envs\mlagents\Scripts\mlagents-learn.exe config\ctr_sac.yaml --run-id=ctr_sac_v1 --results-dir=results --time-scale=20

REM Cross The Road - MA-POCA
C:\Users\Admin\miniconda3\envs\mlagents\Scripts\mlagents-learn.exe config\ctr_poca.yaml --run-id=ctr_poca_v1 --results-dir=results --time-scale=20

REM Capture The Flag - PPO
C:\Users\Admin\miniconda3\envs\mlagents\Scripts\mlagents-learn.exe config\ctf_ppo.yaml --run-id=ctf_ppo_v1 --results-dir=results --time-scale=20

REM Capture The Flag - SAC
C:\Users\Admin\miniconda3\envs\mlagents\Scripts\mlagents-learn.exe config\ctf_sac.yaml --run-id=ctf_sac_v1 --results-dir=results --time-scale=20

REM Capture The Flag - MA-POCA (recommended)
C:\Users\Admin\miniconda3\envs\mlagents\Scripts\mlagents-learn.exe config\ctf_poca.yaml --run-id=ctf_poca_v1 --results-dir=results --time-scale=20
```

### Step 3: Compare Results

After all training is done, run the comparison analysis:

```batch
C:\Users\Admin\miniconda3\envs\mlagents\python.exe compare_results.py
```

This generates:
- `comparison_charts/01_reward_curves.png` - Reward curves per environment
- `comparison_charts/02_final_reward_bar.png` - Final reward bar chart
- `comparison_charts/03_episode_length.png` - Episode length convergence
- `comparison_charts/04_policy_loss.png` - Policy loss
- `comparison_charts/05_entropy.png` - Policy entropy
- `comparison_charts/comparison_report.md` - Full analysis report
- `comparison_report.md` (copy in project root)

### Step 4: View TensorBoard

```batch
C:\Users\Admin\miniconda3\envs\mlagents\Scripts\tensorboard.exe --logdir=results
REM Then open http://localhost:6006 in browser
```

---

## Training Status

| Run ID | Environment | Algorithm | Status |
|--------|------------|-----------|--------|
| `football_ppo_v1` | Football Table | PPO | ⏳ Pending |
| `football_sac_v1` | Football Table | SAC | ⏳ Pending |
| `football_poca_v1` | Football Table | MA-POCA | ⏳ Pending |
| `ctr_ppo_v1` | Cross The Road | PPO | ⏳ Pending |
| `ctr_sac_v1` | Cross The Road | SAC | ⏳ Pending |
| `ctr_poca_v1` | Cross The Road | MA-POCA | ⏳ Pending |
| `ctf_ppo_v1` | Capture The Flag | PPO | ⏳ Pending |
| `ctf_sac_v1` | Capture The Flag | SAC | ⏳ Pending |
| `ctf_poca_v1` | Capture The Flag | MA-POCA | ⏳ Pending |

---

## Project Structure

```
GraduationProject/
├── config/
│   ├── football_ppo.yaml     # Football + PPO
│   ├── football_sac.yaml     # Football + SAC  
│   ├── football_poca.yaml    # Football + MA-POCA
│   ├── ctr_ppo.yaml          # CrossTheRoad + PPO
│   ├── ctr_sac.yaml          # CrossTheRoad + SAC
│   ├── ctr_poca.yaml         # CrossTheRoad + MA-POCA
│   ├── ctf_ppo.yaml          # CaptureFlag + PPO
│   ├── ctf_sac.yaml          # CaptureFlag + SAC
│   └── ctf_poca.yaml         # CaptureFlag + MA-POCA
├── results/
│   ├── football_ppo_v1/      # Training results
│   ├── football_sac_v1/
│   ├── ...
│   └── training_summary.json
├── comparison_charts/
│   ├── 01_reward_curves.png
│   ├── 02_final_reward_bar.png
│   ├── 03_episode_length.png
│   ├── 04_policy_loss.png
│   ├── 05_entropy.png
│   └── comparison_report.md
├── train_all_sequential.py   # Run all 9 training jobs
├── compare_results.py        # Generate comparison report
├── comparison_report.md      # Final report (after training)
└── training_status.json      # Progress tracking
```

---

## Algorithm Selection Rationale

### Why PPO?
- Standard baseline for Unity ML-Agents
- Works for both discrete and continuous action spaces
- On-policy: simple, stable, well-understood
- Self-Play variant for competitive Football Table

### Why SAC?
- Off-policy with experience replay → sample efficient
- Entropy regularization prevents premature convergence
- Max-entropy framework → naturally explores diverse behaviors
- Works well for both discrete and continuous actions

### Why MA-POCA?
- Designed specifically for cooperative multi-agent learning
- Centralized value function sees all agents' states during training
- Decentralized execution: each agent acts independently at inference
- Proper handling of group rewards via `SimpleMultiAgentGroup`
- Best choice for Capture The Flag; comparison baseline for others
