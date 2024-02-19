import errno
import os
import random
import traceback
from enum import Enum, unique
import pygame


from snake.base import Direc, Map, PointType, Pos, Snake
from snake.gui import GameWindow

# Add solver names to globals()
from snake.solver import DQNSolver, GreedySolver, HamiltonSolver,RFCNNSolver


@unique
class GameMode(Enum):
    NORMAL = 0  # AI with GUI
    BENCHMARK = 1  # Run benchmarks without GUI
    TRAIN_RFCNN = 2  # Train DQNSolver without GUI
    TRAIN_RFCNN_GUI = 3
    TRAIN_DQN = 4  # Train DQNSolver without GUI
    TRAIN_DQN_GUI = 5  # Train DQNSolver with GUI


class GameConf:
    def __init__(self):
        """Initialize a default configuration."""

        # Game mode
        self.mode = GameMode.NORMAL

        # Solver
        self.solver_name = "HamiltonSolver"  # Class name of the solver

        # Size
        self.map_rows = 8
        self.map_cols = self.map_rows

        self.map_cell=25
        self.map_width = self.map_rows*self.map_cell  # pixels
        self.map_height = self.map_width
        self.info_panel_width = 155  # pixels
        self.window_width = self.map_width + self.info_panel_width
        self.window_height = self.map_height
        self.grid_pad_ratio = 0.0

        # Switch
        self.show_grid_line = False
        self.show_info_panel = True

        # Delay
        # self.interval_draw = 20  # ms
        self.interval_draw = 20  # ms
        self.pre_interval_draw=self.interval_draw

        # Color
        self.color_bg = "#F4F4F4"
        # self.color_bg = "#FFFFFF"
        self.color_txt = "#F5F5F5"
        self.color_line = "#424242"
        self.color_wall = "#F5F5F5"
        self.color_food = "#0000FF"
        self.color_head = "#FF0000"
        self.color_body = [0,255,0]
        self.chang_body_time=3  #身体颜色改变时长
        # self.color_bg = "#000000"
        # self.color_txt = "#F5F5F5"
        # self.color_line = "#424242"
        # self.color_wall = "#F5F5F5"
        # self.color_food = "#FFF59D"
        # self.color_head = "#F5F5F5"
        # self.color_body = "#F5F5F5"
        # Initial snake
        self.init_direc = Direc.RIGHT
        board=self.map_rows // 2
        # self.init_bodies = [Pos(1, 4), Pos(1, 3), Pos(1, 2), Pos(1, 1)]
        self.init_bodies = [Pos(board-2, board), Pos(board-1, board), Pos(board, board), Pos(board+1, board)]
        self.init_types = [PointType.HEAD_R] + [PointType.BODY_HOR] * 3

        # Font
        self.font_info = ("Arial", 9)

        # Info
        self.info_str = (
            "<w/a/s/d>: snake direction\n"
            "<space>: pause/resume\n"
            "<r>: restart    <esc>: exit\n"
            "-----------------------------------\n"
            "status: %s\n"
            "episode: %d   step: %d\n"
            "length: %d/%d (" + str(self.map_rows) + "x" + str(self.map_cols) + ")\n"
            "-----------------------------------"
        )
        self.info_status = ["eating", "dead", "full"]

        # rfcnn train 参数
        self.NUM_ENV = 8
        self.title="Snake"

        self.show_ui=True



class Game:
    def __init__(self, conf,seed=0):
        self._conf = conf
        self._map = Map(conf.map_rows + 2, conf.map_cols + 2)
        self._snake = Snake(
            self._map, conf.init_direc, conf.init_bodies, conf.init_types
        )
        self._pause = False
        print(globals())
        self._solver = globals()[self._conf.solver_name](self._snake)
        self._episode = 1
        # self._init_log_file()
        if conf.solver_name=="rfcnn":
            random.seed(seed)


    @property
    def snake(self):
        return self._snake

    @property
    def episode(self):
        return self._episode

    def run(self):
        if self._conf.mode == GameMode.BENCHMARK:
            self._run_benchmarks()
        elif self._conf.mode == GameMode.TRAIN_RFCNN:
            self._run_rfcnn_train()
            # self._plot_history()
        # elif self._conf.mode == GameMode.TRAIN_DQN_GUI:
        #     window.show(self._game_main_dqn_train)
        #     self._plot_history()
        else:
            from snake.pygamegui import GameWindow
            window=GameWindow("Snake",self._conf,self._map,self)
            # window = GameWindow(
            #     "Snake",
            #     self._conf,
            #     self._map,
            #     self,
            #     self._on_exit,
            #     (
            #         ("<w>", lambda e: self._update_direc(Direc.UP)),
            #         ("<a>", lambda e: self._update_direc(Direc.LEFT)),
            #         ("<s>", lambda e: self._update_direc(Direc.DOWN)),
            #         ("<d>", lambda e: self._update_direc(Direc.RIGHT)),
            #         ("<r>", lambda e: self._reset()),
            #         ("<space>", lambda e: self._toggle_pause()),
            #     ),
            # )
            # if self._conf.mode == GameMode.NORMAL:
            #     window.show(self._game_main_normal)
            # elif self._conf.mode == GameMode.TRAIN_DQN_GUI:
            #     window.show(self._game_main_dqn_train)
            #     self._plot_history()

    def _run_benchmarks(self):
        steps_limit = 5000
        num_episodes = int(input("Please input the number of episodes: "))

        print(f"\nMap size: {self._conf.map_rows}x{self._conf.map_cols}")
        print(f"Solver: {self._conf.solver_name[:-6].lower()}\n")

        tot_len, tot_steps = 0, 0

        for _ in range(num_episodes):
            print(f"Episode {self._episode} - ", end="")
            while True:
                self._game_main_normal()
                if self._map.is_full():
                    print(
                        f"FULL (len: {self._snake.len()} | steps: {self._snake.steps})"
                    )
                    break
                if self._snake.dead:
                    print(
                        f"DEAD (len: {self._snake.len()} | steps: {self._snake.steps})"
                    )
                    break
                if self._snake.steps >= steps_limit:
                    print(
                        f"STEP LIMIT (len: {self._snake.len()} | steps: {self._snake.steps})"
                    )
                    # self._write_logs()  # Write the last step
                    break
            tot_len += self._snake.len()
            tot_steps += self._snake.steps
            self._reset()

        avg_len = tot_len / num_episodes
        avg_steps = tot_steps / num_episodes
        print(
            f"\n[Summary]\nAverage Length: {avg_len:.2f}\nAverage Steps: {avg_steps:.2f}\n"
        )

        self._on_exit()

    def _run_rfcnn_train(self):
        try:
            self._game_main_rfcnn_train()

            # while not self._game_main_dqn_train():
            #     pass
        except KeyboardInterrupt:
            pass
        except Exception:
            traceback.print_exc()
        finally:
            self._on_exit()

    def _game_main_rfcnn_train(self):
        if not self._map.has_food():
            self._map.create_rand_food()

        if self._pause:
            return
        if self._conf.show_ui:
            pygame.init()
            pygame.display.set_caption(self._conf.title)

            self.screen = pygame.display.set_mode((self._conf.map_width, self._conf.map_height))

        # episode_end, learn_end = self._solver.train(self)
        self._solver.train(self)




    def _game_main_dqn_train(self):
        if not self._map.has_food():
            self._map.create_rand_food()

        if self._pause:
            return

        episode_end, learn_end = self._solver.train()

        if episode_end:
            self._reset()

        return learn_end

    def _game_main_normal(self):
        if not self._map.has_food():
            self._map.create_rand_food()

        if self._pause or self._is_episode_end():
            return "game_over"

        self._update_direc(self._solver.next_direc())

        # if self._conf.mode == GameMode.NORMAL and self._snake.direc_next != Direc.NONE:
        #     self._write_logs()

        game_over=self._snake.move()
        return game_over
        # if self._is_episode_end():
        #     self._write_logs()  # Write the last step

    def _plot_history(self):
        self._solver.plot()

    def _update_direc(self, new_direc):
        self._snake.direc_next = new_direc
        if self._pause:
            self._snake.move()

    def _toggle_pause(self):
        self._pause = not self._pause

    def _is_episode_end(self):
        return self._snake.dead or self._map.is_full()

    def _reset(self):
        self._snake.reset()
        #self._episode += 1
        self.score = 0

    def _on_exit(self):
        # if self._log_file:
        #     self._log_file.close()
        if self._solver:
            self._solver.close()


    def render(self):
        self.screen.fill(self._conf.color_bg)
        # Draw  food
        if self._map.has_food():
            for food in self._map._food:
                self.draw_rect(food.x, food.y, self._conf.color_food)

        # Draw snake
        self.draw_snake()

        #Draw text
        # self.draw_text()

        pygame.display.flip()


    def draw_snake(self):
        head=self._snake._bodies[0]
        self.draw_rect(head.x,head.y,self._conf.color_head)


        for i in range(1,len(self._snake._bodies)):
            c, r = self._snake._bodies[i].x, self._snake._bodies[i].y

            self.draw_rect(c,r,self._conf.color_body)




    def draw_rect(self,x,y,color):
        x=x-1
        y=y-1
        cell_size = self._conf.map_cell
        head_x = y * cell_size
        head_y = x * cell_size
        rect=pygame.Rect(head_x, head_y, cell_size, cell_size)
        self.screen.fill(color, rect)
        pygame.draw.rect(self.screen, (50, 50, 50),rect, 1,)
        rect.inflate_ip(-1, -1)


    def draw_text(self):
        font1=pygame.font.SysFont("仿宋gb2312",12)
        text = font1.render("得分:" + str(len(self._snake._bodies)-4), True, (64, 64, 64))
        self.screen.blit(text, (7, 7))

        # text = font1.render("不是录播:" + str(int(self._snake.velocity)), True, (64, 64, 64))
        # self.screen.blit(text, (10, 52))

        text=font1.render("速度:"+str(int(self._snake.velocity)),True,(64,64,64))
        # self.screen.blit(text,(10,25))
        self.screen.blit(text,(100,7))

    # def _init_log_file(self):
    #     try:
    #         os.makedirs("logs")
    #     except OSError as e:
    #         if e.errno != errno.EEXIST:
    #             raise
    #     try:
    #         self._log_file = None
    #         self._log_file = open("logs/snake.log", "w", encoding="utf-8")
    #     except FileNotFoundError:
    #         if self._log_file:
    #             self._log_file.close()
    #
    # def _write_logs(self):
    #     self._log_file.write(
    #         f"[ Episode {self._episode} / Step {self._snake.steps} ]\n"
    #     )
    #     for i in range(self._map.num_rows):
    #         for j in range(self._map.num_cols):
    #             pos = Pos(i, j)
    #             t = self._map.point(pos).type
    #             if t == PointType.EMPTY:
    #                 self._log_file.write("  ")
    #             elif t == PointType.WALL:
    #                 self._log_file.write("# ")
    #             elif t == PointType.FOOD:
    #                 self._log_file.write("F ")
    #             elif (
    #                 t == PointType.HEAD_L
    #                 or t == PointType.HEAD_U
    #                 or t == PointType.HEAD_R
    #                 or t == PointType.HEAD_D
    #             ):
    #                 self._log_file.write("H ")
    #             elif pos == self._snake.tail():
    #                 self._log_file.write("T ")
    #             else:
    #                 self._log_file.write("B ")
    #         self._log_file.write("\n")
    #     self._log_file.write(
    #         f"[ last/next direc: {self._snake.direc}/{self._snake.direc_next} ]\n"
    #     )
    #     self._log_file.write("\n")
