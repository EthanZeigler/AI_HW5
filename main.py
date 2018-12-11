import arcade
import game_core
import threading
import time
import math
#import os
#import pygame
import game_map as ai
from matplotlib import pyplot as plt
from numpy import interp
import sys


class Agent(threading.Thread):

    def __init__(self, threadID, name, counter, show_grid_info=False):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.counter = counter
        self.show_grid_info = show_grid_info

        self.game = []
        self.move_grid = []
        self.kill_grid = []
        self.isGameClear = False
        self.isGameOver = False
        self.current_stage = 0
        self.time_limit = 0
        self.total_score = 0
        self.total_time = 0
        self.total_life = 0
        self.tanuki_r = 0
        self.tanuki_c = 0
        #Define our own tracker of the last move the tanuki made
        self.tanuki_last = 0




    #############################################################
    #      YOUR SUPER COOL ARTIFICIAL INTELLIGENCE HERE!!!      #
    #############################################################
    def ai_function(self):
        # To send a key stroke to the game, use self.game.on_key_press() method
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
        game_map = ai.GameMap(self)


        # for line in game_map.state_grid:
        #     print('[' + ' '.join('{}'.format(k[1]) for k in enumerate(line)) + ']')
        #This performs the q iteration to get the v values after each move
        game_map.q_iteration(30)

        #Prints the complete v grid
        for r in range(12):
            for c in range(20):
                print(game_map.state_grid[r][c].v, end=" ")
            print()
        print()
        print()
        # fig = plt.figure(num=None, figsize=(30, 10), dpi=200, facecolor='w', edgecolor='k')
        # ax = fig.add_subplot(111)
        # ax.xaxis.set_visible(True)
        # ax.yaxis.set_visible(True)
        # # I deserve to be ridiculed for this...
        # the_table = ax.table(cellText=game_map.state_grid,
        #                      # cellColours=[[game_map.state_colors[(game_map.state_grid[r][c]).cell_type]
        #                                    # for c in range(len(game_map.state_grid[r]))]
        #                                    # for r in range(len(game_map.state_grid))],
        #                      cellColours=[[(interp(game_map.state_grid[r][c].v,[-1, 1],[1, 0]), interp(game_map.state_grid[r][c].v,[-1, 1],[0, 1]), 0)
        #                                 for c in range(len(game_map.state_grid[r]))]
        #                                 for r in range(len(game_map.state_grid))],
        #                      loc='center')
        # plt.savefig("v.png")

        #Temp v values for comparison
        vUp = -sys.maxsize
        vDown = -sys.maxsize
        vLeft = -sys.maxsize
        vRight = -sys.maxsize

        #Temp values saying whether each movement direction is possible
        rValid = False
        lValid = False
        dValid = False
        uValid = False

        #Temp values for checking whether to jump
        lJump = False
        rJump = False


        #Check whether each move is possible in current possition
        if self.tanuki_c > 0:
            isValid = str(game_map.state_grid[self.tanuki_r][self.tanuki_c - 1])
            if "MOVE" in isValid:
                lValid = True
            #Deeper check to see if spot is jumpable (needle or pitfall)
            isNeedle = str(game_map.state_grid[self.tanuki_r + 1][self.tanuki_c - 1].cell_type)
            if "NEEDLE" in isNeedle:
                lValid = True
                lJump = True
            if self.tanuki_c > 1:
                isDrop = str(game_map.state_grid[self.tanuki_r + 2][self.tanuki_c - 1].cell_type)
                isPlat = str(game_map.state_grid[self.tanuki_r + 2][self.tanuki_c - 2].cell_type)
                if "AIR" in isDrop:
                    if "PLATFORM" in isPlat:
                        lValid = True;
                        lJump = True

        if self.tanuki_c < 19:
            isValid = str(game_map.state_grid[self.tanuki_r][self.tanuki_c + 1])
            if "MOVE" in isValid:
                rValid = True
            # Deeper check to see if spot is jumpable (needle or pitfall)
            isNeedle = str(game_map.state_grid[self.tanuki_r + 1][self.tanuki_c + 1].cell_type)
            if "NEEDLE" in isNeedle:
                rValid = True
                rJump = True

            if self.tanuki_c < 18:
                isDrop = str(game_map.state_grid[self.tanuki_r + 2][self.tanuki_c + 1].cell_type)
                isPlat = str(game_map.state_grid[self.tanuki_r + 2][self.tanuki_c + 2].cell_type)
                if "AIR" in isDrop:
                    if "PLATFORM" in isPlat:
                        rValid = True
                        rJump = True


        if self.tanuki_r > 0:
            isValid = str(game_map.state_grid[self.tanuki_r - 1][self.tanuki_c])
            if "MOVE" in isValid:
                uValid = True

        if self.tanuki_r < 19:
            isValid = str(game_map.state_grid[self.tanuki_r + 1][self.tanuki_c])
            if "MOVE" in isValid:
                dValid = True


        #If the move is valid, then update v value for the move, otherwise v value will not be considered
        if rValid & (self.tanuki_last != 1):
            if rJump:
                vRight = game_map.state_grid[self.tanuki_r][self.tanuki_c + 2].v
            else:
                vRight = game_map.state_grid[self.tanuki_r][self.tanuki_c + 1].v
        if lValid & (self.tanuki_last != 2):
            if lJump:
                vLeft = game_map.state_grid[self.tanuki_r][self.tanuki_c - 2].v
            else:
                vLeft = game_map.state_grid[self.tanuki_r][self.tanuki_c - 1].v
        if uValid & (self.tanuki_last != 4):
            vUp = game_map.state_grid[self.tanuki_r - 1][self.tanuki_c].v
        if dValid & (self.tanuki_last != 3):
            vDown = game_map.state_grid[self.tanuki_r + 1][self.tanuki_c].v

        print(vLeft)
        print(vRight)
        print(vUp)
        print(vDown)

        #This will perform the chosen action for the given state and mdp analysis
        if (vLeft == max(vLeft, vRight, vDown, vUp)):
            if (not self.game.tanuki.isGoingLeft) or self.game.tanuki.isGoingUpDown:
                self.game.on_key_press(arcade.key.LEFT, 0)
            if lJump:
                self.game.on_key_press(arcade.key.SPACE, 0)
            else:
                self.game.on_key_press(arcade.key.LEFT, 0)
            self.tanuki_last = 1


        if (vRight == max(vLeft, vRight, vDown, vUp)):
            if self.game.tanuki.isGoingLeft or self.game.tanuki.isGoingUpDown:
                self.game.on_key_press(arcade.key.RIGHT, 0)
            if rJump:
                self.game.on_key_press(arcade.key.SPACE, 0)
            else:
                self.game.on_key_press(arcade.key.RIGHT, 0)
            self.tanuki_last = 2


        if (vUp == max(vLeft, vRight, vDown, vUp)):
            if not self.game.tanuki.isGoingUpDown:
                self.game.on_key_press(arcade.key.UP, 0)
            self.game.on_key_press(arcade.key.UP, 0)
            self.tanuki_last = 3


        if (vDown == max(vLeft, vRight, vDown, vUp)):
            if not self.game.tanuki.isGoingUpDown:
                self.game.on_key_press(arcade.key.DOWN, 0)
            self.game.on_key_press(arcade.key.DOWN, 0)
            self.tanuki_last = 4






    def run(self):
        print("Starting " + self.name)

        # os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % (50+320, 50)
        # pygame.init()

        # Prepare grid information display (can be turned off if performance issue exists)
        time.sleep(1)  # wait briefly so that main game can get ready

        # roughly every 50 milliseconds, retrieve game state (average human response time for visual stimuli = 25 ms)
        go = True
        while go and (self.game is not []):
            # Dispatch events from pygame window event queue
            if self.show_grid_info:
                pass
                # for event in pygame.event.get():
                #     if event.type == pygame.QUIT:
                #         go = False
                #         break

            # RETRIEVE CURRENT GAME STATE
            self.move_grid, self.kill_grid, \
                self.isGameClear, self.isGameOver, self.current_stage, self.time_limit, \
                self.total_score, self.total_time, self.total_life, self.tanuki_r, self.tanuki_c \
                = self.game.get_game_state()

            #Row coordinate regulizer, code doesn't work without it
            self.tanuki_r = self.tanuki_r - 1

            self.ai_function()

            # Display grid information (can be turned off if performance issue exists)
            # if self.show_grid_info:
            #     for row in range(12):
            #         for col in range(20):
            #             c = self.move_grid[row][col] * 255 / 12
            #             arr[col, row] = (c, c, c)
            #         for col in range(20, 40):
            #             if self.kill_grid[row][col-20]:
            #                 arr[col, row] = (255, 0, 0)
            #             else:
            #                 arr[col, row] = (255, 255, 255)
            #
            #     # pygame.transform.scale(backscreen, screen_size, screen)
            #     # pygame.display.flip()

            # We must allow enough CPU time for the main game application
            # Polling interval can be reduced if you don't display the grid information
            time.sleep(0.5)

            #Gameover check so that code will stop when bot is finished with game
            if self.game.isGameOver or self.isGameClear:
                break

        print("Exiting " + self.name)


def main():
    ag = Agent(1, "to lose my mind", 1, True)
    ag.game = game_core.GameMain()
    ag.start()

    ag.game.set_location(800, 400)

    #Uncomment below for recording
    #ag.game.isRecording = True
    #ag.game.replay('replay.rpy')  # You can specify replay file name or it will be generated using timestamp

    # Uncomment below to replay recorded play
    # ag.game.isReplaying = True
    # ag.game.replay('replay_clear.rpy')

    ag.game.reset()
    arcade.run()


if __name__ == "__main__":
    main()