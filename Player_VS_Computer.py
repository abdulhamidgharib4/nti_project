import random
import re
from tools import ts


def get_guess():
    while True:
        player_guess = input("Enter your guess number : ")

        if re.fullmatch(r'\d{4}', player_guess) and not ts.remove_same_digits(player_guess):
            return str(player_guess)
        else:
            print("Please try agine ! ")


while True:
    player = str(random.randint(1000, 9999))
    check = ts.remove_same_digits(player)

    if check == False:
        break


while True:
    computer = str(random.randint(1000, 9999))
    check = ts.remove_same_digits(computer)

    if check == False:
        break


# print("================================")
# print("player secret number is : ", player)
# print("computer secret number is : ", computer)
# print("================================")
# print("you can start your round !")

possible_numbers = []

for i in range(1000, 10000):
    number = str(i)

    if not ts.remove_same_digits(number):
        possible_numbers.append(number)


while True:

    print("\nYour round :")

    player_guess = get_guess()

    stars, points = ts.game_culc(
        player_guess,
        player
    )

    print(
        f"\nyour guess is {player_guess} "
        f"and the result is {stars} stars "
        f"and {points} points"
    )

    if stars == 4:
        print("Congratulations, you win the game !")
        break


    print("\nComputer round :")

    computer_guess = random.choice(possible_numbers)

    stars, points = ts.game_culc(
        computer_guess,
        computer
    )

    print(
        f"computer guess is {computer_guess} "
        f"and the result is {stars} stars "
        f"and {points} points"
    )

    if stars == 4:
        print("Computer win the game !")
        break


    new_possible_numbers = []

    for number in possible_numbers:

        test_stars, test_points = ts.game_culc(
            computer_guess,
            number
        )

        if test_stars == stars and test_points == points:
            new_possible_numbers.append(number)

    possible_numbers = new_possible_numbers

    print(
        f"computer possible numbers : "
        f"{len(possible_numbers)}"
    )