from enum import Enum, auto
import copy
from main import Agent

# MDP Values and costs
GAMMA = 0.98
BONUS_LOW_REWARD = .5
BONUS_HIGH_REWARD = .7
BONUS_ENEMY_REWARD = -.1
FRUIT_REWARD = 1
ENEMY_REWARD = -1.5

# Data structures and magic number wrappers

class Direction(Enum):
    UP     = (-1, 0)
    DOWN   = (1, 0)
    LEFT   = (0, -1)
    RIGHT  = (0, 1)

    def __init__(self, row, col):
        self.row = row
        self.col = col




class TType(Enum):
    MOVE     = auto()
    JUMP     = auto()
    INVALID  = auto()
    DANGER   = auto()

    def valid_q(self):
        return self == TType.MOVE or self == TType.JUMP

    def __str__(self):
        return self.name


class PlayerState(Enum):
    FACE_RIGHT      = auto()
    FACE_LEFT       = auto()
    FACE_VERTICAL   = auto()


class CellType(Enum):
    DNE                     = -1
    SPAWN_CELL              = 0
    AIR                     = 1
    PLATFORM_LEFT_DROPOFF   = 2
    PLATFORM_RIGHT_DROPOFF  = 3
    PLATFORM_FULL           = 4
    PLATFORM_ISLAND         = 5
    LADDER                  = 6
    NEEDLE                  = 7
    FRUIT                   = 8
    BONUS_LOW               = 9
    BONUS_HIGH              = 10
    BONUS_DANGER            = 11


    def __str__(self):
        return self.name

    def is_safe(self):
        return self == self.PLATFORM_FULL or\
                self == self.PLATFORM_ISLAND or\
                self == self.PLATFORM_LEFT_DROPOFF or\
                self == self.PLATFORM_RIGHT_DROPOFF or\
                self == self.LADDER or\
                self == self.FRUIT or\
                self == self.BONUS_LOW or\
                self == self.BONUS_HIGH or\
                self == self.BONUS_DANGER

    def is_safe_ground(self):
        return self == self.PLATFORM_FULL or\
                self == self.PLATFORM_ISLAND or\
                self == self.PLATFORM_LEFT_DROPOFF or\
                self == self.PLATFORM_RIGHT_DROPOFF or\
                self == self.LADDER

    def valid_q_transition(self, d:Direction):

        return

naive_transitions = { 0 : TType.INVALID, # Spawn point (right wall)
                 1 : TType.MOVE,         # Air
                 2 : TType.INVALID,      # Platform / left half-circle
                 3 : TType.INVALID,      # Platform / right half-circle
                 4 : TType.INVALID,      # Platform / rectangle
                 5 : TType.INVALID,      # Platform / island
                 6 : TType.MOVE,         # Ladder
                 7 : TType.JUMP,         # Needle
                 8 : TType.MOVE,         # Fruit
                 9 : TType.MOVE,         # Bonus
                 10: TType.MOVE,         # Bonus
                 11: TType.MOVE          # Bonus (Danger)
}

reward_values = { CellType.SPAWN_CELL : 0,
                  CellType.NEEDLE : 0,
                  CellType.AIR : 0,
                  CellType.DNE : 0,
                  CellType.PLATFORM_FULL : 0,
                  CellType.PLATFORM_ISLAND : 0,
                  CellType.PLATFORM_LEFT_DROPOFF : 0,
                  CellType.PLATFORM_RIGHT_DROPOFF : 0,
                  CellType.LADDER : 0,
                  CellType.FRUIT : 1,
                  CellType.BONUS_LOW : 0.5,
                  CellType.BONUS_HIGH : 0.7,
                  CellType.BONUS_DANGER : -0.1
}

q_transition_validity = {
                CellType.SPAWN_CELL : {
                    Direction.UP: False,
                    Direction.DOWN: False,
                    Direction.LEFT: False,
                    Direction.RIGHT: False
                },
                CellType.NEEDLE : {
                    Direction.UP: False,
                    Direction.DOWN: False,
                    Direction.LEFT: True,
                    Direction.RIGHT: True
                },
                CellType.AIR : {
                    Direction.UP: False,
                    Direction.DOWN: False,
                    Direction.LEFT: False,
                    Direction.RIGHT: False
                },
                CellType.DNE : 0,
                CellType.PLATFORM_FULL : 0,
                CellType.PLATFORM_ISLAND : 0,
                CellType.PLATFORM_LEFT_DROPOFF : 0,
                CellType.PLATFORM_RIGHT_DROPOFF : 0,
                CellType.LADDER : 0,
                CellType.FRUIT : 1,
                CellType.BONUS_LOW : 0.5,
                CellType.BONUS_HIGH : 0.7,
                CellType.BONUS_DANGER : -0.1
}

class GameCell(object):


    @staticmethod
    def get_cell_type(r:int, c:int, g:[[]]) -> CellType:
        if is_valid_cell(r, c, g):
            return CellType(g[r][c])
        else:
            return CellType.DNE

    def get_transition_type(self, r:int, c:int, g:[], t:Direction) -> TType:
        # Check if valid cell, otherwise invalid
        if is_valid_cell(r + t.value[0], c + t.value[1], g):
            # Get naive transition
            naive_transition = naive_transitions[g[r + t.value[0]][c + t.value[1]]]
            # if invalid, no further checking
            if naive_transition == TType.INVALID: return naive_transition
            # refine for platform check with additional torture and messy code on the side
            ground_cell = GameCell.get_cell_type(r + t.value[0] + Direction.DOWN.value[0],
                                                 c + t.value[1] + Direction.DOWN.value[1], g)\
                                        if naive_transition is TType.MOVE else\
                                            GameCell.get_cell_type(r + Direction.DOWN.value[0], c + (2 * t.value[1]), g)
            # check if valid platform
            # yeah, it's awful
            # if up or down, don't return danger, but invalid
            if CellType.is_safe_ground(ground_cell):
                return naive_transition
            elif t == Direction.UP or t == Direction.DOWN:
                return TType.INVALID
            elif CellType.is_safe_ground(GameCell.get_cell_type(r + Direction.DOWN.value[0], c + (2 * t.value[1]), g)):
                return TType.JUMP
            else:
                return TType.DANGER
        else:
            return TType.INVALID

    def __init__(self, r:int, c:int, g:[[]]):
        self.cell_type = self.get_cell_type(r, c, g)
        # populated by game map
        self.q_up = 0
        self.q_down = 0
        self.q_left = 0
        self.q_right = 0
        self.v = 0
        # transition functions between cells
        self.t_up = self.get_transition_type(r, c, g, Direction.UP)
        self.t_down = self.get_transition_type(r, c, g, Direction.DOWN)
        self.t_left = self.get_transition_type(r, c, g, Direction.LEFT)
        self.t_right = self.get_transition_type(r, c, g, Direction.RIGHT)



    def update_v(self, r:int, c:int, g:[[]]):
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

        # This is making me hate myself.
        # 0 or move or jump based on designated transition function
        self.q_up = 0 if not self.t_up.valid_q() else\
            (g[r + Direction.UP[0]][c + Direction.UP[1]]).v if self.t_up == TType.MOVE else\
                (g[r + (2 * Direction.UP[0])][c + (2 * Direction.UP[1])]).v

        self.q_down = 0 if not self.t_down.valid_q() else \
            (g[r + Direction.DOWN[0]][c + Direction.DOWN[1]]).v if self.t_down == TType.MOVE else \
                (g[r + (2 * Direction.DOWN[0])][c + (2 * Direction.DOWN[1])]).v

        self.q_left = 0 if not self.t_left.valid_q() else \
            (g[r + Direction.LEFT[0]][c + Direction.LEFT[1]]).v if self.t_left == TType.MOVE else \
                (g[r + (2 * Direction.LEFT[0])][c + (2 * Direction.LEFT[1])]).v

        self.q_right = 0 if not self.t_right.valid_q() else \
            (g[r + Direction.RIGHT[0]][c + Direction.RIGHT[1]]).v if self.t_right == TType.MOVE else \
                (g[r + (2 * Direction.RIGHT[0])][c + (2 * Direction.RIGHT[1])]).v



    def __str__(self) -> str:
        return self.t_down.__str__().center(15, " ")


class GameMap:
    state_colors = {CellType.BONUS_DANGER: 'xkcd:pale yellow',
                    CellType.BONUS_HIGH: 'xkcd:kelly green',
                    CellType.BONUS_LOW: 'xkcd:kelly green',
                    CellType.FRUIT: 'xkcd:seafoam',
                    CellType.LADDER: 'xkcd:reddish grey',
                    CellType.PLATFORM_RIGHT_DROPOFF: 'xkcd:baby pink',
                    CellType.PLATFORM_LEFT_DROPOFF: 'xkcd:baby pink',
                    CellType.PLATFORM_ISLAND: 'xkcd:baby pink',
                    CellType.PLATFORM_FULL: 'xkcd:baby pink',
                    CellType.DNE: "w",
                    CellType.AIR: "w",
                    CellType.NEEDLE: "xkcd:orangish",
                    CellType.SPAWN_CELL: "xkcd:dark sand"}

    def __init__(self, agent:Agent):
        self.raw_grid = copy.deepcopy(agent.move_grid)
        self.state_grid = []
        for r in range(len(self.raw_grid)):
            self.state_grid.append([])
            for c in range(len(self.raw_grid[r])):
                self.state_grid[r].append(GameCell(r, c, self.raw_grid))




def is_valid_cell(r:int, c:int, g:[[]]):
    """Check if inside the grid"""
    return (0 <= r < len(g)) and (0 <= c < len(g[r]))






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