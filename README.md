# Minesweeper Agent - CS4100 Final Project
Elaina Kreher, Bella D’Aniello, & Vaishant Kottam
### Overview of the Problem
Minesweeper is a game that requires players to make decisions using incomplete information. Some moves can be determined through logical reasoning, while others require estimating risk and making informed guesses. This project explores how different AI approaches including random decision-making, rule-based reasoning, probabilistic inference, and reinforcement learning perform when solving Minesweeper. An effective Minesweeper agent must determine which cells are safe, identify likely mine locations, and decide how to act when no guaranteed safe move exists. The objective is to compare these methods and determine which approach is most effective for reasoning and decision-making under uncertainty.

### How to Set up an Equivalent Python Environment 

#### Prerequisites
- Python 3.10+
- numpy
- matplotlib

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
source .venv/bin/activate
```

### How to Execute Code

### Organization Overview
The project is divided into several components that separate the game environment, AI agents, evaluation framework, and visualization tools.
```text
CS4100-FinalProject/
│
├── minesweeper/
│   ├── __main__.py
│   ├── handler.py
│   └── minesweeper.py
│   └── MINESWEEPER_README.md
│
├── source/
│   ├── agents/
│   │   ├── base_agent.py
│   │   ├── random_agent.py
│   │   ├── rule_based_agent.py
│   │   ├── probability_agent.py
│   │   ├── rl_agent.py
│   │   └── AGENT_README.md
│   │
│   ├── run_experiments.py
│   └── visualizer.py
│
├── results/
│   ├── experiment_results.csv
│   └── figures/
│
└── README.md
```

#### `minesweeper/`
Contains the Minesweeper game environment and API implementation. This component manages board generation, mine placement, move execution, win/loss detection, and communication with the agents through HTTP requests.

#### `source/agents/`
Contains all AI agents used in the project.
- **BaseAgent**: Shared functionality for communicating with the Minesweeper API.
- **RandomAgent**: Selects random unrevealed cells.
- **RuleBasedAgent**: Uses deterministic Minesweeper logic.
- **ProbabilityAgent**: Uses probabilistic reasoning when deterministic moves are unavailable.
- **RLAgent**: Uses reinforcement learning to learn gameplay strategies through repeated experience.

#### `source/run_experiments.py`
Runs large-scale evaluations of all agents and computes performance metrics such as win rate, reward, runtime, and board progress.

#### `source/visualize_results.py`
Creates graphs and visualizations from experiment results to support analysis and comparison.

#### `results/`
Stores experiment outputs, evaluation metrics, trained models, and generated visualizations.
