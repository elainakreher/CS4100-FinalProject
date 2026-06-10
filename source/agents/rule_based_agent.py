"""
RuleBasedAgent uses basic Minesweeper logic to choose moves

Logic:
- doesnt calculate probabilities & only makes guaranteed safe moves when possible
- if no guaranteed safe move exists, it falls back to a random unknown cell 
"""
import random
from source.agents.base_agent import BaseAgent

class RuleBasedAgent(BaseAgent):
    def __init__(self, api_url="http://localhost:8080", width=10, height=10, mine_count=10):
        """
        Initializes the rule-based agent
        known_mines stores cells that the agent believes are definitely mines
        safe_moves stores cells that the agent believes are safe to reveal
        """
        super().__init__(api_url, width, height, mine_count)

        self.known_mines = set()
        self.safe_moves = set()

    def get_neighbors(self, board, x, y):
        """
        Returns all valid neighboring cells around position (x, y)
        """
        neighbors = []
        width = len(board)
        height = len(board[0])

        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:

                # skip the cell itself
                if dx == 0 and dy == 0:
                    continue

                new_x = x + dx
                new_y = y + dy

                # make sure the neighbor is inside the board
                if 0 <= new_x < width and 0 <= new_y < height:
                    neighbors.append((new_x, new_y))

        return neighbors

    def analyze_board(self, board):
        """
        Applies basic Minesweeper logic to the current board

        Rule 1:
        If the number of hidden neighbors equals the number of remaining mines, then all hidden neighbors must be mines

        Rule 2:
        If all mines around a revealed clue are already known, then the remaining hidden neighbors are safe
        """
        # loop through every cell on the board
        for x in range(len(board)):
            for y in range(len(board[x])):

                cell_value = board[x][y]
                # only revealed numbered cells give useful information
                if cell_value < 0 or cell_value > 8:
                    continue

                neighbors = self.get_neighbors(board, x, y)
                hidden_neighbors = []
                known_mine_neighbors = []

                for neighbor in neighbors:
                    nx, ny = neighbor

                    # -1 means the cell is still hidden
                    if board[nx][ny] == -1:

                        if neighbor in self.known_mines:
                            known_mine_neighbors.append(neighbor)
                        else:
                            hidden_neighbors.append(neighbor)

                # how many mines still need to be found around this clue
                remaining_mines = cell_value - len(known_mine_neighbors)

                # Rule 1
                if remaining_mines == len(hidden_neighbors) and remaining_mines > 0:
                    for hidden_cell in hidden_neighbors:
                        self.known_mines.add(hidden_cell)

                # Rule 2
                if remaining_mines == 0:
                    for hidden_cell in hidden_neighbors:
                        self.safe_moves.add(hidden_cell)

    def choose_move(self, board):
        """
        Chooses the next move for the RuleBasedAgent
        Analyze the board using deterministic Minesweeper rules
            If a guaranteed safe move exists, reveal it
            If not --> fall back to a random unknown cell that is not known to be a mine
        """
        self.analyze_board(board)

        # remove any safe moves that are no longer hidden
        self.safe_moves = {
            (x, y)
            for (x, y) in self.safe_moves
            if board[x][y] == -1 and (x, y) not in self.known_mines
        }

        # if we found a guaranteed safe move use it
        if self.safe_moves:
            return self.safe_moves.pop()

        # if no safe move exists choose randomly from unknown cells
        unknown_cells = self.get_unknown_cells(board)

        # dont intentionally click cells we believe are mines
        possible_moves = [
            cell for cell in unknown_cells
            if cell not in self.known_mines
        ]

        if not possible_moves:
            raise Exception("No possible moves left.")

        return random.choice(possible_moves)


if __name__ == "__main__":
    agent = RuleBasedAgent(width=10, height=10, mine_count=10)
    result = agent.play_game()
    print("RuleBasedAgent finished with result:", result)