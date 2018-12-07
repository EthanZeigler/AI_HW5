import arcade
import game_core
import threading
import time
import os
import pygame
import game_map as ai
from matplotlib import pyplot as plt
import sys


class Agent(threading.Thread):

    def __init__(self, threadID, name, counter, show_grid_info=True):
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
        for line in game_map.state_grid:
            print('[' + ' '.join('{}'.format(k[1]) for k in enumerate(line)) + ']')

        fig = plt.figure(num=None, figsize=(30, 10), dpi=200, facecolor='w', edgecolor='k')
        ax = fig.add_subplot(111)
        ax.xaxis.set_visible(True)
        ax.yaxis.set_visible(True)
        the_table = ax.table(cellText=game_map.state_grid,
                             loc='center')
        plt.savefig("/media/sf_Ethan/Desktop/t_left.png")

        sys.exit(-1)


    def run(self):
        print("Starting " + self.name)

        os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % (50+320, 50)
        pygame.init()

        # Prepare grid information display (can be turned off if performance issue exists)
        if self.show_grid_info:
            screen_size = [200, 120]
            backscreen_size = [40, 12]

            screen = pygame.display.set_mode(screen_size)
            backscreen = pygame.Surface(backscreen_size)
            arr = pygame.PixelArray(backscreen)
        else:
            time.sleep(0.5)  # wait briefly so that main game can get ready

        # roughly every 50 milliseconds, retrieve game state (average human response time for visual stimuli = 25 ms)
        go = True
        while go and (self.game is not []):
            # Dispatch events from pygame window event queue
            if self.show_grid_info:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        go = False
                        break

            # RETRIEVE CURRENT GAME STATE
            self.move_grid, self.kill_grid, \
                self.isGameClear, self.isGameOver, self.current_stage, self.time_limit, \
                self.total_score, self.total_time, self.total_life, self.tanuki_r, self.tanuki_c \
                = self.game.get_game_state()

            self.ai_function()

            # Display grid information (can be turned off if performance issue exists)
            if self.show_grid_info:
                for row in range(12):
                    for col in range(20):
                        c = self.move_grid[row][col] * 255 / 12
                        arr[col, row] = (c, c, c)
                    for col in range(20, 40):
                        if self.kill_grid[row][col-20]:
                            arr[col, row] = (255, 0, 0)
                        else:
                            arr[col, row] = (255, 255, 255)

                pygame.transform.scale(backscreen, screen_size, screen)
                pygame.display.flip()

            # We must allow enough CPU time for the main game application
            # Polling interval can be reduced if you don't display the grid information
            time.sleep(0.05)

        print("Exiting " + self.name)


def main():
    ag = Agent(1, "My Agent", 1, True)
    ag.start()

    ag.game = game_core.GameMain()
    ag.game.set_location(50, 50)

    # Uncomment below for recording
    # ag.game.isRecording = True
    # ag.game.replay('replay.rpy')  # You can specify replay file name or it will be generated using timestamp

    # Uncomment below to replay recorded play
    # ag.game.isReplaying = True
    # ag.game.replay('replay_clear.rpy')

    ag.game.reset()
    arcade.run()


if __name__ == "__main__":
    main()