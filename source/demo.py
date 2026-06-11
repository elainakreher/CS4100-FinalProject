import sys
import time
import pygame
import argparse

from source.visualizer import init_display, render, poll_quit
from source.agents.random_agent import RandomAgent
from source.agents.rule_based_agent import RuleBasedAgent
from source.agents.probability_agent import ProbabilityAgent
from source.agents.rl_agent import RLAgent
from source.agents.dqn_agent import DQNAgent


parser = argparse.ArgumentParser(description="Minesweeper agent visualizer")
parser.add_argument(
    "agent",
    choices=["random", "rule_based", "probability", "rl", "dqn"],
    help="which agent to run"
)
args = parser.parse_args()

if args.agent == "random":
    agent = RandomAgent(width=10, height=10, mine_count=10)
elif args.agent == "rule_based":
    agent = RuleBasedAgent(width=10, height=10, mine_count=10)
elif args.agent == "probability":
    agent = ProbabilityAgent(width=10, height=10, mine_count=10)
elif args.agent == "rl":
    agent = RLAgent(width=5, height=5, mine_count=3)
    agent.load_q_table("results/q_table_1000000.json")
elif args.agent == "dqn":
    agent = DQNAgent(width=5, height=5, mine_count=3)
    agent.load_model("results/dqn_model.pth")



def run_demo(agent, delay=1):
    agent.create_game()
    
    game_state = agent.get_game_state()
    board = game_state["board"]
    
    screen, font = init_display(board)    

    result = None
    
    while True:
        if poll_quit():
            break
            
        game_state = agent.get_game_state()
        board = game_state["board"]
        state = game_state["state"]
        
        render(screen, board, font)
        
        if state in ("Win", "Lose"):
            result = state
            pygame.display.set_caption(f"Minesweeper — {state}")
            time.sleep(3)
            break
        
        x, y = agent.choose_move(board)
        agent.make_move(x, y)
        
        time.sleep(delay)
    
    agent.delete_game()
    pygame.quit()
    return result

if __name__ == "__main__":
    result = run_demo(agent)
    print(f"Game finished with result: {result}")