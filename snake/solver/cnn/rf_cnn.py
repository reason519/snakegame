import os
import random

import torch
# from stable_baselines3.common.monitor import  Monitor
from stable_baselines3.common.vec_env import SubprocVecEnv,DummyVecEnv
from stable_baselines3.common.callbacks import CheckpointCallback
from stable_baselines3 import PPO

from sb3_contrib import MaskablePPO
from sb3_contrib.common.wrappers import ActionMasker
from snake.solver.base import BaseSolver
from snake.solver.cnn.snake_game_custom_wrapper_cnn import SnakeEnv
import sys
import time

# def make_env(conf,seed=0):
#     def _init():
#         env = SnakeEnv(conf,seed=seed)
#         env = ActionMasker(env, SnakeEnv.get_action_mask)
#         env = Monitor(env)
#         env.seed(seed)
#
#         return env
#     return _init

# Linear scheduler
def linear_schedule(initial_value, final_value=0.0):

    if isinstance(initial_value, str):
        initial_value = float(initial_value)
        final_value = float(final_value)
        assert (initial_value > 0.0)

    def scheduler(progress):
        return final_value + progress * (initial_value - final_value)

    return scheduler

class RFCNNSolver(BaseSolver):
    def __init__(self, snake):
        super().__init__(snake)



    def train(self,game):
        # Generate a list of random seeds for each environment.
        # seed_set = set()
        # while len(seed_set) < conf.NUM_ENV:
        #     seed_set.add(random.randint(0, 1e9))
        #     # Create the Snake environment.
        #     # env = SubprocVecEnv([make_env(seed=s) for s in seed_set])
        #     env = DummyVecEnv([make_env(conf,seed=s) for s in seed_set])

        # models_dir = f"models/{int(time.time())}/"
        models_dir = f"models/"
        # logdir = f"logs/{int(time.time())}/"
        logdir = f"logs/"

        env = SnakeEnv(game,0)
        env = ActionMasker(env, SnakeEnv.get_action_mask)
        # env.reset()

        if not os.path.exists(models_dir):
            os.makedirs(models_dir)

        if not os.path.exists(logdir):
            os.makedirs(logdir)
        lr_schedule = linear_schedule(3.5e-4, 2.5e-5)
        clip_range_schedule = linear_schedule(0.150, 0.025)

        model = MaskablePPO('CnnPolicy', env,
                            # device="cuda",
                            # n_steps=2048,
                            n_steps=2048,
                            batch_size=512,
                            n_epochs=4,
                            # gamma=0.94,
                            gamma=0.9999,
                            learning_rate=lr_schedule,
                            clip_range=clip_range_schedule,
                            verbose=1,tensorboard_log=logdir)

        checkpoint_interval = 15625  # checkpoint_interval * num_envs = total_steps_per_checkpoint
        # checkpoint_interval = 1e6  # checkpoint_interval * num_envs = total_steps_per_checkpoint
        # checkpoint_interval = 1e8  # checkpoint_interval * num_envs = total_steps_per_checkpoint
        checkpoint_callback = CheckpointCallback(save_freq=checkpoint_interval, save_path=models_dir,
                                                 name_prefix="ppo_snake")
        # Writing the training logs from stdout to a file
        # original_stdout = sys.stdout
        # log_file_path = os.path.join(save_dir, "training_log.txt")
        # with open(log_file_path, 'w') as log_file:
        #     sys.stdout = log_file
        #
        model.learn(
            # total_timesteps=int(100000000),
            total_timesteps=int(5000000),
            reset_num_timesteps=False,
            callback=[checkpoint_callback]
        )

        #     env.close()
        #
        # # Restore stdout
        # sys.stdout = original_stdout

        # Save the final model
        model.save(os.path.join(models_dir, "ppo_snake_final.zip"))

# NUM_ENV=8
#
# def make_env(seed=0):
#     def _init():
#         env = SnakeEnv(seed=seed)
#         env = ActionMasker(env, SnakeEnv.get_action_mask)
#         env = Monitor(env)
#         env.seed(seed)
#
#         return env
#     return _init
#
# def main():
#     # Generate a list of random seeds for each environment.
#     seed_set = set()
#     while len(seed_set) < NUM_ENV:
#         seed_set.add(random.randint(0, 1e9))
#     env = DummyVecEnv([make_env(seed=s) for s in seed_set])
#
#
# if __name__ == "__main__":
#     main()