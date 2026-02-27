# LAN Multiplayer Sudoku (Python + Pygame)

A simple 2-player Sudoku game for two laptops on the same hotspot/LAN.

## Features

- Host/client LAN play using Python sockets
- Real-time win notification (`You won` / `Peer won`)
- Sudoku generation using [sudoku generator](https://github.com/BurnYourPc/Sudoku/tree/master)
- Keyboard + mouse controls in a `pygame` window

## Requirements

Install dependencies:

```bash
pip install -r requirements.txt
```

## Run

From project root:

### 1) Start host (Laptop A)

```bash
python server.py
```

### 2) Start client (Laptop B)

Use Laptop A's LAN IP (for example `127.0.0.1`):

```bash
python client.py
```

## Controls

- Click a cell to select
- Number keys `1-9` to fill

## Notes

- This is an MVP protocol: host sends puzzle  to client.
