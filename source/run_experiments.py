"""
Evaluation Metrics:
- Win rate
- Average reward
- Average episode length
- Average safe cells revealed
- Average runtime
- Q-table size for RLAgent
- Replay buffer size and network parameter count for DQNAgent
"""

import time
import csv
import os
from source.agents.random_agent import RandomAgent
from source.agents.rule_based_agent import RuleBasedAgent
from source.agents.probability_agent import ProbabilityAgent
from source.agents.rl_agent import RLAgent
from source.agents.dqn_agent import DQNAgent
import matplotlib.pyplot as plt

training_curves = {}


def count_hidden_cells(board):
    return sum(row.count(-1) for row in board)


def count_revealed_cells(board):
    total_cells = sum(len(row) for row in board)
    hidden_cells = count_hidden_cells(board)
    return total_cells - hidden_cells


def calculate_reward(old_board, new_board, new_state):
    if new_state == "Win":
        return 300

    if new_state == "Lose":
        return -300

    old_hidden = count_hidden_cells(old_board)
    new_hidden = count_hidden_cells(new_board)

    cells_revealed = old_hidden - new_hidden

    # Reward safe progress
    if cells_revealed > 0:
        return cells_revealed * 2  # reward each revealed cell more
    return -0.5  # smaller penalty for neutral moves


def normalize_move(chosen_move):
    """
    Some agents return just (x, y), while RLAgent currently returns
    ((x, y), used_random). This helper lets the experiment runner handle both.
    """
    if (
        isinstance(chosen_move, tuple)
        and len(chosen_move) == 2
        and isinstance(chosen_move[0], tuple)
    ):
        return chosen_move[0]

    return chosen_move


def rolling_average(values, window_size=100):
    """
    Converts per-episode wins/losses into a rolling win-rate curve.
    """
    averages = []

    for index in range(len(values)):
        start_index = max(0, index - window_size + 1)
        window = values[start_index:index + 1]
        averages.append(sum(window) / len(window))

    return averages


def run_single_game(agent):
    start_time = time.time()
    agent.create_game()

    moves = 0
    total_reward = 0
    final_revealed_cells = 0

    while True:
        # get the current visible board
        old_game_state = agent.get_game_state()
        old_board = old_game_state["board"]
        old_state = old_game_state["state"]

        # if the game is already over, stop
        if old_state in ["Win", "Lose"]:
            runtime = time.time() - start_time
            agent.delete_game()
            return old_state, moves, total_reward, final_revealed_cells, runtime

        # ask agent to choose a move
        x, y = normalize_move(agent.choose_move(old_board))

        # send that move to the Minesweeper API
        move_result = agent.make_move(x, y)
        moves += 1

        new_state = move_result["new_state"]

        # get updated board after the move
        new_game_state = agent.get_game_state()
        new_board = new_game_state["board"]

        # update revealed-cell count
        final_revealed_cells = count_revealed_cells(new_board)

        # add reward for this move
        reward = calculate_reward(old_board, new_board, new_state)
        total_reward += reward

        # if move ended the game, return results
        if new_state in ["Win", "Lose"]:
            runtime = time.time() - start_time
            agent.delete_game()
            return new_state, moves, total_reward, final_revealed_cells, runtime


def evaluate_agent(agent_class, agent_name, games=100, width=10, height=10, mine_count=10):
    """
    Evaluate non-RL agent over many games
    """
    wins = 0
    losses = 0
    total_moves = 0
    total_reward = 0
    total_revealed_cells = 0
    total_runtime = 0

    for game_num in range(games):
        # create a fresh agent for each game
        agent = agent_class(width=width, height=height, mine_count=mine_count)
        result, moves, reward, revealed_cells, runtime = run_single_game(agent)

        if result == "Win":
            wins += 1
        else:
            losses += 1

        total_moves += moves
        total_reward += reward
        total_revealed_cells += revealed_cells
        total_runtime += runtime

    return {
        "agent": agent_name,
        "games": games,
        "wins": wins,
        "losses": losses,
        "win_rate": wins / games,
        "average_reward": total_reward / games,
        "average_episode_length": total_moves / games,
        "average_safe_cells_revealed": total_revealed_cells / games,
        "average_runtime": total_runtime / games,
        "training_episodes": 0,
        "training_wins": "",
        "training_losses": "",
        "q_table_size": "",
        "replay_buffer_size": "",
        "network_parameters": ""
    }


def evaluate_rl_agent(games=100, width=5, height=5, mine_count=3, training_episodes=1000):
    """
    Trains and evaluates the RLAgent
    """
    agent = RLAgent(width=width, height=height, mine_count=mine_count)
    print("\nTraining RLAgent...")
    training_wins = 0
    training_losses = 0
    episode_wins = []

    for episode in range(training_episodes):
        result = agent.train_one_game()

        if result == "Win":
            training_wins += 1
            episode_wins.append(1)
        else:
            training_losses += 1
            episode_wins.append(0)

        if (episode + 1) % 100 == 0:
            print(
                episode + 1,
                " Episodes Complete:",
                training_wins,
                " Wins,",
                training_losses,
                " Losses,",
                len(agent.q_table),
                " entries in Q-table"
            )

    training_curves["RLAgent"] = rolling_average(episode_wins)

    wins = 0
    losses = 0
    total_moves = 0
    total_reward = 0
    total_revealed_cells = 0
    total_runtime = 0

    # save old epsilon so we can restore it after evaluation
    old_epsilon = agent.epsilon

    # epsilon = 0 means no random exploration during evaluation
    agent.epsilon = 0

    for game_num in range(games):
        result, moves, reward, revealed_cells, runtime = run_single_game(agent)

        if result == "Win":
            wins += 1
        else:
            losses += 1

        total_moves += moves
        total_reward += reward
        total_revealed_cells += revealed_cells
        total_runtime += runtime

    # restore original epsilon
    agent.epsilon = old_epsilon

    return {
        "agent": "RLAgent",
        "games": games,
        "wins": wins,
        "losses": losses,
        "win_rate": wins / games,
        "average_reward": total_reward / games,
        "average_episode_length": total_moves / games,
        "average_safe_cells_revealed": total_revealed_cells / games,
        "average_runtime": total_runtime / games,
        "training_episodes": training_episodes,
        "training_wins": training_wins,
        "training_losses": training_losses,
        "q_table_size": len(agent.q_table),
        "replay_buffer_size": "",
        "network_parameters": ""
    }


def evaluate_dqn_agent(games=100, width=5, height=5, mine_count=3, training_episodes=1000):
    """
    Trains and evaluates the DQNAgent.
    """
    agent = DQNAgent(width=width, height=height, mine_count=mine_count)
    print("\nTraining DQNAgent...")
    agent.train(episodes=training_episodes)

    episode_wins = [
        1 if result == "Win" else 0
        for result in agent.training_results
    ]
    training_curves["DQNAgent"] = rolling_average(episode_wins)

    wins = 0
    losses = 0
    total_moves = 0
    total_reward = 0
    total_revealed_cells = 0
    total_runtime = 0

    old_epsilon = agent.epsilon
    agent.epsilon = 0

    for game_num in range(games):
        result, moves, reward, revealed_cells, runtime = run_single_game(agent)

        if result == "Win":
            wins += 1
        else:
            losses += 1

        total_moves += moves
        total_reward += reward
        total_revealed_cells += revealed_cells
        total_runtime += runtime

    agent.epsilon = old_epsilon

    network_parameters = sum(
        parameter.numel()
        for parameter in agent.policy_network.parameters()
    )

    return {
        "agent": "DQNAgent",
        "games": games,
        "wins": wins,
        "losses": losses,
        "win_rate": wins / games,
        "average_reward": total_reward / games,
        "average_episode_length": total_moves / games,
        "average_safe_cells_revealed": total_revealed_cells / games,
        "average_runtime": total_runtime / games,
        "training_episodes": training_episodes,
        "training_wins": agent.training_results.count("Win"),
        "training_losses": agent.training_results.count("Lose"),
        "q_table_size": "",
        "replay_buffer_size": len(agent.replay_buffer),
        "network_parameters": network_parameters
    }


def save_results(results, filename="results/experiment_results.csv"):
    os.makedirs("results", exist_ok=True)

    fieldnames = [
        "agent",
        "games",
        "wins",
        "losses",
        "win_rate",
        "average_reward",
        "average_episode_length",
        "average_safe_cells_revealed",
        "average_runtime",
        "training_episodes",
        "training_wins",
        "training_losses",
        "q_table_size",
        "replay_buffer_size",
        "network_parameters"
    ]

    with open(filename, "w", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)

        writer.writeheader()

        for result in results:
            writer.writerow(result)


def print_results(results):
    print("\nExperiment Results")
    for result in results:
        print(f"\nAgent: {result['agent']}")
        print(f"Games: {result['games']}")
        print(f"Wins: {result['wins']}")
        print(f"Losses: {result['losses']}")
        print(f"Win Rate: {result['win_rate']:.2%}")
        print(f"Average Reward: {result['average_reward']:.2f}")
        print(f"Average Episode Length: {result['average_episode_length']:.2f}")
        print(f"Average Safe Cells Revealed: {result['average_safe_cells_revealed']:.2f}")
        print(f"Average Runtime: {result['average_runtime']:.4f} seconds")

        if result["training_episodes"] != 0:
            print(f"Training Episodes: {result['training_episodes']}")
            print(f"Training Wins: {result['training_wins']}")
            print(f"Training Losses: {result['training_losses']}")

        if result["q_table_size"] != "":
            print(f"Q-table Size: {result['q_table_size']}")

        if result["replay_buffer_size"] != "":
            print(f"Replay Buffer Size: {result['replay_buffer_size']}")
            print(f"Network Parameters: {result['network_parameters']}")


def save_results_table_png(results, filename="results/figures/experiment_results_table.png"):
    os.makedirs("results/figures", exist_ok=True)
    table_data = []

    for result in results:
        table_data.append([
            result["agent"],
            result["games"],
            result["wins"],
            result["losses"],
            f"{result['win_rate']:.2%}",
            f"{result['average_reward']:.2f}",
            f"{result['average_episode_length']:.2f}",
            f"{result['average_safe_cells_revealed']:.2f}",
            f"{result['average_runtime']:.4f}s",
            result["training_episodes"],
            result["training_wins"],
            result["training_losses"],
            result["q_table_size"],
            result["replay_buffer_size"],
            result["network_parameters"]
        ])

    column_labels = [
        "Agent",
        "Games",
        "Wins",
        "Losses",
        "Win Rate",
        "Avg Reward",
        "Avg Moves",
        "Avg Cells",
        "Runtime",
        "Train Eps",
        "Train Wins",
        "Train Losses",
        "Q-Table",
        "Replay",
        "Params"
    ]

    fig, ax = plt.subplots(figsize=(22, 3))
    ax.axis("off")

    table = ax.table(
        cellText=table_data,
        colLabels=column_labels,
        loc="center",
        cellLoc="center"
    )

    table.auto_set_font_size(False)
    table.set_fontsize(9)
    table.scale(1, 1.5)
    plt.tight_layout()
    plt.savefig(filename, dpi=300, bbox_inches="tight")
    plt.close()


def save_training_curves_png(curves, filename="results/figures/rl_dqn_training_curves.png"):
    """
    Saves a line plot of rolling training win rate for RLAgent and DQNAgent.
    """
    os.makedirs("results/figures", exist_ok=True)

    plt.figure(figsize=(10, 6))

    for agent_name, rolling_win_rates in curves.items():
        episodes = range(1, len(rolling_win_rates) + 1)
        plt.plot(episodes, rolling_win_rates, label=agent_name)

    plt.title("RL and DQN Training Curves")
    plt.xlabel("Training Episode")
    plt.ylabel("Rolling Win Rate")
    plt.ylim(0, 1)
    plt.grid(True, alpha=0.3)
    plt.legend()
    plt.tight_layout()
    plt.savefig(filename, dpi=300)
    plt.close()


if __name__ == "__main__":
    games = 100
    width = 5
    height = 5
    mine_count = 3
    training_episodes = 50000
    results = []

    # random baseline
    results.append(
        evaluate_agent(
            RandomAgent,
            "RandomAgent",
            games=games,
            width=width,
            height=height,
            mine_count=mine_count
        )
    )

    # rule-based logical agent
    results.append(
        evaluate_agent(
            RuleBasedAgent,
            "RuleBasedAgent",
            games=games,
            width=width,
            height=height,
            mine_count=mine_count
        )
    )

    # probability-based agent
    results.append(
        evaluate_agent(
            ProbabilityAgent,
            "ProbabilityAgent",
            games=games,
            width=width,
            height=height,
            mine_count=mine_count
        )
    )

    # reinforcement learning agent
    results.append(
        evaluate_rl_agent(
            games=games,
            width=width,
            height=height,
            mine_count=mine_count,
            training_episodes=training_episodes
        )
    )

    # deep Q-learning agent
    results.append(
        evaluate_dqn_agent(
            games=games,
            width=width,
            height=height,
            mine_count=mine_count,
            training_episodes=training_episodes
        )
    )

    print_results(results)
    save_results(results)
    save_results_table_png(results)
    save_training_curves_png(training_curves)