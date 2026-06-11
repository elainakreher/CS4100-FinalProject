import pygame

CELL_SIZE = 40
MARGIN = 2

HIDDEN  = (180, 180, 180)
EMPTY   = (220, 220, 220)
MINE    = (255, 60,  60)
FLAG    = (255, 200, 0)

NUMBER_COLORS = {
    1: (0,   0,   255),
    2: (0,   128, 0),
    3: (200, 0,   0),
    4: (0,   0,   128),
    5: (128, 0,   0),
    6: (0,   128, 128),
    7: (0,   0,   0),
    8: (100, 100, 100),
}


def board_surface_size(board):
    height = len(board)
    width  = len(board[0]) if height > 0 else 0
    return width * CELL_SIZE, height * CELL_SIZE


def draw_board(screen, board, font):
    """
    Draws the current board state.

    board: 2D list where
        -1 = hidden
         0 = revealed, no adjacent mines
         1-8 = revealed, number of adjacent mines
         9 = mine (revealed on loss)
    """
    for y, row in enumerate(board):
        for x, cell in enumerate(row):
            rect = (
                x * CELL_SIZE + MARGIN,
                y * CELL_SIZE + MARGIN,
                CELL_SIZE - MARGIN * 2,
                CELL_SIZE - MARGIN * 2,
            )

            if cell == -1:
                pygame.draw.rect(screen, HIDDEN, rect)

            elif cell == 0:
                pygame.draw.rect(screen, EMPTY, rect)

            elif cell == 9:
                pygame.draw.rect(screen, MINE, rect)

            else:
                pygame.draw.rect(screen, EMPTY, rect)
                color = NUMBER_COLORS.get(cell, (0, 0, 0))
                text  = font.render(str(cell), True, color)
                text_x = x * CELL_SIZE + (CELL_SIZE - text.get_width())  // 2
                text_y = y * CELL_SIZE + (CELL_SIZE - text.get_height()) // 2
                screen.blit(text, (text_x, text_y))


def init_display(board, title="Minesweeper"):
    pygame.init()
    font   = pygame.font.SysFont(None, 28)
    w, h   = board_surface_size(board)
    screen = pygame.display.set_mode((w, h))
    pygame.display.set_caption(title)
    return screen, font


def render(screen, board, font, bg=(100, 100, 100)):
    screen.fill(bg)
    draw_board(screen, board, font)
    pygame.display.flip()


def poll_quit():
    " has the user closed the pygame window? "
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            return True
    return False