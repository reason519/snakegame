from snake.base.pos import Pos
from snake.solver.base import BaseSolver
from snake.solver.path import PathSolver
import time
from collections import deque

class GreedySolver(BaseSolver):
    def __init__(self, snake):
        super().__init__(snake)
        self.path_to_tail=deque()
        self._path_solver = PathSolver(snake)

    def next_direc(self):
        # Create a virtual snake
        s_copy, m_copy = self.snake.copy()

        # Step 1
        self._path_solver.snake = self.snake
        path_to_food = self._path_solver.shortest_path_to_food()


        if path_to_food:
            # 最后有空行，强制蛇吃食物
            # if self.snake.len() >(self.map.num_rows**2-self.map.num_rows**2*0.01)\
            #         and Pos.manhattan_dist(self.snake.head(), self.snake.tail()) < 2:
            #     return path_to_food[0]

            # Step 2
            s_copy.move_path(path_to_food)
            if m_copy.is_full() or \
                self.snake.count_step>self.map.num_rows**2:
                return path_to_food[0]
            # if len(self.snake.bodies)

            # Step 3
            self._path_solver.snake = s_copy

            path_to_tail = self._path_solver.shortest_path_to_tail()
            # path_to_tail = self._path_solver.longest_path_to_tail()

            if len(path_to_tail) > 1:
                self.path_to_tail.clear()
                return path_to_food[0]

        # Step 4
        self._path_solver.snake = self.snake
        if len(self.path_to_tail)>1:
            return self.path_to_tail.popleft()
        else:
            self.path_to_tail = self._path_solver.longest_path_to_tail()
            if len(self.path_to_tail) > 1:
                return self.path_to_tail.popleft()
        # Step 5
        head = self.snake.head()
        direc, max_dist = self.snake.direc, -1
        for adj in head.all_adj():
            if self.map.is_safe(adj):
                dist = Pos.manhattan_dist(adj, self.map.food)
                if dist > max_dist:
                    max_dist = dist
                    direc = head.direc_to(adj)
        return direc
