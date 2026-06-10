import random
from source.agents.rule_based_agent import RuleBasedAgent


class ProbabilityAgent(RuleBasedAgent):
    def get_cell_probabilities(self, board):
        probabilities = {}

        for x in range(len(board)):
            for y in range(len(board[x])):
                cell_value = board[x][y]

                if cell_value < 0 or cell_value > 8:
                    continue

                neighbors = self.get_neighbors(board, x, y)

                hidden_neighbors = []
                known_mine_count = 0

                for neighbor in neighbors:
                    nx, ny = neighbor

                    if neighbor in self.known_mines:
                        known_mine_count += 1
                    elif board[nx][ny] == -1:
                        hidden_neighbors.append(neighbor)

                remaining_mines = cell_value - known_mine_count

                if len(hidden_neighbors) == 0:
                    continue

                probability = remaining_mines / len(hidden_neighbors)

                for hidden_cell in hidden_neighbors:
                    if hidden_cell not in probabilities:
                        probabilities[hidden_cell] = []

                    probabilities[hidden_cell].append(probability)

        averaged_probabilities = {}

        for cell in probabilities:
            averaged_probabilities[cell] = sum(probabilities[cell]) / len(probabilities[cell])

        return averaged_probabilities

    def choose_move(self, board):
        self.analyze_board(board)

        self.safe_moves = {
            (x, y)
            for (x, y) in self.safe_moves
            if board[x][y] == -1 and (x, y) not in self.known_mines
        }

        if self.safe_moves:
            return self.safe_moves.pop()

        probabilities = self.get_cell_probabilities(board)

        possible_moves = [
            cell for cell in self.get_unknown_cells(board)
            if cell not in self.known_mines
        ]

        if not possible_moves:
            raise Exception("No possible moves left.")

        if not probabilities:
            return random.choice(possible_moves)

        best_probability = min(
            probabilities[cell]
            for cell in probabilities
            if cell in possible_moves
        )

        best_moves = [
            cell for cell in possible_moves
            if cell in probabilities and probabilities[cell] == best_probability
        ]

        if best_moves:
            return random.choice(best_moves)

        return random.choice(possible_moves)

    def play_game(self):
        self.known_mines = set()
        self.safe_moves = set()
        return super().play_game()


if __name__ == "__main__":
    agent = ProbabilityAgent(width=10, height=10, mine_count=10)
    result = agent.play_game()
    print("ProbabilityAgent finished with result:", result)