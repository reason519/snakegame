import torch
from sb3_contrib import MaskablePPO
from snake.solver.cnn.snake_game_custom_wrapper_cnn import SnakeEnv
from snake.game import GameConf,Game
import time
import pygame
# MODEL_PATH = r"./models/ppo_snake_重走路径惩罚.zip"
MODEL_PATH = r"./models/ppo_snake_5000000_steps.zip"
# MODEL_PATH = r"./models/ppo_snake_437500_steps.zip"
# MODEL_PATH = r"./models/ppo_snake_531250_steps.zip"

NUM_EPISODE = 1000

conf = GameConf()
conf.solver_name = "RFCNNSolver"
conf.mode = "test_rfcnn"
print(f"Solver: {conf.solver_name}   Mode: {conf.mode}")
game=Game(conf,0)
env = SnakeEnv(game,0)

pygame.init()
pygame.display.set_caption(conf.title)
env.game.screen = pygame.display.set_mode((conf.map_width, conf.map_height))

RENDER = False
FRAME_DELAY = 0.3 # 0.01 fast, 0.05 slow
ROUND_DELAY = 5

# Load the trained model
model = MaskablePPO.load(MODEL_PATH)
print(model.policy)

total_step=0
total_reward = 0
total_score = 0
min_score = 1e9
max_score = 0

for episode in range(NUM_EPISODE):
    obs = env.reset()
    episode_reward = 0
    done = False

    num_step = 0
    info = None

    sum_step_reward = 0

    retry_limit = 9
    print(f"=================== Episode {episode + 1} ==================")
    while not done:
        action, _ = model.predict(obs, action_masks=env.get_action_mask())
        prev_mask = env.get_action_mask()
        prev_direction = env.game.snake.direc
        num_step += 1
        obs, reward, done, info = env.step(action)

        if done:
            if len(env.game.snake.bodies) == env.game._conf.map_rows**2:
                print(f"You are BREATHTAKING! Victory reward: {reward:.4f}.")
            else:
                # LEFT = 1    UP = 2    RIGHT = 3    DOWN = 4
                last_action = ["LEFT", "UP", "RIGHT", "DOWN"][action]
                print(f"Gameover Penalty: {reward:.4f}. Last action: {last_action}")

        elif env.game.snake.iseatfood:
            print(
                f"Food obtained at step {num_step:04d}. Food Reward: {reward:.4f}. Step Reward: {sum_step_reward:.4f}")
            sum_step_reward = 0

        else:
            sum_step_reward += reward

        episode_reward += reward
        if RENDER:
            env.render()
            time.sleep(FRAME_DELAY)

    episode_score = env.game.score
    if episode_score < min_score:
        min_score = episode_score
    if episode_score > max_score:
        max_score = episode_score

    snake_size = len(game.snake.bodies)
    print(
        f"Episode {episode + 1}: Reward Sum: {episode_reward:.4f}, Score: {episode_score}, Total Steps: {num_step}, Snake Size: {snake_size}")
    total_reward += episode_reward
    total_score += len(env.game.snake.bodies)
    total_step+=num_step
    if RENDER:
        time.sleep(ROUND_DELAY)

env.close()
print(f"=================== Summary ==================")
print(
    f"Average Score: {total_score / NUM_EPISODE},Average Step: {total_step / NUM_EPISODE}, Min Score: {min_score}, Max Score: {max_score}, Average reward: {total_reward / NUM_EPISODE}")
