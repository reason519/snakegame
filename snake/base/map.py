import random

from snake.base.point import Point, PointType
from snake.base.pos import Pos


class Map:
    """2D game map."""

    def __init__(self, num_rows, num_cols):
        """Initialize a Map object."""
        if not isinstance(num_rows, int) or not isinstance(num_cols, int):
            raise TypeError("'num_rows' and 'num_cols' must be integers")
        if num_rows < 5 or num_cols < 5:
            raise ValueError("'num_rows' and 'num_cols' must >= 5")
        self._num_rows = num_rows
        self._num_cols = num_cols
        self._capacity = (num_rows - 2) * (num_cols - 2)
        self._content = [[Point() for _ in range(num_cols)] for _ in range(num_rows)]
        self.reset()

        self.pre_del_food=None

        # random.seed(5)

    def reset(self):
        self._food = []
        for i in range(self._num_rows):
            for j in range(self._num_cols):
                if (
                    i == 0
                    or i == self._num_rows - 1
                    or j == 0
                    or j == self._num_cols - 1
                ):
                    self._content[i][j].type = PointType.WALL
                else:
                    self._content[i][j].type = PointType.EMPTY

    def copy(self):
        m_copy = Map(self._num_rows, self._num_cols)
        for i in range(self._num_rows):
            for j in range(self._num_cols):
                m_copy._content[i][j].type = self._content[i][j].type
        return m_copy

    @property
    def num_rows(self):
        return self._num_rows

    @property
    def num_cols(self):
        return self._num_cols

    @property
    def capacity(self):
        return self._capacity

    @property
    def food(self):
        return self._food

    def point(self, pos):
        """Return a point on the map.

        DO NOT directly modify the point type to PointType.FOOD and vice versa.
        Use {add|rm}_food() methods instead.

        Args:
            pos (base.pos.Pos): The position of the point to be fetched

        Returns:
            snake.point.Point: The point at the given position.

        """
        return self._content[pos.x][pos.y]

    def is_inside(self, pos):
        return (
            pos.x > 0
            and pos.x < self.num_rows - 1
            and pos.y > 0
            and pos.y < self.num_cols - 1
        )

    def is_empty(self, pos):
        return self.is_inside(pos) and self.point(pos).type == PointType.EMPTY

    def is_safe(self, pos):
        return self.is_inside(pos) and (
            self.point(pos).type == PointType.EMPTY
            or self.point(pos).type == PointType.FOOD
        )

    def is_full(self):
        """Check if the map is filled with the snake's bodies."""
        for i in range(1, self.num_rows - 1):
            for j in range(1, self.num_cols - 1):
                t = self._content[i][j].type
                if t.value < PointType.HEAD_L.value:
                    return False
        return True

    def has_food(self):
        return len(self._food)>0

    def rm_food(self,pos):
        if self.has_food() and (pos in self._food):
            self.point(pos).type = PointType.EMPTY
            self._food.remove(pos)
            self.pre_del_food=pos
        self.create_rand_food()

    def create_food(self, pos):
        self.point(pos).type = PointType.FOOD
        self._food.append(pos)
        return self._food

    def create_rand_food(self,k=3):
        empty_pos = []
        for i in range(1, self._num_rows - 1):
            for j in range(1, self._num_cols - 1):
                t = self._content[i][j].type
                if t == PointType.EMPTY:
                    empty_pos.append(Pos(i, j))
                # elif t == PointType.FOOD:
                #     return None  # Stop if food exists
        if empty_pos:
            if len(empty_pos)>=2:
                food_list=random.sample(empty_pos,k=2)
            else:
                food_list=empty_pos
            for f in food_list:
                if f!=self.pre_del_food and \
                        f not in self._food and len(self._food)<k:
                    self.create_food(f)
            return self._food
        return None
