# Minesweeper Agent - CS4100 Final Project
Elaina Kreher, Bella D'Aniello, & Vaishant Kottam

---

## Overview of the Problem

Minesweeper is a game that requires players to make decisions using incomplete information. Some moves can be determined through logical reasoning, while others require estimating risk and making informed guesses. This project explores how different AI approaches perform when solving Minesweeper: random decision-making, rule-based reasoning, probabilistic inference, and reinforcement learning (Q-learning and Deep Q-Networks).

An effective Minesweeper agent must determine which cells are safe, identify likely mine locations, and decide how to act when no guaranteed safe move exists. The objective is to compare these methods and determine which approach is most effective for reasoning and decision-making under uncertainty.

---

## How to Set Up an Equivalent Python Environment

### Prerequisites
- Python 3.10+
- numpy
- matplotlib
- torch (PyTorch)
- pygame

### Steps

1. Clone the repository:
```bash
git clone https://github.com/elainakreher/CS4100-FinalProject.git
cd CS4100-FinalProject
```

2. Create a virtual environment:
```bash
python3 -m venv .venv
```

3. Activate the virtual environment:
```bash
# macOS / Linux
source .venv/bin/activate

# Windows
.venv\Scripts\activate
```

4. Install dependencies:
```bash
pip install torch matplotlib pygame numpy
```

---

## How to Execute Code

All commands should be run from the project root directory with the virtual environment activated.

### Step 1: Start the Minesweeper API

The agents communicate with a local Minesweeper game server over HTTP. Start it in a separate terminal before running anything else:

```bash
python -m minesweeper
```

The API will start at `http://localhost:8080`. Leave this terminal running.

### Step 2: Run Experiments

To train all agents and evaluate their performance across 100 games each:

```bash
python -m source.run_experiments
```

This will:
- Evaluate RandomAgent, RuleBasedAgent, and ProbabilityAgent immediately (no training needed)
- Train RLAgent for 50,000 episodes, then evaluate
- Train DQNAgent for 50,000 episodes, then evaluate
- Save results to `results/experiment_results.csv`
- Save a results table to `results/figures/experiment_results_table.png`
- Save training curves to `results/figures/rl_dqn_training_curves.png`

> ⚠️ Training both RL agents for 50,000 episodes takes significant time. Expect the full run to take 30–60 minutes depending on your machine.

### Step 3: Run the Visual Demo (Optional)

To watch an agent play Minesweeper in a pygame window:

```bash
python -m source.demo random
python -m source.demo rule_based
python -m source.demo probability
python -m source.demo rl        # loads saved Q-table from results/q_table.json
python -m source.demo dqn       # loads saved model from results/dqn_model.pth
```

> ⚠️ The API must be running before launching the demo.

### Step 4: Generate Training Curves Separately (Optional)

To regenerate only the RL vs DQN training curve plot without running the full experiment:

```bash
python -m source.plot_training_curves
```
---

## Organization Overview

```text
CS4100-FinalProject/
│
├── minesweeper/
│   ├── __main__.py
│   ├── handler.py
│   ├── minesweeper.py
│   └── MINESWEEPER_README.md
│
├── source/
│   ├── agents/
│   │   ├── base_agent.py
│   │   ├── random_agent.py
│   │   ├── rule_based_agent.py
│   │   ├── probability_agent.py
│   │   ├── rl_agent.py
│   │   ├── dqn_agent.py
│   │   └── AGENT_README.md
│   │
│   ├── run_experiments.py
│   ├── plot_training_curves.py
│   ├── demo.py
│   └── visualizer.py
│
├── results/
│   ├── experiment_results.csv
│   ├── q_table.json
│   ├── dqn_model.pth
│   └── figures/
│       ├── experiment_results_table.png
│       └── rl_dqn_training_curves.png
│
└── README.md
```

### `minesweeper/`
Contains the Minesweeper game environment and HTTP API. Manages board generation, mine placement, flood-fill reveal, win/loss detection, and all game state. Agents never interact with this directly — they communicate through HTTP requests to the running server.

### `source/agents/`
Contains all AI agents. Each agent inherits from `BaseAgent` and implements a `choose_move(board)` method.

- **BaseAgent** — shared HTTP communication with the Minesweeper API; handles game creation, move submission, and game deletion. Not evaluated directly.
- **RandomAgent** — baseline agent that selects a random unrevealed cell each turn.
- **RuleBasedAgent** — applies deterministic Minesweeper logic. If the number of hidden neighbors around a revealed clue equals the remaining mine count, all hidden neighbors are flagged as mines. If all mines around a clue are already known, remaining hidden neighbors are marked safe. Falls back to random when no safe move can be deduced.
- **ProbabilityAgent** — extends RuleBasedAgent. When no guaranteed safe move exists, estimates the mine probability of each hidden cell based on neighboring clue constraints and picks the cell with the lowest risk.
- **RLAgent** — Q-learning agent. Learns a Q-table mapping (board state, action) pairs to expected rewards through repeated gameplay. Uses epsilon-greedy exploration with decay. Trained for 50,000 episodes.
- **DQNAgent** — Deep Q-Network agent. Replaces the Q-table with a feedforward neural network (input → 128 → 128 → 64 → output) that approximates Q-values, allowing it to generalize across board configurations it has not seen before. Uses experience replay, a target network, and epsilon-greedy exploration. Trained for 50,000 episodes.

### `source/run_experiments.py`
Trains and evaluates all five agents, computes performance metrics (win rate, average reward, episode length, cells revealed, runtime), and saves results to CSV and PNG figures.

### `source/plot_training_curves.py`
Standalone script that trains the RLAgent and DQNAgent and saves a rolling win-rate plot comparing their learning curves over training episodes.

### `source/demo.py`
Launches a pygame window to visually watch a chosen agent play one game of Minesweeper in real time. Accepts an agent name as a command-line argument.

### `source/visualizer.py`
Pygame rendering utilities used by `demo.py`. Draws the board, colors cells by state, and renders number clues.

### `results/`
Stores all experiment outputs: the CSV results table, saved model weights (`dqn_model.pth`), the saved Q-table (`q_table.json`), and generated figures.
