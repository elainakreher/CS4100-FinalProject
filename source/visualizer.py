import pygame
import requests
import sys
import time

# --- Config ---
BASE_URL = "http://localhost:8000"
CELL_SIZE = 40
MARGIN = 2

# --- Colors ---
HIDDEN   = (180, 180, 180)
EMPTY    = (220, 220, 220)
MINE     = (255, 0, 0)
NUMBERS  = {
    1: (0, 0, 255),
    2: (0, 128, 0),
    3: (255, 0, 0),
    4: (0, 0, 128),
    5: (128, 0, 0),
    6: (0, 128, 128),
    7: (0, 0, 0),
    8: (128, 128, 128),
}

def create_game(width=10, height=10, mines=10):
    r = requests.put(BASE_URL + "/", json={"width": width, "height": height, "mine_count": mines})
    return r.json()["id"]

def get_state(game_id):
    r = requests.get(f"{BASE_URL}/{game_id}")
    return r.json()

def draw_board(screen, board, font):
    for y, row in enumerate(board):
        for x, cell in enumerate(row):
            rect = (x * CELL_SIZE + MARGIN, y * CELL_SIZE + MARGIN,
                    CELL_SIZE - MARGIN * 2, CELL_SIZE - MARGIN * 2)
            if cell == -1:
                pygame.draw.rect(screen, HIDDEN, rect)
            elif cell == 0:
                pygame.draw.rect(screen, EMPTY, rect)
            elif cell == 9:
                pygame.draw.rect(screen, MINE, rect)
            else:
                pygame.draw.rect(screen, EMPTY, rect)
                text = font.render(str(cell), True, NUMBERS.get(cell, (0,0,0)))
                screen.blit(text, (x * CELL_SIZE + 14, y * CELL_SIZE + 10))

def main():
    pygame.init()
    font = pygame.font.SysFont(None, 28)

    game_id = create_game()
    state = get_state(game_id)

    width = state["width"]
    height = state["height"]

    screen = pygame.display.set_mode((width * CELL_SIZE, height * CELL_SIZE))
    pygame.display.set_caption("Minesweeper")

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        state = get_state(game_id)
        screen.fill((100, 100, 100))
        draw_board(screen, state["board"], font)
        pygame.display.flip()
        time.sleep(0.5) 

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()