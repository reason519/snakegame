from snake.base import PointType, Pos
import pygame
import sys,time
from douyin import util

class GameWindow():
    def __init__(self,title, conf, game_map, game=None):
        pygame.init()
        pygame.display.set_caption(title)

        self.screen=pygame.display.set_mode((conf.map_width,conf.map_height))

        self._conf = conf
        self._map = game_map

        self.interval_time=1

        if game is not None:
            self._game = game
            self._snake = game.snake




        game_state="running"
        start_time = time.time()

        while True:
            # end_time=time.time()
            # if(end_time-start_time)>self.interval_time:
            #     self._conf.interval_draw=40

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                elif event.type==pygame.KEYDOWN:
                    if event.key==pygame.K_UP:
                        self._conf.interval_draw=0
                    if event.key==pygame.K_DOWN:
                        self._conf.interval_draw=40
                    if event.key==pygame.K_LEFT:
                        util.color_little_change(self._conf.color_body,1)
                # elif event.type==pygame.KEYUP:
                #     if event.key == pygame.K_UP:
                #         self._conf.new_interval_draw = 0
                #     elif event.key == pygame.K_DOWN:
                #         self._conf.interval_draw = 40




            if game_state == "running":
               # if time.time() - start_time >= self._conf.interval_draw:
               #      start_time=time.time()

                    game_over=self._game._game_main_normal()
                    if game_over=="game_over":
                        game_state=game_over
                        print(game_state)
                        pygame.time.wait(5000)
                        self._game._reset()
                        game_state="running"

                    self._game.render()
                    # print(time.time()-start_time)

            # if game_state=="game_over":
            #     self.game._reset()
            #     game_state="running"
            #     print("sssssss")

            pygame.time.wait(self._conf.interval_draw)






