import random

import engine

def run():
    engine.init()
    while engine.can_move():
        engine.move(random.randrange(4))
    return engine.score

if __name__ == "__main__":
    # Dump the data (for my results)
    print(run for _ in range(1000)