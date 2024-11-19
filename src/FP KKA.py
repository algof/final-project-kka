import pygame
import numpy as np
import sys
import random
import math

ROW_COUNT = 6
COLUMN_COUNT = 7
PLAYER = 0
BOT = 1
EMPTY = 0
PLAYER_PIECE = 1
BOT_PIECE = 2
WINDOW_LENGTH = 4
SQUARESIZE = 100
RADIUS = int(SQUARESIZE / 2 - 5)
width = COLUMN_COUNT * SQUARESIZE
height = (ROW_COUNT + 1) * SQUARESIZE
size = (width, height)
BLUE = (0, 0, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
WHITE = (255, 255, 255)

pygame.init()
screen = pygame.display.set_mode(size)
pygame.display.set_caption("Connect Four")
myfont = pygame.font.SysFont("monospace", 75)

player_color = RED
bot_color = YELLOW

def create_board():
    return np.zeros((ROW_COUNT, COLUMN_COUNT))

def draw_board(board):
    for c in range(COLUMN_COUNT):
        for r in range(ROW_COUNT):
            pygame.draw.rect(screen, BLUE, (c * SQUARESIZE, r * SQUARESIZE + SQUARESIZE, SQUARESIZE, SQUARESIZE))
            pygame.draw.circle(screen, BLACK, (int(c * SQUARESIZE + SQUARESIZE / 2), int(r * SQUARESIZE + SQUARESIZE + SQUARESIZE / 2)), RADIUS)

    for c in range(COLUMN_COUNT):
        for r in range(ROW_COUNT):
            if board[r][c] == PLAYER_PIECE:
                pygame.draw.circle(screen, player_color, (int(c * SQUARESIZE + SQUARESIZE / 2), height - int(r * SQUARESIZE + SQUARESIZE / 2)), RADIUS)
            elif board[r][c] == BOT_PIECE:
                pygame.draw.circle(screen, bot_color, (int(c * SQUARESIZE + SQUARESIZE / 2), height - int(r * SQUARESIZE + SQUARESIZE / 2)), RADIUS)

    pygame.display.update()

def drop_piece(board, row, col, piece):
    board[row][col] = piece

def animate_chip_drop(board, col, piece, color):
    row = get_next_open_row(board, col)
    x = col * SQUARESIZE + SQUARESIZE // 2
    y = SQUARESIZE // 2

    while y < (ROW_COUNT - row) * SQUARESIZE + SQUARESIZE // 2:
        pygame.draw.rect(screen, BLACK, (0, 0, width, SQUARESIZE))  
        draw_board(board)
        pygame.draw.circle(screen, color, (x, y), RADIUS)
        pygame.display.update()
        pygame.time.wait(10)  
        y += 20  

    drop_piece(board, row, col, piece)
    draw_board(board)

def is_valid_location(board, col):
    return board[ROW_COUNT - 1][col] == 0

def get_next_open_row(board, col):
    for r in range(ROW_COUNT):
        if board[r][col] == 0:
            return r

def winning_move(board, piece):
    for c in range(COLUMN_COUNT - 3):
        for r in range(ROW_COUNT):
            if all(board[r][c + i] == piece for i in range(4)):
                return True

    for c in range(COLUMN_COUNT):
        for r in range(ROW_COUNT - 3):
            if all(board[r + i][c] == piece for i in range(4)):
                return True

    for c in range(COLUMN_COUNT - 3):
        for r in range(ROW_COUNT - 3):
            if all(board[r + i][c + i] == piece for i in range(4)):
                return True

    for c in range(COLUMN_COUNT - 3):
        for r in range(3, ROW_COUNT):
            if all(board[r - i][c + i] == piece for i in range(4)):
                return True

    return False


def evaluate_window(window, piece):
    score = 0
    opp_piece = PLAYER_PIECE if piece == BOT_PIECE else BOT_PIECE

    if window.count(piece) == 4:
        score += 100
    elif window.count(piece) == 3 and window.count(EMPTY) == 1:
        score += 5
    elif window.count(piece) == 2 and window.count(EMPTY) == 2:
        score += 2

    if window.count(opp_piece) == 3 and window.count(EMPTY) == 1:
        score -= 4

    return score

def score_position(board, piece):
    score = 0

    center_array = [int(i) for i in list(board[:, COLUMN_COUNT // 2])]
    center_count = center_array.count(piece)
    score += center_count * 3

    for r in range(ROW_COUNT):
        row_array = [int(i) for i in list(board[r, :])]
        for c in range(COLUMN_COUNT - 3):
            window = row_array[c:c + WINDOW_LENGTH]
            score += evaluate_window(window, piece)

    for c in range(COLUMN_COUNT):
        col_array = [int(i) for i in list(board[:, c])]
        for r in range(ROW_COUNT - 3):
            window = col_array[r:r + WINDOW_LENGTH]
            score += evaluate_window(window, piece)

    for r in range(ROW_COUNT - 3):
        for c in range(COLUMN_COUNT - 3):
            window = [board[r + i][c + i] for i in range(WINDOW_LENGTH)]
            score += evaluate_window(window, piece)

    for r in range(ROW_COUNT - 3):
        for c in range(COLUMN_COUNT - 3):
            window = [board[r + 3 - i][c + i] for i in range(WINDOW_LENGTH)]
            score += evaluate_window(window, piece)

    return score

def is_terminal_node(board):
    return winning_move(board, PLAYER_PIECE) or winning_move(board, BOT_PIECE) or len(get_valid_locations(board)) == 0

def minimax(board, depth, alpha, beta, maximizingPlayer):
    valid_locations = get_valid_locations(board)
    is_terminal = is_terminal_node(board)
    if depth == 0 or is_terminal:
        if is_terminal:
            if winning_move(board, BOT_PIECE):
                return (None, 100000000000000)
            elif winning_move(board, PLAYER_PIECE):
                return (None, -100000000000000)
            else:  
                return (None, 0)
        else:  
            return (None, score_position(board, BOT_PIECE))

    if maximizingPlayer:
        value = -math.inf
        column = random.choice(valid_locations)
        for col in valid_locations:
            row = get_next_open_row(board, col)
            temp_board = board.copy()
            drop_piece(temp_board, row, col, BOT_PIECE)
            new_score = minimax(temp_board, depth - 1, alpha, beta, False)[1]
            if new_score > value:
                value = new_score
                column = col
            alpha = max(alpha, value)
            if alpha >= beta:
                break
        return column, value

    else:  
        value = math.inf
        column = random.choice(valid_locations)
        for col in valid_locations:
            row = get_next_open_row(board, col)
            temp_board = board.copy()
            drop_piece(temp_board, row, col, PLAYER_PIECE)
            new_score = minimax(temp_board, depth - 1, alpha, beta, True)[1]
            if new_score < value:
                value = new_score
                column = col
            beta = min(beta, value)
            if alpha >= beta:
                break
        return column, value


def get_valid_locations(board):
    return [c for c in range(COLUMN_COUNT) if is_valid_location(board, c)]

def main():
    global player_color, bot_color

    screen.fill(WHITE)
    text_red = myfont.render("Red", True, RED)
    text_yellow = myfont.render("Yellow", True, YELLOW)
    screen.blit(text_red, (width // 4 - text_red.get_width() // 2, height // 2 - text_red.get_height() // 2))
    screen.blit(text_yellow, (3 * width // 4 - text_yellow.get_width() // 2, height // 2 - text_yellow.get_height() // 2))
    pygame.display.update()

    color_selected = False
    while not color_selected:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                x_pos = event.pos[0]
                if x_pos < width // 2:
                    player_color = RED
                    bot_color = YELLOW
                else:
                    player_color = YELLOW
                    bot_color = RED
                color_selected = True

    board = create_board()
    game_over = False
    turn = random.choice([PLAYER, BOT])
    draw_board(board)

    while not game_over:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()

            if event.type == pygame.MOUSEMOTION:
                pygame.draw.rect(screen, BLACK, (0, 0, width, SQUARESIZE))
                posx = event.pos[0]
                pygame.draw.circle(screen, player_color, (posx, SQUARESIZE // 2), RADIUS)
                pygame.display.update()

            if event.type == pygame.MOUSEBUTTONDOWN:
                pygame.draw.rect(screen, BLACK, (0, 0, width, SQUARESIZE))

                if turn == PLAYER:
                    posx = event.pos[0]
                    col = posx // SQUARESIZE

                    if is_valid_location(board, col):
                        row = get_next_open_row(board, col)
                        animate_chip_drop(board, col, PLAYER_PIECE, player_color)

                        if winning_move(board, PLAYER_PIECE):
                            game_over = True
                            display_winner("Player Wins!")
                        turn = BOT

        if turn == BOT and not game_over:
            col, minimax_score = minimax(board, 5, -math.inf, math.inf, True)

            if is_valid_location(board, col):
                pygame.time.wait(500)
                row = get_next_open_row(board, col)
                animate_chip_drop(board, col, BOT_PIECE, bot_color)

                if winning_move(board, BOT_PIECE):
                    game_over = True
                    display_winner("Bot Wins!")
                turn = PLAYER

        draw_board(board)

        if game_over:
            pygame.time.wait(3000)
            show_end_buttons()

def display_winner(text):
    pygame.draw.rect(screen, WHITE, (0, 0, width, SQUARESIZE))
    label = myfont.render(text, True, BLACK)
    screen.blit(label, (width // 2 - label.get_width() // 2, SQUARESIZE // 2 - label.get_height() // 2))
    pygame.display.update()

def show_end_buttons():
    screen.fill(WHITE)
    text_refresh = myfont.render("Refresh", True, BLUE)
    text_quit = myfont.render("Quit", True, RED)
    screen.blit(text_refresh, (width // 4 - text_refresh.get_width() // 2, height // 2 - text_refresh.get_height() // 2))
    screen.blit(text_quit, (3 * width // 4 - text_quit.get_width() // 2, height // 2 - text_quit.get_height() // 2))
    pygame.display.update()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                x_pos = event.pos[0]
                if x_pos < width // 2:
                    main() 
                else:
                    sys.exit()

if __name__ == "__main__":
    main()
