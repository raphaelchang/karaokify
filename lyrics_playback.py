import time

def play(lyrics):
    start = time.time()
    for l in lyrics:
        while time.time() - start  < l[1]:
            pass
        print(l[0])
