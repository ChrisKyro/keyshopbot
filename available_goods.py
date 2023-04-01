def available_Fences():
    counter = 0
    with open('./goods/Ключи Fences.txt') as f:
        for lines in f:
            counter+=1
    return counter

def available_CSGO():
    counter = 0
    with open('./goods/Ключи CSGO.txt') as f:
        for lines in f:
            counter+=1
    return counter
