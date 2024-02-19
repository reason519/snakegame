import argparse

from snake.game import Game, GameConf, GameMode


def main():
    dict_solver = {
        "greedy": "GreedySolver",
        "hamilton": "HamiltonSolver",
        "dqn": "DQNSolver",
        "rfcnn":"RFCNNSolver"
    }
    dict_mode = {
        "normal": GameMode.NORMAL,
        "bcmk": GameMode.BENCHMARK,
        "train_rfcnn": GameMode.TRAIN_RFCNN,
        "train_rfcnn_gui": GameMode.TRAIN_RFCNN_GUI,
    }
    # dict_mode = {
    #     "normal": GameMode.NORMAL,
    #     "bcmk": GameMode.BENCHMARK,
    #     "train_dqn": GameMode.TRAIN_DQN,
    #     "train_dqn_gui": GameMode.TRAIN_DQN_GUI,
    # }

    parser = argparse.ArgumentParser(description="Run snake game agent.")
    parser.add_argument(
        "-s",
        default="rfcnn",
        choices=dict_solver.keys(),
        help="name of the solver to direct the snake (default: hamilton)",
    )
    parser.add_argument(
        "-m",
        default="train_rfcnn",
        choices=dict_mode.keys(),
        help="game mode (default: normal)",
    )
    args = parser.parse_args()

    conf = GameConf()
    conf.solver_name = dict_solver[args.s]
    conf.mode = dict_mode[args.m]
    print(f"Solver: {conf.solver_name}   Mode: {conf.mode}")
    Game(conf,0).run()


if __name__ == "__main__":
    main()
