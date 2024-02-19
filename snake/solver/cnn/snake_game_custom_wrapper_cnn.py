import math

import gym
import numpy as np
import time
import random
import pygame
import pandas as pd


from snake.base import Direc

class SnakeEnv(gym.Env):
    def __init__(self,game, seed=0,limit_step=True):
        super().__init__()
        self.game = game
        self.game._reset()

        self.action_space = gym.spaces.Discrete(4)

        self.board_size=self.game._conf.map_rows
        self.map_cell=self.game._conf.map_cell
        self.grid_size = self.board_size ** 2  # Max length of snake is board_size^2
        self.init_snake_size = len(self.game._conf.init_bodies)
        self.max_growth = self.grid_size - self.init_snake_size
        self.pre_snake_head=self.game._conf.init_bodies[0]

        a=self.board_size*self.map_cell
        self.observation_space = gym.spaces.Box(
            low=0, high=255,
            shape=(a, a, 3),
            dtype=np.uint8
        )

        self.done = False
        if limit_step:
            self.step_limit = self.grid_size * 4*5 # More than enough steps to get the food.
        else:
            self.step_limit = 1e9 # Basically no limit.
        self.reward_step_counter = 0

        self.his_pos=[] #记录历史路径

        #用pandas将蛇长度写入csv
        # self.islog=True
        self.islog=False
        self.elapse=0
        if self.islog:
            self.df_data={"elapse":[],
                     "snakelen":[]}
            pd.DataFrame(self.df_data).to_csv("./logs/snake_pic.csv", index=False)


    def reset(self):
        self.write_log_csv()
        self.game._reset()
        # random.seed(0)

        self.done = False
        self.reward_step_counter = 0
        # self.pre_snake_head=self.game._conf.init_bodies[0]
        self.his_pos.clear()
        obs = self._generate_observation()
        return obs

    def action_to_direct(self,action):
        cur_direc = Direc.NONE
        if action == 0:
            cur_direc = Direc.LEFT
        elif action == 1:
            cur_direc = Direc.UP
        elif action == 2:
            cur_direc = Direc.RIGHT
        elif action == 3:
            cur_direc = Direc.DOWN
        return cur_direc

    def step(self,action):

        for event in pygame.event.get():
            pass

        if not self.game.snake.map.has_food():
            self.game.snake.map.create_rand_food()

        #LEFT = 1    UP = 2    RIGHT = 3    DOWN = 4
        cur_direc=self.action_to_direct(action)

        self.game._update_direc(cur_direc)
        game_over=self.game.snake.move()
        if game_over=="game_over":
            self.done=True
        else:
            self.done=False
        obs=self._generate_observation()

        reward=0.0
        self.reward_step_counter+=1

        info={}
        if self.game.snake.map.is_full():
            # self.write_log_csv()
            # reward=len(self.game.snake.bodies)*0.1 # Victory reward
            reward=len(self.game.snake.bodies)*0.1 # Victory reward
            self.done=True
            return obs,reward,self.done,info

        if self.reward_step_counter > self.step_limit:  # Step limit reached, game over.
            self.reward_step_counter = 0
            self.done = True

        if self.done:  # Snake bumps into wall or itself. Episode is over.
            # Game Over penalty is based on snake size.
            # self.write_log_csv()
            # reward = -(self.grid_size - len(self.game.snake.bodies))
            reward = - math.pow(self.max_growth, (
                        self.grid_size - len(self.game.snake.bodies)) / self.max_growth)  # (-max_growth, -1)
            reward = reward * 0.1
            # reward=-(self.grid_size-len(self.game.snake.bodies))
            # reward=-2

            # reward = reward
            self.his_pos.clear()
            return obs, reward, self.done, info

        elif self.game.snake.iseatfood:  # Food eaten. Reward boost on snake size.
            self.his_pos.clear()
            reward = len(self.game.snake.bodies) / self.grid_size
            # reward = len(self.game.snake.bodies) *0.1
            # reward = len(self.game.snake.bodies)*2
            self.reward_step_counter = 0  # Reset reward step counter

        else:
            if self.game.snake.head() in self.his_pos:
                reward=-1/len(self.game.snake.bodies)
            else:
                reward = 1 / len(self.game.snake.bodies)
                self.his_pos.append(self.game.snake.head())
                reward = reward * 0.1
        #     # Give a tiny reward/penalty to the agent based on whether it is heading towards the food or not.
        #     # Not competing with game over penalty or the food eaten reward.
        #     if np.linalg.norm(self.pos2tuple(self.game.snake.head())
        #                       - self.pos2tuple(self.game.snake.map.food)) < np.linalg.norm(
        #             self.pos2tuple(self.game.snake.bodies[1])
        #             - self.pos2tuple(self.game.snake.map.food)):
        #         reward =  1/len(self.game.snake.bodies)
        #         # reward = 1 / info["snake_size"]
        #     else:
        #         reward = -1/len(self.game.snake.bodies)
        #         # reward = - 1 / info["snake_size"]
        #     reward = reward * 0.1
        # self.pre_snake_head=self.game.snake.head()
        self.render()
        # time.sleep(0.1)
        return obs, reward, self.done, info

    def render(self, mode="human"):
        self.game.render()

    def get_action_mask(self):
        return np.array([[self._check_action_validity(a) for a in range(self.action_space.n)]])

    # Check if the action is against the current direction of the snake or is ending the game.
    def _check_action_validity(self, action):
        next_direc=self.action_to_direct(action)
        current_direction = self.game.snake.direc
        # snake_list = self.game.snake
        # row, col = snake_list[0]
        if next_direc == Direc.opposite(current_direction)\
                or next_direc == Direc.NONE:
            return False

        new_head = self.game.snake.head().adj(next_direc)
        # self._bodies.appendleft(new_head)

        if  self.game.snake.map.is_safe(new_head):
            return True
        return False



    # EMPTY: BLACK; SnakeBODY: GRAY; SnakeHEAD: GREEN; FOOD: RED;
    def _generate_observation(self):
        obs = np.zeros((self.board_size, self.board_size), dtype=np.uint8)

        # Set the snake body to gray with linearly decreasing intensity from head to tail.
        obs[tuple(np.transpose([(a.x-1,a.y-1) for a in self.game._snake.bodies]))]=np.linspace(200, 50, len(self.game._snake.bodies), dtype=np.uint8)
        # obs[tuple(np.transpose(self.game._snake))] = np.linspace(200, 50, len(self.game.snake), dtype=np.uint8)

        # Stack single layer into 3-channel-image.
        obs = np.stack((obs, obs, obs), axis=-1)

        # Set the snake head to green and the tail to blue
        obs[tuple([self.game._snake.bodies[0].x-1,self.game._snake.bodies[0].y-1])] = [0, 255, 0]
        obs[tuple([self.game._snake.bodies[-1].x-1,self.game._snake.bodies[-1].y-1])] = [255, 0, 0]

        # Set the food to red
        if self.game._snake._map.has_food():
            for food in self.game._snake._map.food:
                obs[(food.x-1,food.y-1)] = [0, 0, 255]

        # Enlarge the observation to 84x84
        obs = np.repeat(np.repeat(obs, 8, axis=0), 8, axis=1)

        return obs

    def pos2tuple(self,pos):
        return np.array([pos.x-1,pos.y-1])


    def write_log_csv(self):
        if self.islog:
            self.elapse+=1
            self.df_data["snakelen"].append(len(self.game.snake.bodies))
            self.df_data["elapse"].append(self.elapse)
            if self.elapse%1000==0:
                df_csv = pd.read_csv("./logs/snake_pic.csv")
                # df_csv.append(pd.DataFrame(self.df_data), ignore_index=True)
                res=pd.concat([df_csv,pd.DataFrame(self.df_data)], ignore_index=True)
                # pd.DataFrame(self.df_data).to_csv("./logs/snake1done_fun.csv",index=False)
                res.to_csv("./logs/snake_pic.csv",index=False)
                self.df_data["snakelen"].clear()
                self.df_data["elapse"].clear()
