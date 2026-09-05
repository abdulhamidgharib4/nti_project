import random
# 1 - with re module 
import re 

from tools import ts 



def get_guess():
    while True:
        player_guess = input("Enter your guess number : ")
        if re.fullmatch(r'\d{4}',player_guess) and not ts.remove_same_digits(player_guess):
            return str(player_guess)
        else:
            print("Please try agine ! ")




