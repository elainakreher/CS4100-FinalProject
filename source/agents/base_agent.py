"""
This file defines the BaseAgent class

BaseAgent is NOT one of the agents we evaluate, its the parent class that all other agents will inherit from

It handles these tasks:
- connecting to the Minesweeper API
- creating a new game
- getting the current board
- sending a move
- deleting a finished game

Each specific agent only has to implement choose_move()
"""

import json
import urllib.request


class BaseAgent:
    def __init__(self, api_url="http://localhost:8080", width=10, height=10, mine_count=10):
        """
        Initializes the agent

        Inputs:
        api_url: where the Minesweeper API is running
        width: board width
        height: board height
        mine_count: number of mines on the board
        """

        self.api_url = api_url
        self.width = width
        self.height = height
        self.mine_count = mine_count
        self.game_id = None

    def create_game(self):
        """
        Creates a new Minesweeper game using a PUT request
        The API returns a game ID which we save so the agent can keep playing that specific game
        """

        data = {
            "width": self.width,
            "height": self.height,
            "mine_count": self.mine_count
        }

        request = urllib.request.Request(
            self.api_url + "/",
            data=json.dumps(data).encode("utf-8"),
            method="PUT"
        )

        response = urllib.request.urlopen(request)
        result = json.loads(response.read().decode("utf-8"))

        self.game_id = result["id"]
        return self.game_id

    def get_game_state(self):
        """
        Gets the current visible board using a GET request

        Outputs:
        - state: First Move, Playing, Win, or Lose
        - board: 2D list where:
            -1 = unknown cell
             0-8 = revealed number
             9 = mine
        """

        request = urllib.request.Request(
            self.api_url + "/" + self.game_id,
            method="GET"
        )

        response = urllib.request.urlopen(request)
        result = json.loads(response.read().decode("utf-8"))

        return result

    def make_move(self, x, y):
        """
        Opens a cell on the board using a POST request

        Inputs:
        x: column coordinate
        y: row coordinate

        API responds with the new game state
        """
        data = {
            "x": x,
            "y": y
        }

        request = urllib.request.Request(
            self.api_url + "/" + self.game_id,
            data=json.dumps(data).encode("utf-8"),
            method="POST"
        )

        response = urllib.request.urlopen(request)
        result = json.loads(response.read().decode("utf-8"))

        return result

    def delete_game(self):
        """
        Deletes the current game from the API (useful after agent finishes playing so old games dont stay stored in memory)
        """
        if self.game_id is None:
            return

        request = urllib.request.Request(
            self.api_url + "/" + self.game_id,
            method="DELETE"
        )

        urllib.request.urlopen(request)
        self.game_id = None

    def get_unknown_cells(self, board):
        """
        Finds all cells that are still hidden (unknown cells are represented by -1)

        Output:
        a list of coordinate pairs: [(x1, y1), (x2, y2), ...]
        """

        unknown_cells = []

        for x in range(len(board)):
            for y in range(len(board[x])):
                if board[x][y] == -1:
                    unknown_cells.append((x, y))

        return unknown_cells

    def choose_move(self, board):
        """
        This method must be written by each specific agent
        BaseAgent does not know how to choose a move itself
        """

        raise NotImplementedError("Each agent must implement choose_move().")

    def play_game(self):
        """
        Plays one complete game
        1. Creates a game
        2. Gets the board
        3. Asks the specific agent to choose a move
        4. Sends the move to the API
        5. Repeats until the game ends
        """

        self.create_game()

        while True:
            game_state = self.get_game_state()
            state = game_state["state"]
            board = game_state["board"]

            if state == "Win" or state == "Lose":
                return state

            move, rand = self.choose_move(board)
            x, y = move
            move_result = self.make_move(x, y)

            new_state = move_result["new_state"]

            if new_state == "Win" or new_state == "Lose":
                return new_state