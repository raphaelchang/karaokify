import time

def play(lyrics):
    start = time.time()
    for l in lyrics:
        while time.time() - start < l[1]:
            time.sleep(0.01)
        print(l[0])
