import random
import json
import time
from source.agents.base_agent import BaseAgent


class RLAgent(BaseAgent):
    def __init__(
        self,
        api_url="http://localhost:8080",
        width=5,
        height=5,
        mine_count=3,
        learning_rate=0.1,
        discount_factor=0.9,
        epsilon=0.2,
        epsilon_decay=0.995
    ):
        """
        width/height/mine_count are smaller by default because RL needs many games
        learning_rate = how much the agent updates old knowledge with new information
        discount_factor =  how much the agent cares about future rewards
        epsilon = exploration rate (higher epsilon means more random moves)
        """

        super().__init__(api_url, width, height, mine_count)

        self.learning_rate = learning_rate
        self.discount_factor = discount_factor
        self.epsilon = epsilon
        self.epsilon_decay = epsilon_decay

        # Key format: (state_key, action)
        # state_key = simplified version of current board
        # action = (x, y)
        self.q_table = {}

        # for calculating eta
        self.update_counts = {}


    def get_state_key(self, board):
        """
        Converts the board into a hashable format
        """
        return tuple(tuple(row) for row in board)

    def get_q_value(self, state_key, action):
        """
        Gets the Q-value for a specific state-action pair
        """
        return self.q_table.get((state_key, action), 0.0)

    def choose_move(self, board):
        """
        Chooses a move using epsilon-greedy strategy
        """
        unknown_cells = self.get_unknown_cells(board)

        if not unknown_cells:
            raise Exception("No unknown cells left to choose from.")

        state_key = self.get_state_key(board)

        # choose a random move
        if random.random() < self.epsilon:
            return random.choice(unknown_cells)

        # choose the move with the highest Q-value
        best_move = None
        best_value = float("-inf")

        for action in unknown_cells:
            q_value = self.get_q_value(state_key, action)

            if q_value > best_value:
                best_value = q_value
                best_move = action

        return best_move

    def calculate_reward(self, old_board, new_board, new_state):
        """
        Gives the agent a reward after each move
        """
        if new_state == "Win":
            return 100  # change reward values

        if new_state == "Lose":
            return -100 # change values

        # count how many cells were revealed after the move
        old_hidden = sum(row.count(-1) for row in old_board)
        new_hidden = sum(row.count(-1) for row in new_board)

        cells_revealed = old_hidden - new_hidden

        # reward the agent for safely revealing cells
        if cells_revealed > 0:
            return 1 + cells_revealed

        # small penalty if nothing useful happened
        return -1

    def update_q_value(self, old_state_key, action, reward, new_state_key, new_board):
        """
        Updates the Q-table using the Q-learning formula

        New Q-value =
        old Q-value + learning_rate * (reward + future reward - old Q-value)
        """

        old_q = self.get_q_value(old_state_key, action)

        count = self.update_counts.get((old_state_key, action), 0)
        eta = 1 / (1 + count)
        self.update_counts[(old_state_key, action)] = count + 1

        possible_next_actions = self.get_unknown_cells(new_board)

        if possible_next_actions:
            future_q_values = [
                self.get_q_value(new_state_key, next_action)
                for next_action in possible_next_actions
            ]
            max_future_q = max(future_q_values)
        else:
            max_future_q = 0

        updated_q = old_q + eta * (
            reward + self.discount_factor * max_future_q - old_q
        )

        self.q_table[(old_state_key, action)] = updated_q

    def train_one_game(self):
        """
        Trains the agent on one full Minesweeper game
        """
        self.create_game()

        while True:
            old_game_state = self.get_game_state()
            old_board = old_game_state["board"]
            old_state_key = self.get_state_key(old_board)

            action = self.choose_move(old_board)
            x, y = action
        
            move_result = self.make_move(x, y)
            new_state = move_result["new_state"]

            new_game_state = self.get_game_state()
            new_board = new_game_state["board"]
            new_state_key = self.get_state_key(new_board)

            reward = self.calculate_reward(old_board, new_board, new_state)

            self.update_q_value(
                old_state_key,
                action,
                reward,
                new_state_key,
                new_board
            )

            self.epsilon = max(0.01, self.epsilon * self.epsilon_decay)

            if new_state == "Win" or new_state == "Lose":
                self.delete_game()
                return new_state

    def train(self, episodes=1000): 
        """
        Trains the RL agent over many games
        """
        wins = 0
        losses = 0

        for episode in range(episodes):
            result = self.train_one_game()

            if result == "Win":
                wins += 1
            else:
                losses += 1

            if (episode + 1) % 100 == 0:
                print(
                    episode + 1,
                    " Episodes Complete:",
                    wins,
                    " Wins | ",
                    losses,
                    "Losses | ",
                    len(self.q_table),
                    " entries in Q-table | ",
                    round(wins / (wins + losses) * 100, 2),
                    "% win rate"

                )

        print("Training complete.")
        print("Final wins:", wins)
        print("Final losses:", losses)

    def save_q_table(self, filename="results/q_table.json"):
        """
        Saving the Q-table
        """
        q_table_as_strings = {
            str(key): value
            for key, value in self.q_table.items()
        }

        with open(filename, "w") as file:
            json.dump(q_table_as_strings, file)

    def load_q_table(self, filename="results/q_table.json"):
        """
        loading a Q-table
        """
        with open(filename, "r") as file:
            q_table_as_strings = json.load(file)
    
        self.q_table = {
            eval(key): value
            for key, value in q_table_as_strings.items()
    }

    def play_trained_game(self):
        """
        Plays one game using learned Q-values
        """
        old_epsilon = self.epsilon
        self.epsilon = 0 # epsilon temporarily set to 0 so the agent only uses what it learned

        result = self.play_game()

        self.epsilon = old_epsilon

        return result


if __name__ == "__main__":
    agent = RLAgent(width=5, height=5, mine_count=3)
    agent.train(episodes=10000) # can change values of episodes
    agent.save_q_table()
    result = agent.play_trained_game()
    print("Trained RLAgent finished with result:", result)
