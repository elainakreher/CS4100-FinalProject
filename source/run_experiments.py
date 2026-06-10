"""
Evaluation Metrics:
- Win rate
- Average reward
- Average episode length
- Average safe cells revealed
- Average runtime
- Q-table size for RLAgent
"""

import time
import csv
import os
from source.agents.random_agent import RandomAgent
from source.agents.rule_based_agent import RuleBasedAgent
from source.agents.probability_agent import ProbabilityAgent
from source.agents.rl_agent import RLAgent

def count_hidden_cells(board):
    return sum(row.count(-1) for row in board)


def count_revealed_cells(board):
    total_cells = sum(len(row) for row in board)
    hidden_cells = count_hidden_cells(board)
    return total_cells - hidden_cells


def calculate_reward(old_board, new_board, new_state):
    if new_state == "Win":
        return 100

    if new_state == "Lose":
        return -100

    old_hidden = count_hidden_cells(old_board)
    new_hidden = count_hidden_cells(new_board)

    cells_revealed = old_hidden - new_hidden

    # Reward safe progress
    if cells_revealed > 0:
        return 1 + cells_revealed
    # Small penalty if no useful progress happened
    return -1


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

        # ff the game is already over --> stop
        if old_state in ["Win", "Lose"]:
            runtime = time.time() - start_time
            agent.delete_game()
            return old_state, moves, total_reward, final_revealed_cells, runtime

        # ask agent to choose a move
        x, y = agent.choose_move(old_board)

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

        # if move ended the game return results
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
        "q_table_size": ""
    }


def evaluate_rl_agent(games=100, width=5, height=5, mine_count=3, training_episodes=1000):
    """
    Trains and evaluates the RLAgent
    """
    agent = RLAgent(width=width, height=height, mine_count=mine_count)
    print("\nTraining RLAgent...")
    agent.train(episodes=training_episodes)

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
        "q_table_size": len(agent.q_table)
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
        "q_table_size"
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

        if result["q_table_size"] != "":
            print(f"Q-table Size: {result['q_table_size']}")


if __name__ == "__main__":
    games = 100
    results = []

    # random baseline
    results.append(
        evaluate_agent(
            RandomAgent,
            "RandomAgent",
            games=games,
            width=10,
            height=10,
            mine_count=10
        )
    )

    # rule-based logical agent
    results.append(
        evaluate_agent(
            RuleBasedAgent,
            "RuleBasedAgent",
            games=games,
            width=10,
            height=10,
            mine_count=10
        )
    )

    # probability-based agent
    results.append(
        evaluate_agent(
            ProbabilityAgent,
            "ProbabilityAgent",
            games=games,
            width=10,
            height=10,
            mine_count=10
        )
    )

    # reinforcement learning agent
    results.append(
        evaluate_rl_agent(
            games=games,
            width=5,
            height=5,
            mine_count=3,
            training_episodes=1000
        )
    )

    print_results(results)
    save_results(results)