from random import shuffle
from enum import Enum

class Minesweeper:
    class GameState(str, Enum):
        FIRST = 'First Move'
        PLAYING = 'Playing'
        WIN = 'Win'
        LOSE = 'Lose'


    class CellContent(Enum):
        UNKNOWN = -1
        EMPTY = 0
        MINE = 9


    class CellPrintChar(str, Enum):
        UNKNOWN = '?'
        EMPTY = '-'
        MINE = 'X'


    def __init__(self, width=10, height=10, mine_count=10):
        # Check there are not more mines than cells
        if mine_count > width * height:
            raise ValueError('There can not be more mines than cells ' +
                '(got %d mines and %d total cells)' % (mine_count, width * height))

        # Store variables
        self.width = width
        self.height = height
        self.mine_count = mine_count
        self.cell_count = width * height
        self.hidden_cells = self.cell_count
        self.game_state = Minesweeper.GameState.FIRST

        self.cells_mines = None
        self.cells_revealed = None
        self.cells_neighboring = None

        self.init_mine_field()


    def init_mine_field(self):
        # Create mine field
        base_cells = [True] * self.mine_count + \
            [False] * (self.cell_count - self.mine_count)
        shuffle(base_cells)

        # Create 2D lists
        self.cells_mines = [base_cells[i*self.height:(i+1)*self.height] \
            for i in range(self.width)]
        self.cells_revealed = [[False] * self.height for _ in range(self.width)]
        self.cells_neighboring = [
            [
                sum([self.cells_mines[i][j] for i, j in self.neighbors(x, y)])
                for y in range(self.height)
            ]
            for x in range(self.width)
        ]


    def neighbors(self, x, y):
        for i in range(-1, 2):
            if 0 <= x-i < self.width:
                for j in range(-1, 2):
                    if 0 <= y-j < self.height:
                        if not i == j == 0:
                            yield (x-i, y-j)


    def print_internal_state(self):
        print('=====')
        print('Width: %3d \tHeight: %3d \tMines %3d' % \
            (self.width, self.height, self.mine_count))
        print('State: %s' % repr(self.game_state.value))
        print('-----')
        for x in range(self.width):
            line = ''.join(Minesweeper.CellPrintChar.MINE.value \
                if self.cells_mines[x][y] \
                else Minesweeper.CellPrintChar.EMPTY.value \
                for y in range(self.height))
            print('\t' + line)
        print('=====')


    def print_visible_state(self):
        print('=====')
        print('State: %s' % repr(self.game_state.value))
        print('-----')
        for x in range(self.width):
            line = ''.join(
                (
                    Minesweeper.CellPrintChar.MINE.value \
                    if self.cells_mines[x][y] \
                    else str(self.cells_neighboring[x][y]) \
                )
                if self.cells_revealed[x][y]
                else Minesweeper.CellPrintChar.UNKNOWN.value
                for y in range(self.height))
            print('\t' + line)
        print('=====')


    def get_visible_cells(self):
        return \
        [
            [
                (
                    Minesweeper.CellContent.MINE.value \
                    if self.cells_mines[x][y] \
                    else self.cells_neighboring[x][y] \
                )
                if self.cells_revealed[x][y]
                else Minesweeper.CellContent.UNKNOWN.value
                for y in range(self.height)
            ]
            for x in range(self.width)
        ]


    def reveal(self, x, y):
        if not self.cells_revealed[x][y]:
            self.cells_revealed[x][y] = True
            self.hidden_cells -= 1


    def floodfill_empty(self, initial):
        pending = {initial}

        # While pending cells
        while pending:
            # Pop cell
            x, y = pending.pop()
            # Set to revealed
            self.reveal(x, y)
            # Add neighbors to pending set if cell is empty
            if self.cells_neighboring[x][y] == Minesweeper.CellContent.EMPTY.value:
                pending |= {
                    (x, y) for x, y in self.neighbors(x, y) if \
                    not self.cells_revealed[x][y] \
                }


    def is_finished(self):
        return self.game_state in (Minesweeper.GameState.WIN,
            Minesweeper.GameState.LOSE)


    def open_cell(self, x, y):
        # Check the game is not finished
        if self.is_finished():
            raise Exception('Game is finished')

        # Ensure first action does not lose the game
        if self.game_state == Minesweeper.GameState.FIRST:
            while self.cells_mines[x][y]:
                self.init_mine_field()
            self.game_state = Minesweeper.GameState.PLAYING

        # Reveal cell
        self.reveal(x, y)
        if self.cells_mines[x][y]:
            self.game_state = Minesweeper.GameState.LOSE
        else:
            if self.cells_neighboring[x][y] == Minesweeper.CellContent.EMPTY.value:
                self.floodfill_empty((x, y))

        # Check victory condition
        if self.hidden_cells == self.mine_count:
            self.game_state = Minesweeper.GameState.WIN
