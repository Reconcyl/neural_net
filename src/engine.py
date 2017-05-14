import random, math

# changing this will probably break things;
# it's just for clarity.
BOARD_SIZE = 4

def init(rand_state=None):
    "Initializes the board for a game."
    if rand_state is not None:
        random.setstate(rand_state)
    global board, score
    board = [
        [0, 0, 0, 0],
        [0, 0, 0, 0],
        [0, 0, 0, 0],
        [0, 0, 0, 0],
    ]
    score = 0
    place_random()
    place_random()
    
def place_random():
    "Places a random tile on the board."
    tile = 1 + (random.random() > 0.9)
    while True:
        # this is faster than random.randrange for some reason
        tileX = math.floor(random.random() * BOARD_SIZE)
        tileY = math.floor(random.random() * BOARD_SIZE)
        if not board[tileY][tileX]:
            break
    board[tileY][tileX] = tile
    
def transpose_board():
    "Swaps rows and columns in the board."
    global board
    board = list(map(list, zip(*board)))
def reverse_board():
    "Reverses each row in the board."
    global board
    board = [list(reversed(row)) for row in board]

def merge_row(row):
    """The algorithm for this is quite complicated; in
       the interest of optimization, it has been replaced
       with a bunch of logic."""
    global score
    row = [i for i in row if i]
    row_length = len(row)
    if row_length == 0:
        return [0, 0, 0, 0]
    if row_length == 1:
        return row + [0, 0, 0]
    if row_length == 2:
        if 0 < row[0] == row[1]:
            score_tile(row[0])
            return [row[0] + 1, 0, 0, 0]
        return row + [0, 0]
    if row_length == 3:
        if 0 < row[0] == row[1]:
            score_tile(row[0])
            return [row[0] + 1, row[2], 0, 0]
        elif 0 < row[1] == row[2]:
            score_tile(row[1])
            return [row[0], row[1] + 1, 0, 0]
        return row + [0]
    if row_length == 4:
        row_0, row_1, row_2, row_3 = row
        eq_last = (0 < row_2 == row_3)
        if 0 < row_0 == row_1:
            score_tile(row_0)
            if eq_last:
                score_tile(row_2)
                return [row_0 + 1, row_2 + 1, 0, 0]
            return [row_0 + 1, row_2, row_3, 0]
        if 0 < row_1 == row_2:
            score_tile(row_1)
            return [row_0, row_1 + 1, row_3, 0]
        if eq_last:
            score_tile(row_2)
            return [row_0, row_1, row_2 + 1, 0]
        return row
    
def score_tile(tile):
    "Increases the score by the correct amount, given the number of the merged tile."
    global score
    score += 1 << (tile + 1)
    
def merge_left():
    """Merges each row. This has the same effect as pressing
       the left arrow in the game."""
    for i, row in enumerate(board):
        board[i] = merge_row(row)
        
def merge(direction):
    "Merges the board in a specific direction."
    if direction == 0: # up
        transpose_board()
        reverse_board()
        merge_left()
        reverse_board()
        transpose_board()
    elif direction == 1: # right
        reverse_board()
        merge_left()
        reverse_board()
    elif direction == 2: # down
        transpose_board()
        merge_left()
        transpose_board()
    elif direction == 3: # left
        # for some reason the comparsion board != old_board down in move()
        # doesn't work when direction==3, so I just reverse the board twice
        # to fix that (for some reason that works)
        reverse_board()
        reverse_board()
        merge_left()
    else:
        # Should never happen
        raise ValueError("direction must be integer 0-3")
        
def move(direction):
    "Preforms a move. Merges the board and places a new tile."
    old_board = board
    merge(direction)
    if board != old_board:
        place_random()
        
def can_move():
    """Returns True if any move can be made.
       It is extremely inefficient."""
    global board, score
    board_copy = board
    score_copy = score
    try:
        for i in range(4):
            merge(i)
            if board != board_copy:
                return True
        return False
    finally:
        board = board_copy
        score = score_copy
        
def copy_board():
    "Returns a copy of the board."
    return [row[:] for row in board]

#if __name__ == "__main__":
    