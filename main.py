import random
# 1 - with re module 
import re 


def remove_same_digits(num):
    if num[0] == num[1] or num[0] == num[2] or num[0] == num[3]:
        return True
    elif num[1] == num[2] or num[1] == num[3]:
        return True
    elif num[2] == num[3]:
        return True
    
    return False

def game_culc(guess_1,guess_2):
    stars = 0
    points = 0
    if guess_1[0]==guess_2[0]:
        stars+=1
    if guess_1[1]==guess_2[1]:
        stars+=1
    if guess_1[2]==guess_2[2]:
        stars+=1
    if guess_1[3]==guess_2[3]:
        stars+=1
    if guess_1[0]==guess_2[1] or guess_1[0]==guess_2[2] or guess_1[0]==guess_2[3]:
        points+=1
    if guess_1[1]==guess_2[0] or guess_1[1]==guess_2[2] or guess_1[1]==guess_2[3]:
        points+=1
    if guess_1[2]==guess_2[0] or guess_1[2]==guess_2[1] or guess_1[2]==guess_2[3]:
        points+=1
    if guess_1[3]==guess_2[0] or guess_1[3]==guess_2[1] or guess_1[3]==guess_2[2]:
        points+=1
    return stars,points


def get_guess():
    while True:
        player_guess = input("Enter your guess number : ")
        if re.fullmatch(r'\d{4}',player_guess) and not  remove_same_digits(player_guess):
            return str(player_guess)
        else:
            print("Please try agine ! ")



while True:
    player_1=str(random.randint(1000,9999))
    check_1=remove_same_digits(player_1)
    player_2=str(random.randint(1000,9999)) 
    check_2=remove_same_digits(player_2)
    if check_1==False and check_2==False:
        break

# print("player 1 your number is : ",player_1)
# print("player 2 your number is : ",player_2)

while True:
    print("player 1 your ruond:")
    player_1_guess = get_guess()
    stars,points= game_culc(player_1_guess,player_1)
    if stars==4:
        print("player 1 win the game !")
        break
    print(f"\nplayer 1 your guess is {player_1_guess} and the result is {stars} stars and {points} points\n")
    print("player 2 your ruond:")
    player_2_guess = get_guess()
    stars,points= game_culc(player_2_guess,player_2)
    if stars==4:
        print("player 2 win the game !")
        break
    print(f"\nplayer 2 your guess is {player_2_guess} and the result is {stars} stars and {points} points\n")
    







