"""
server.py will be responsible for creating sudoko puzzle and sending it to the clients.

at the end of the game (after submiting the solution) the server will check the solution and send the result to the clients.

"""
import json
import socket
import threading
import sys
import os

# Add Sudoku directory to sys.path so 'src' module can be found by internal imports
sys.path.append(os.path.join(os.getcwd(), 'Sudoku'))

from Sudoku.src.generators import Generators as Gen

# Setup
SERVER_IP = '0.0.0.0' # Listens on all available interfaces
PORT = 5555
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((SERVER_IP, PORT))
server.listen(2)

clients = []
# Generate a board (string representation)
board_array = Gen.GenerateProb(22, 32, 0)  # Non-symmetrical, 22-32 known cells
board_str = json.dumps(board_array.tolist())

def handle_client(conn, addr):
    # Send the board to the new player immediately
    conn.send(board_str.encode())
    
    while True:
        try:
            msg = conn.recv(1024).decode()
            if not msg:
                break
            if msg == "WIN":
                # Only broadcast if game isn't already over (simple check)
                print(f"Player {addr} won!")
                broadcast("GAME_OVER_WINNER_FOUND")
            elif msg == "LOSE":
                print(f"Player {addr} lost!")
        except:
            break
    
    if conn in clients:
        clients.remove(conn)
    conn.close()

def broadcast(msg):
    for client in clients:
        client.send(msg.encode())

print("Server Started. Waiting for connections...")
while True:
    conn, addr = server.accept()
    clients.append(conn)
    # Start a thread for this player
    thread = threading.Thread(target=handle_client, args=(conn, addr))
    thread.start()
