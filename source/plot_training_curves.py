"""
Plots RLAgent and DQNAgent training curves.

Run from the project root with:
    python -m source.plot_training_curves

The script trains both learning agents on the same board configuration and
saves a rolling win-rate plot that shows whether performance improves over
training episodes.
"""

import json
import os
import subprocess
import sys
import time
import urllib.error
import urllib.request

import matplotlib.pyplot as plt

from source.agents.dqn_agent import DQNAgent
from source.agents.rl_agent import RLAgent


API_URL = "http://localhost:8080"


def api_is_running(api_url=API_URL):
    """
    Checks that the API can create and delete a small test game.
    """
    try:
        data = {
            "width": 1,
            "height": 1,
            "mine_count": 0,
        }

        create_request = urllib.request.Request(
            api_url + "/",
            data=json.dumps(data).encode("utf-8"),
            method="PUT",
        )
        response = urllib.request.urlopen(create_request, timeout=2)
        result = json.loads(response.read().decode("utf-8"))

        delete_request = urllib.request.Request(
            api_url + "/" + result["id"],
            method="DELETE",
        )
        urllib.request.urlopen(delete_request, timeout=2)

        return True
    except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError, OSError):
        return False


def start_api_if_needed():
    """
    Starts the Minesweeper API if it is not already running.

    Returns the process only when this script started the server.
    """
    if api_is_running():
        return None

    print("Starting Minesweeper API at http://localhost:8080...")
    os.makedirs("results", exist_ok=True)
    log_file = open("results/minesweeper_api_training_curves.log", "a")

    process = subprocess.Popen(
        [sys.executable, "-m", "minesweeper", "--no-threading"],
        stdout=log_file,
        stderr=log_file,
    )

    for _ in range(50):
        if api_is_running():
            return process
        time.sleep(0.2)

    raise RuntimeError(
        "Could not start the Minesweeper API. "
        "Check results/minesweeper_api_training_curves.log."
    )


def stop_api_if_started(process):
    """
    Stops the API only if this script started it.
    """
    if process is None:
        return

    process.terminate()
    try:
        process.wait(timeout=2)
    except subprocess.TimeoutExpired:
        process.kill()


def rolling_average(values, window_size):
    """
    Computes a rolling average using all available earlier values near the start.
    """
    averages = []

    for index in range(len(values)):
        start = max(0, index - window_size + 1)
        window = values[start:index + 1]
        averages.append(sum(window) / len(window))

    return averages


def train_rl_curve(episodes, width, height, mine_count):
    """
    Trains RLAgent and returns per-episode win indicators.
    """
    agent = RLAgent(width=width, height=height, mine_count=mine_count)
    wins = []

    print("\nTraining RLAgent for curve...")

    for episode in range(episodes):
        result = agent.train_one_game()
        wins.append(1 if result == "Win" else 0)

        if (episode + 1) % 100 == 0:
            recent_win_rate = sum(wins[-100:]) / len(wins[-100:])
            print(
                f"RLAgent episode {episode + 1}: "
                f"recent win rate = {recent_win_rate:.2%}, "
                f"q-table entries = {len(agent.q_table)}"
            )

    return wins


def train_dqn_curve(episodes, width, height, mine_count):
    """
    Trains DQNAgent and returns per-episode win indicators.
    """
    agent = DQNAgent(width=width, height=height, mine_count=mine_count)
    wins = []

    print("\nTraining DQNAgent for curve...")

    for episode in range(episodes):
        result, total_reward = agent.train_one_game()
        agent.training_rewards.append(total_reward)
        agent.training_results.append(result)

        wins.append(1 if result == "Win" else 0)

        if agent.epsilon > agent.epsilon_min:
            agent.epsilon *= agent.epsilon_decay
            agent.epsilon = max(agent.epsilon, agent.epsilon_min)

        if (episode + 1) % agent.target_update_frequency == 0:
            agent.target_network.load_state_dict(agent.policy_network.state_dict())

        if (episode + 1) % 100 == 0:
            recent_win_rate = sum(wins[-100:]) / len(wins[-100:])
            print(
                f"DQNAgent episode {episode + 1}: "
                f"recent win rate = {recent_win_rate:.2%}, "
                f"epsilon = {agent.epsilon:.3f}"
            )

    return wins


def save_training_curve_plot(rl_wins, dqn_wins, window_size, filename):
    """
    Saves a line plot comparing rolling win rates for RLAgent and DQNAgent.
    """
    os.makedirs(os.path.dirname(filename), exist_ok=True)

    episodes = list(range(1, len(rl_wins) + 1))
    rl_curve = rolling_average(rl_wins, window_size)
    dqn_curve = rolling_average(dqn_wins, window_size)

    plt.figure(figsize=(10, 6))
    plt.plot(episodes, rl_curve, label="RLAgent rolling win rate", linewidth=2)
    plt.plot(episodes, dqn_curve, label="DQNAgent rolling win rate", linewidth=2)
    plt.xlabel("Training Episode")
    plt.ylabel(f"Rolling Win Rate ({window_size}-episode window)")
    plt.title("RLAgent vs DQNAgent Training Curves")
    plt.ylim(0, 1)
    plt.grid(True, alpha=0.3)
    plt.legend()
    plt.tight_layout()
    plt.savefig(filename, dpi=300)
    plt.close()


def main():
    episodes = 1000
    window_size = 100
    width = 5
    height = 5
    mine_count = 3
    output_file = "results/figures/rl_dqn_training_curves.png"

    api_process = start_api_if_needed()

    try:
        rl_wins = train_rl_curve(episodes, width, height, mine_count)
        dqn_wins = train_dqn_curve(episodes, width, height, mine_count)
        save_training_curve_plot(rl_wins, dqn_wins, window_size, output_file)
    finally:
        stop_api_if_started(api_process)

    print(f"\nSaved training curve plot to {output_file}")


if __name__ == "__main__":
    main()
