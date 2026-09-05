
class ts:
    
    
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


    
        






    

    