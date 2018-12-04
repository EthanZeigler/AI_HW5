from enum import Enum

GAMMA = 0.98
BONUS_REWARD = 1
ENEMY_REWARD = -.5

class GameMap:
    pass


def is_valid_cell(r:int, c:int, g:[[]]):
    return (0 <= r < len(g)) and (0 <= c < len(g[r]))


class GameCell:
    def __init__(self):
        self.q_up = 0
        self.q_down = 0
        self.q_left = 0
        self.q_right = 0
        self.v = 0

    def update_v(self, r:int, c:int, g:[[]], reward:[[]]):
        if is_valid_cell():
            v = (max(g[r][c], g[r+1][c], g[r-1][c], g[r][c+1], g[r][c-1]) * GAMMA) + reward[r][c]
        else:
            g[r][c] = 0
        pass


class CellType(Enum):
    EMPTY = 0
    PLATFORM = 1
    LADDER = 2
    NEEDLE = 3
    TARGET = 4
    BONUS = 5
    ENEMY = 6

class TType(Enum):
    MOVE = 0
    JUMP = 1
    WALL = 2
    ENEMY = 3

# Stage Information: Each stage is (rows x cols) = (12 x 20) cells
# .	empty
# 2	platform / left half-circle
# 3	platform / right half-circle
# 4	platform / rectangle
# 5	platform / island
# 6	ladder
# 7	needle
# #	target (100 points)
# a	bonus (500 points)
# b	bonus (1000 points)
# c	enemy1 (always appear on the right)