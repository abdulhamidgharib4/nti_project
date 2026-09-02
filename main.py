import random

def remove_same_digits(num):
    if num[0] == num[1] or num[0] == num[2] or num[0] == num[3]:
        return True
    elif num[1] == num[2] or num[1] == num[3]:
        return True
    elif num[2] == num[3]:
        return True
    
    return False



while True:
    player_1=str(random.randint(1000,9999))
    check_1=remove_same_digits(player_1)
    player_2=str(random.randint(1000,9999)) 
    check_2=remove_same_digits(player_2)
    if check_1==False and check_2==False:
        break

print("Player 1 number:", player_1)
print("Player 2 number:", player_2)

