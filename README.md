## Team Member Names
- Abdulhamid Hamdy Abdulhamid Gharib
- Mahmoud Ahmed Mahmoud Elsayed
- Seba Ehab Ibrahim Abdelrazek Amer 
- Eman Ayman Mostafa Abdelkader

## GUESSING NUMBER GAME (4-Digit Secret Code)
A comprehensive Python-based implementation of the classic 4-digit number guessing game (Bulls and Cows / Mastermind concept). The game features multiple game modes including Single Player, Local 2-Player, Networked Multiplayer using Sockets, and an Algorithmic Computer bot.

## Game Concept & Rules
The game revolves around generating a secret 4-digit number where all digits must be completely unique (no repeating numbers like 1123 or 4444).

Players take turns guessing the secret 4-digit number. After every guess, the game calculates two evaluation metrics:

Stars (Exact Matches):

Granted when a digit in the guess matches both the value and the exact position/index of a digit in the secret number.

Example: Secret = 1234, Guess = 1567 -> 1 Star (for digit 1).

Points (Partial Matches):

Granted when a digit in the guess exists inside the secret number, but is located in a different position/index.

Example: Secret = 1234, Guess = 5612 -> 2 Points (for digits 1 and 2).

Winning Condition:

The first player/entity to achieve 4 Stars (100% positional match) wins the round immediately!

# Project Architecture

```text
.
├── tools.py               # Core helper module containing validation and scoring algorithms (ts class)
├── One_Player.py          # Single player mode implementation
├── Two_Players.py         # Local two-player mode implementation (Pass-and-Play)
├── Online.py              # Networked multiplayer implementation (TCP Sockets over local network)
├── Player_VS_Computer.py  # Smart Computer Bot mode using dynamic array reduction
└── README.md              # Full project documentation


## Detailed Methods & Functions Documentation
1. Helper Methods (tools.py)
The tools.py module exposes the ts class containing static utility methods used by all 4 game modes:

### remove_same_digits(num: str) -> bool
Purpose: Evaluates whether a given string/number contains duplicate digits.

Algorithm/Logic:

Compares index 0 with indices 1, 2, 3.

Compares index 1 with indices 2, 3.

Compares index 2 with index 3.

Returns:

True: If at least one digit is repeated (e.g., "1223" or "5555").

False: If all 4 digits are completely unique (e.g., "1234").

### game_culc(guess_1: str, guess_2: str) -> tuple[int, int]
Purpose: Compares two 4-digit strings (guess_1 vs guess_2) and calculates the total Stars and Points.

Algorithm/Logic:

Stars Loop: Checks positional equality (guess_1[i] == guess_2[i]) across indices 0, 1, 2, 3. Increments stars by 1 for each true match.

Points Loop: Checks if guess_1[i] exists anywhere in guess_2 excluding index i. Increments points by 1 for each cross-position match.

Returns:

A tuple containing (stars, points) as integers.

2. Input Validation Function (get_guess)
Present in mood-1.py, mood-2.py, mood-3.py, and mood-4.py.

### get_guess() -> str
Purpose: Handles user terminal input safely to prevent invalid inputs or crashes.

Algorithm/Logic:

Enters an infinite while True loop waiting for input.

Uses Regular Expressions (re.fullmatch(r'\d{4}', player_guess)) to ensure the user entered exactly 4 numeric digits.

Calls ts.remove_same_digits(player_guess) to guarantee no digits are repeated.

If both validations pass, returns the valid 4-digit string.

If validation fails, prints "Please try agine ! " and prompts the player again.

3. Network Communication Methods (mood-3.py)
Handles Socket-based server/client creation over local TCP connections:

### create_room() -> socket.socket
Purpose: Initializes a TCP socket server on port 5555.

Algorithm/Logic:

Binds the socket to ("0.0.0.0", 5555).

Listens for 1 incoming client connection.

Fetches the host IP address (socket.gethostbyname(...)) and displays it as the Room Code.

Accepts the connection (server.accept()) and returns the connection object conn.

### join_room(room_code: str) -> socket.socket
Purpose: Connects a client to an existing server room.

Algorithm/Logic:

Creates a TCP client socket.

Connects to (room_code, 5555).

Returns the connected client socket object.

### send_data(sock: socket.socket, data: str)
Purpose: Encodes a string to utf-8 and sends it through the TCP socket (sock.sendall()).

receive_data(sock: socket.socket) -> str
Purpose: Listens to incoming byte stream (buffer size 1024) from the TCP socket and decodes it back to a utf-8 string.

##  Game Modes Explained
### Mode 1: Single Player (One_Player.py)
Flow:

Generates a random 4-digit secret number for the player using random.randint(1000, 9999) ensuring no duplicate digits via ts.remove_same_digits().

Prompts the player to enter a guess repeatedly.

Displays feedback (X stars and Y points) after each turn until 4 stars are reached.

### Mode 2: Local 2-Player (Two_Players.py)
Flow:

Generates two separate secret numbers (player_1 and player_2).

Runs a turn-based loop alternating between Player 1 and Player 2 on the same device.

Evaluates guesses independently and terminates as soon as Player 1 or Player 2 hits 4 stars.

### Mode 3: Networked Multiplayer (Online.py)
Flow:

Asks user to either "create room" (Host) or "join" (Client).

Establishes a TCP Socket bridge between two devices over local network/WiFi.

Sends messages back and forth to control turn sequences ("your round", "YOU LOSE !").

### Mode 4: Player vs Smart Computer Bot (Player_VS_Computer.py)
Flow & Bot Algorithm:

Possible Universe: The computer generates a list possible_numbers containing all valid non-repeating 4-digit numbers between 1000 and 9999 (4536 possible combinations).

Player Turn: Player guesses the computer's secret number.

Computer AI Turn:

The computer picks a guess randomly from its possible_numbers list.

Evaluates its guess against the player's secret number to get (stars, points).

Filtering Logic: The AI iterates through possible_numbers and removes any number that wouldn't yield the exact same (stars, points) feedback if it were the secret number.

The candidate list shrinks rapidly each round, allowing the Computer to guess the player's number in very few turns!

## How to Run the Game
Open your terminal or command prompt inside the project folder and execute any mode:
# Run Single Player Mode
python One_Player.py

# Run Local 2-Player Mode
python Two_Players.py

# Run Networked Multiplayer Mode
python Online.py

# Run Player vs Computer Bot Mode
python Player_VS_Computer.py


## Technical Requirements
Python Version: Python 3.x or higher.

Dependencies: None! Built purely using Standard Python Libraries:

random (Random number generation)

re (Regular expression validation)

socket (Network socket communication)
