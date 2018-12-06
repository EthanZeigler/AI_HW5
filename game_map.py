from enum import Enum, auto
import copy
from main import Agent

GAMMA = 0.98
BONUS_REWARD = 1
ENEMY_REWARD = -.5

class PlayerState(Enum):
    FACE_RIGHT      = auto()
    FACE_LEFT       = auto()
    FACE_VERTICAL   = auto()


class CellType(Enum):
    SPAWN_CELL              = auto()
    AIR                     = auto()
    PLATFORM_LEFT_DROPOFF   = auto()
    PLATFORM_RIGHT_DROPOFF  = auto()
    PLATFORM_FULL           = auto()
    PLATFORM_ISLAND         = auto()
    LADDER                  = auto()
    NEEDLE                  = auto()
    BONUS                   = auto()


class TType(Enum):
    MOVE     = 0
    JUMP     = 1
    INVALID  = 2
    DANGER   = 3

# img_world = ['01.png',  # background
#              '02.png', '03.png', '04.png', '05.png',  # left / right / rectangle / island platform
#              '06.png',  # ladder
#              '07.png',  # needle
#              '08.png']  # bonus

cell_type_map = {  '0'

}

naive_transitions = { '0' : TType.INVALID, # Spawn point (right wall)
                 '1' : TType.MOVE,         # Air
                 '2' : TType.INVALID,      # Platform / left half-circle
                 '3' : TType.INVALID,      # Platform / right half-circle
                 '4' : TType.INVALID,      # Platform / rectangle
                 '5' : TType.INVALID,      # Platform / island
                 '6' : TType.MOVE,         # Ladder
                 '7' : TType.JUMP,         # Needle
                 '8' : TType.MOVE,         # Fruit
                 '9' : TType.MOVE,         # Bonus
                 '10': TType.MOVE,         # Bonus
                 '11': TType.MOVE          # Bonus (Danger)
}



class GameMap:
    def __init__(self, agent:Agent):
        self.grid = copy.deepcopy(agent.move_grid)

def is_valid_cell(r:int, c:int, g:[[]]):
    return (0 <= r < len(g)) and (0 <= c < len(g[r]))

class GameCell:
    def __init__(self, r:int, c:int, g:[[]]):
        self.q_up = 0
        self.q_down = 0
        self.q_left = 0
        self.q_right = 0
        self.v = 0
        self.t_up = CellType.EMPTY
        self.t_down = CellType.EMPTY
        self.t_left = CellType.EMPTY
        self.t_right = CellType.EMPTY

    def get_transition_type(self, r:int, c:int, g:[[]]) -> TType:
        if is_valid_cell(r, c, g):
            if g[r][c] == '2' or g[r][c] == '3' or g[r][c] == '4' or g[r][c] == '5':
                pass
        else:
            return TType.INVALID

    def update_v(self, r:int, c:int, g:[[]], reward:[[]]):
        # Value Iteration Algorithm:
        # Step 1: Initialize V as some matrix (can be all zeroes; can be based on some intelligent estimate)
        #
        #   Loop until your V is desirably accurate:
        #
        #       Loop over s:
        #
        #           Loop over a:
        #
        #           Step 2: update Q recursively {Q(s,a) <- R(s,a) + gamma * sum_over_all_states(P(s,a,s') * V(s')}
        #
        #           end loop
        #
        #           Step 3: update V(s) <- max_over_all_actions(Q(s,a))
        #
        #           end loop
        #
        #   end loop
        #
        # return V

        if is_valid_cell():
            v = (max(g[r][c], g[r+1][c], g[r-1][c], g[r][c+1], g[r][c-1]) * GAMMA) + reward[r][c]
        else:
            g[r][c] = 0
        pass




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