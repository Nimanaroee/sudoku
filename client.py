import numpy as np
import json
import pygame
import socket
import threading
import sys
import os

# Add Sudoku directory to path to import from src
sys.path.append(os.path.join(os.getcwd(), 'Sudoku'))
from Sudoku.src.solver import solver as SL

# Network Setup
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# IP of the computer running server.py (Found via ipconfig/ifconfig)
SERVER_IP = input("Enter Host IP: ") 
client.connect((SERVER_IP, 5555))

# Receive the board from server
initial_board_data = client.recv(1024).decode()
# ... Convert string to 9x9 grid ...
board_array = np.array(json.loads(initial_board_data))
solve_board_array = SL.SudoBruteSolve(board_array, 1)
fixed_cells = board_array != 0
selected_cell = None
highlight_cells = set()
wrong_answer = 0
wrong_cells = set()
flash_cells = [] # List of tuples (row, col, start_time)
MAX_WRONG_ANSWERS = 3
# Pygame Setup
pygame.init()
screen = pygame.display.set_mode((540, 600))
pygame.display.set_caption("Sudoku Client")
start_time = pygame.time.get_ticks()
ui_font = pygame.font.SysFont(None, 40)
font = pygame.font.SysFont(None, 48)

running = True
game_over = False

def listen_for_server():
    global game_over
    while True:
        msg = client.recv(1024).decode()
        if msg == "GAME_OVER_WINNER_FOUND":
            game_over = True
            print("Someone else won!")

# Start network listener thread
threading.Thread(target=listen_for_server, daemon=True).start()    

def check_borad(row, col):
    if solve_board_array[row][col] != board_array[row][col]:
        return False
    return True

def get_highlight_cells(row, col):
    cells = set()
    target_value = board_array[row][col]
    if target_value == 0:
        return cells
    
    # Find all occurrences of the target value
    matches = np.argwhere(board_array == target_value)
    
    for (r, c) in matches:
        # Add row
        for j in range(9):
            cells.add((r, j))
        # Add column
        for i in range(9):
            cells.add((i, c))
        # Add 3x3 box
        box_row = (r // 3) * 3
        box_col = (c // 3) * 3
        for i in range(box_row, box_row + 3):
            for j in range(box_col, box_col + 3):
                cells.add((i, j))

    return cells

while running:
    # 1. Draw Grid
    screen.fill((255, 255, 255))  # White background
    cell_size = 60

    # Draw Red Flash for Wrong Answers
    current_time = pygame.time.get_ticks()
    flash_surface = pygame.Surface((cell_size, cell_size))
    flash_surface.fill((255, 0, 0)) # Red

    # Filter active flashes
    flash_cells = [f for f in flash_cells if current_time - f[2] < 300] # 300ms flash

    for (r, c, _) in flash_cells:
        rect = pygame.Rect(c * cell_size, r * cell_size, cell_size, cell_size)
        screen.blit(flash_surface, rect)

    # Highlight selected row/column/box when a filled cell is selected
    highlight_surface = pygame.Surface((cell_size, cell_size), pygame.SRCALPHA)
    highlight_surface.fill((173, 216, 230, 120))
    for (r, c) in highlight_cells:
        highlight_rect = pygame.Rect(c * cell_size, r * cell_size, cell_size, cell_size)
        screen.blit(highlight_surface, highlight_rect)

    for i in range(10):
        thickness = 3 if i % 3 == 0 else 1
        pygame.draw.line(screen, (0, 0, 0), (i * cell_size, 0), (i * cell_size, 540), thickness)
        pygame.draw.line(screen, (0, 0, 0), (0, i * cell_size), (540, i * cell_size), thickness)
    
    # Draw bottom separation line
    pygame.draw.line(screen, (0, 0, 0), (0, 540), (540, 540), 3)

    # Draw numbers on the board
    for i in range(9):
        for j in range(9):
            if board_array[i][j] != 0:
                text = font.render(str(board_array[i][j]), True, (0, 0, 0))
                screen.blit(text, (j * cell_size + cell_size // 3, i * cell_size + cell_size // 3))

    # Draw selection outline
    if selected_cell is not None:
        sel_row, sel_col = selected_cell
        sel_rect = pygame.Rect(sel_col * cell_size, sel_row * cell_size, cell_size, cell_size)
        pygame.draw.rect(screen, (0, 120, 215), sel_rect, 3)

    # Handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_pos = pygame.mouse.get_pos()
            if mouse_pos[0] < 540 and mouse_pos[1] < 540:
                col = mouse_pos[0] // cell_size
                row = mouse_pos[1] // cell_size
                selected_cell = (row, col)
                if board_array[row][col] != 0:
                    highlight_cells = get_highlight_cells(row, col)
                else:
                    highlight_cells = set()

        elif event.type == pygame.KEYDOWN:
            if selected_cell is not None:
                row, col = selected_cell
                if not fixed_cells[row][col]:
                    if pygame.K_1 <= event.key <= pygame.K_9:
                        num = event.key - pygame.K_0
                        if solve_board_array[row][col] != num:
                            wrong_answer+=1
                            wrong_cells.add((row, col))
                            flash_cells.append((row, col, pygame.time.get_ticks()))
                             # Clear the cell visually but keep it red
                            board_array[row][col] = 0
                        else:
                            fixed_cells[row][col] = 1
                            if (row, col) in wrong_cells:
                                wrong_cells.remove((row, col))
                            board_array[row][col] = num

                    elif event.key in (pygame.K_0, pygame.K_BACKSPACE, pygame.K_DELETE):
                        board_array[row][col] = 0
                        if (row, col) in wrong_cells:
                            wrong_cells.remove((row, col))

                    if board_array[row][col] != 0:
                        highlight_cells = get_highlight_cells(row, col)
                    else:
                        highlight_cells = set()

    # Draw UI (Timer and Mistakes)
    elapsed_seconds = (pygame.time.get_ticks() - start_time) // 1000
    minutes = elapsed_seconds // 60
    seconds = elapsed_seconds % 60
    time_str = f"Time: {minutes:02}:{seconds:02}"
    mistakes_str = f"Mistakes: {wrong_answer}/{MAX_WRONG_ANSWERS}"
    
    time_surface = ui_font.render(time_str, True, (0, 0, 0))
    mistakes_surface = ui_font.render(mistakes_str, True, (255, 0, 0) if wrong_answer > 0 else (0, 0, 0))

    screen.blit(time_surface, (20, 555))
    screen.blit(mistakes_surface, (300, 555))

    # Check if board is full and correct
        # If yes: client.send("WIN".encode())
    if np.count_nonzero(board_array) == 81:
        client.send("WIN".encode())
        print("You won!")
        game_over = True
        running = False

    if wrong_answer >= MAX_WRONG_ANSWERS:
        client.send("LOSE".encode())
        print("You lost!")
        running = False

    pygame.display.update()

