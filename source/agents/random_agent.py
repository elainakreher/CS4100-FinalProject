"""
This file defines the RandomAgent class

RandomAgent is the simplest possible Minesweeper AI agent (doesnt use logic or probability)

1. Looks at the current visible board
2. Finds all unknown cells
3. Randomly chooses one unknown cell
4. Reveals that cell
"""
import random
from source.agents.base_agent import BaseAgent

class RandomAgent(BaseAgent):
    def choose_move(self, board):
        """
        Chooses a random unknown cell from the board

        Input:
        board: 2D list from the Minesweeper API
              -1 means the cell is still hidden
               0-8 means the cell has already been revealed
        Output:
            (x, y): coordinates of the cell the agent wants to reveal
        """

        # use the helper method from base agent to find all hidden cells
        unknown_cells = self.get_unknown_cells(board)

        # if there are no unknown cells left something is wrong or the game is over
        if not unknown_cells:
            raise Exception("No unknown cells left to choose from.")

        # randomly pick one hidden cell
        move = random.choice(unknown_cells)

        # return the move as an (x, y) coordinate pair
        return move


if __name__ == "__main__":
    agent = RandomAgent(width=10, height=10, mine_count=10)
    result = agent.play_game()
    print("RandomAgent finished with result:", result)