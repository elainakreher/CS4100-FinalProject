"""
The DQNAgent replaces the Q-table with a neural network that approximates
Q-values. Instead of memorizing individual board states, the network learns
patterns across similar states, allowing it to make reasonable decisions
even on board configurations it has never seen before.
- RLAgent = Q-table (memorization)
- DQNAgent = Neural network (generalization)
"""
import os
import random
from collections import deque
import torch
import torch.nn as nn
import torch.optim as optim
from source.agents.base_agent import BaseAgent

class DQN(nn.Module):
    """
    Simple feedforward network that predicts one Q-value per board cell
    """
    def __init__(self, input_size, output_size):
        super().__init__()
        self.network = nn.Sequential(
            nn.Linear(input_size, 128),
            nn.ReLU(),
            nn.Linear(128, 128),
            nn.ReLU(),
            nn.Linear(128, 64),
            nn.ReLU(),
            nn.Linear(64, output_size),
        )

    def forward(self, x):
        return self.network(x)


class DQNAgent(BaseAgent):
    def __init__(
            self,
            api_url="http://localhost:8080",
            width=5,
            height=5,
            mine_count=3,
            learning_rate=0.0005,  # lower = more stable
            discount_factor=0.95,
            epsilon=1.0,
            epsilon_decay=0.9995,  # slower decay so it explores longer
            epsilon_min=0.05,
            replay_buffer_size=10000,  # larger buffer
            batch_size=64,  # larger batches
            target_update_frequency=200,
    ):


        super().__init__(api_url=api_url, width=width, height=height, mine_count=mine_count)

        self.learning_rate = learning_rate
        self.discount_factor = discount_factor
        self.epsilon = epsilon
        self.epsilon_decay = epsilon_decay
        self.epsilon_min = epsilon_min
        self.batch_size = batch_size
        self.target_update_frequency = target_update_frequency

        self.input_size = self.width * self.height
        self.output_size = self.width * self.height

        self.policy_network = DQN(self.input_size, self.output_size)
        self.target_network = DQN(self.input_size, self.output_size)
        self.target_network.load_state_dict(self.policy_network.state_dict())
        self.target_network.eval()

        self.optimizer = optim.Adam(self.policy_network.parameters(), lr=self.learning_rate)
        self.loss_function = nn.MSELoss()

        self.replay_buffer = deque(maxlen=replay_buffer_size)
        self.training_rewards = []
        self.training_results = []

    def board_to_tensor(self, board):
        """
        Flattens a board into a length width * height float tensor

        Board values are encoded into a consistent [0, 1] range:
        - hidden cell (-1) -> 0.0
        - revealed clues (0-8) -> 0.1 through 0.9
        - revealed mine (9) -> 1.0

        This keeps hidden cells, empty revealed cells, clue numbers, and mines
        distinct without sending out-of-range values into the neural network.
        """

        flat_board = []
        for x in range(self.width):
            for y in range(self.height):
                cell = board[x][y]

                # Keep every board value in [0, 1] so the neural network receives consistently scaled inputs
                # Hidden cells map to 0.0 revealed clues map to 0.1-0.9 and revealed mines map to 1.0
                if cell == -1:
                    flat_board.append(0.0)
                else:
                    flat_board.append((cell + 1) / 10.0)

        return torch.tensor(flat_board, dtype=torch.float32)

    def action_to_xy(self, action):
        """
        Converts a single action index into an (x, y) board coordinate
        """
        x = action // self.height
        y = action % self.height
        return x, y

    def xy_to_action(self, x, y):
        """
        Converts an (x, y) board coordinate into a single action index
        """
        return x * self.height + y

    def get_valid_actions(self, board):
        """
        Returns action indexes for cells that are still hidden
        """
        valid_actions = []

        for x in range(self.width):
            for y in range(self.height):
                if board[x][y] == -1:
                    valid_actions.append(self.xy_to_action(x, y))

        return valid_actions

    def choose_move(self, board):
        """
        Chooses an (x, y) move using epsilon-greedy exploration
        BaseAgent.play_game() expects coordinates, so this method returns an (x, y) tuple instead of the integer action used internally by DQN
        """
        valid_actions = self.get_valid_actions(board)

        if not valid_actions:
            raise Exception("No valid hidden cells left to choose from.")

        if random.random() < self.epsilon:
            action = random.choice(valid_actions)
            return self.action_to_xy(action)

        state_tensor = self.board_to_tensor(board).unsqueeze(0)

        with torch.no_grad():
            q_values = self.policy_network(state_tensor).squeeze(0)

        best_action = max(valid_actions, key=lambda action: q_values[action].item())
        return self.action_to_xy(best_action)

    def calculate_reward(self, old_board, new_board, new_state):
        """
        Calculates the reward for one move
        """
        if new_state == "Win":
            return 500

        if new_state == "Lose":
            return -100

        old_hidden = sum(row.count(-1) for row in old_board)
        new_hidden = sum(row.count(-1) for row in new_board)
        cells_revealed = old_hidden - new_hidden

        if cells_revealed > 0:
            return cells_revealed * 2  # reward each revealed cell more
        return -0.5  # smaller penalty for neutral moves

    def store_experience(self, state, action, reward, next_state, next_board, done):
        """
        Stores one transition in replay memory
        """
        self.replay_buffer.append((state, action, reward, next_state, next_board, done))

    def train_step(self):
        """
        Trains the policy network on one random minibatch from replay memory
        """
        if len(self.replay_buffer) < self.batch_size * 10:
            return

        batch = random.sample(self.replay_buffer, self.batch_size)

        states = torch.stack([experience[0] for experience in batch])
        actions = torch.tensor([experience[1] for experience in batch], dtype=torch.long)
        rewards = torch.tensor([experience[2] for experience in batch], dtype=torch.float32)
        next_states = torch.stack([experience[3] for experience in batch])
        next_boards = [experience[4] for experience in batch]
        dones = torch.tensor([experience[5] for experience in batch], dtype=torch.float32)

        current_q_values = self.policy_network(states)
        current_action_q_values = current_q_values.gather(1, actions.unsqueeze(1)).squeeze(1)

        with torch.no_grad():
            all_next_q_values = self.target_network(next_states)
            max_next_q_values = []

            for index, next_board in enumerate(next_boards):
                valid_next_actions = self.get_valid_actions(next_board)

                if valid_next_actions:
                    valid_q_values = all_next_q_values[index, valid_next_actions]
                    max_next_q_values.append(valid_q_values.max())
                else:
                    max_next_q_values.append(torch.tensor(0.0))

            max_next_q_values = torch.stack(max_next_q_values)
            target_q_values = rewards + self.discount_factor * max_next_q_values * (1 - dones)

        loss = self.loss_function(current_action_q_values, target_q_values)

        self.optimizer.zero_grad()
        loss.backward()
        self.optimizer.step()

    def train_one_game(self):
        """
        Creates one game, plays until it ends, and trains after each move
        """
        self.create_game()
        total_reward = 0

        try:
            while True:
                old_game_state = self.get_game_state()
                old_board = old_game_state["board"]
                old_state_tensor = self.board_to_tensor(old_board)

                x, y = self.choose_move(old_board)
                action = self.xy_to_action(x, y)

                move_result = self.make_move(x, y)
                new_state = move_result["new_state"]

                new_game_state = self.get_game_state()
                new_board = new_game_state["board"]
                new_state_tensor = self.board_to_tensor(new_board)

                reward = self.calculate_reward(old_board, new_board, new_state)
                total_reward += reward

                done = new_state in ("Win", "Lose")

                self.store_experience(
                    old_state_tensor,
                    action,
                    reward,
                    new_state_tensor,
                    new_board,
                    done,
                )

                self.train_step()

                if done:
                    return new_state, total_reward
        finally:
            self.delete_game()

    def train(self, episodes=1000):
        """
        Trains the DQN agent across many games
        """
        wins = 0
        losses = 0

        for episode in range(episodes):
            result, total_reward = self.train_one_game()

            self.training_rewards.append(total_reward)
            self.training_results.append(result)

            if result == "Win":
                wins += 1
            else:
                losses += 1

            if self.epsilon > self.epsilon_min:
                self.epsilon *= self.epsilon_decay
                self.epsilon = max(self.epsilon, self.epsilon_min)

            if (episode + 1) % self.target_update_frequency == 0:
                self.target_network.load_state_dict(self.policy_network.state_dict())

            if (episode + 1) % 100 == 0:
                recent_rewards = self.training_rewards[-100:]
                recent_average_reward = sum(recent_rewards) / len(recent_rewards)

                print(
                    f"Episode {episode + 1}: "
                    f"Wins={wins}, "
                    f"Losses={losses}, "
                    f"Epsilon={self.epsilon:.3f}, "
                    f"Recent Avg Reward={recent_average_reward:.2f}"
                )

        print("Training complete.")
        print("Final wins:", wins)
        print("Final losses:", losses)

    def play_trained_game(self):
        """
        Plays one game greedily with the trained network
        """
        old_epsilon = self.epsilon
        self.epsilon = 0.0

        self.create_game()

        try:
            while True:
                game_state = self.get_game_state()
                state = game_state["state"]
                board = game_state["board"]

                if state in ("Win", "Lose"):
                    return state

                x, y = self.choose_move(board)
                move_result = self.make_move(x, y)
                new_state = move_result["new_state"]

                if new_state in ("Win", "Lose"):
                    return new_state
        finally:
            self.epsilon = old_epsilon
            self.delete_game()

    def save_model(self, filename="results/dqn_model.pth"):
        """
        Saves the policy network weights and creates results
        """
        directory = os.path.dirname(filename)
        if directory:
            os.makedirs(directory, exist_ok=True)

        torch.save(self.policy_network.state_dict(), filename)

    def load_model(self, filename="results/dqn_model.pth"):
        """
        Loads policy network weights and syncs the target network
        """
        self.policy_network.load_state_dict(torch.load(filename, map_location="cpu"))
        self.target_network.load_state_dict(self.policy_network.state_dict())
        self.target_network.eval()


if __name__ == "__main__":
    agent = DQNAgent(width=5, height=5, mine_count=3)
    agent.train(episodes=50000)
    result = agent.play_trained_game()
    print("DQNAgent finished with result:", result)
    agent.save_model("results/dqn_model.pth")