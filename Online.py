import socket
from tools import ts
import random
import re

PORT = 5555


def create_room():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    server.bind(("0.0.0.0", PORT))
    server.listen(1)

    ip = socket.gethostbyname(socket.gethostname())

    print("\nRoom created!")
    print(f"Room code: {ip}")
    print("Waiting for another player...\n")

    conn, addr = server.accept()

    print("Player connected!")

    server.close()

    return conn


def join_room(room_code):
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    client.connect((room_code, PORT))

    print("\nConnected to room!")

    return client


def send_data(sock, data):
    sock.sendall(data.encode("utf-8"))


def receive_data(sock):
    return sock.recv(1024).decode("utf-8")

while True:
    player_1=str(random.randint(1000,9999))
    check_1=ts.remove_same_digits(player_1)
    player_2=str(random.randint(1000,9999)) 
    check_2=ts.remove_same_digits(player_2)
    if check_1==False and check_2==False:
        break


def get_guess():
    while True:
        player_guess = input("Enter your guess number : ")
        if re.fullmatch(r'\d{4}',player_guess) and not ts.remove_same_digits(player_guess):
            return str(player_guess)
        else:
            print("Please try agine ! ")



choice = input(
    "Do you want to create a room or join a room? "
).lower()


if choice == "create room":

    connection = create_room()

    send_data(connection, "Hello from Player 1!")
 
    message = receive_data(connection)

    print("Player 2 says:", message)


    while True:
       

        if message== "YOU LOSE !":
            print(message)
            break

        print("player 1 your round:")
        player_1_guess =get_guess()
        stars,points=ts.game_culc(player_1_guess,player_1)
        if stars==4:
            print("player 1 win the game !")
            send_data(connection, "YOU LOSE !")
            break
        print(f"\nplayer 1 your guess is {player_1_guess} and the result is {stars} stars and {points} points\n")
        send_data(connection, "your round")
        message = receive_data(connection)
    if message !="YOU LOSE !":
        print(f"{player_1_guess} IS TRUE, you win")
    input()
    
        


elif choice == "join":

    room_code = input("Enter room code: ")

    connection = join_room(room_code)

    message = receive_data(connection)

    print("Player 1 says:", message)


    send_data(connection, "Hello from Player 2!")
    message = receive_data(connection)

    while message=="your round":
        message=""
        print("player 2 your round:")
        player_2_guess =get_guess()
        stars,points=ts.game_culc(player_2_guess,player_2)
        if stars==4:
            print("player 2 win the game !")
            send_data(connection, "YOU LOSE !")            
            break
        print(f"\nplayer 2 your guess is {player_2_guess} and the result is {stars} stars and {points} points\n")
        send_data(connection, "your round")  
        message = receive_data(connection) 

    if message == "YOU LOSE !":
        print(message)
    else:
         print(f"{player_2_guess} IS TRUE, you win")    

    input()


else:

    print("Invalid choice.")
