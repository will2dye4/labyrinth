from enum import Enum
from typing import Callable, Optional, Set, Tuple

from labyrinth.generate import MazeGenerator, RandomDepthFirstSearchGenerator
from labyrinth.grid import Cell, Grid


class Direction(Enum):
    N = (0, -1)
    S = (0, 1)
    E = (1, 0)
    W = (-1, 0)

    @property
    def dx(self) -> int:
        return self.value[0]

    @property
    def dy(self) -> int:
        return self.value[1]

    @property
    def opposite(self) -> 'Direction':
        return next(d for d in self.__class__ if (d.dx, d.dy) == (-self.dx, -self.dy))

    @classmethod
    def between(cls, start_cell: Cell, end_cell: Cell) -> 'Direction':
        dx = end_cell.column - start_cell.column
        dy = end_cell.row - start_cell.row
        return next(d for d in cls if (d.dx, d.dy) == (dx, dy))


class Maze:

    def __init__(self, width: int = 10, height: int = 10,
                 generator: Optional[MazeGenerator] = RandomDepthFirstSearchGenerator()) -> None:
        self._grid = Grid(width, height)
        if generator:
            generator.generate(self)

    def __getitem__(self, item: Tuple[int, int]) -> Cell:
        return self._grid[item]

    def __str__(self) -> str:
        cell_width = 3
        maze_str = '+' + ((('-' * cell_width) + '+') * self.width) + '\n'
        for row in range(self.height):
            maze_str += '|'
            for column in range(self.width):
                cell = self[row, column]
                maze_str += ' ' * cell_width
                maze_str += ' ' if Direction.E in cell.open_walls else '|'
            maze_str += '\n+'
            for column in range(self.width):
                maze_str += (' ' if Direction.S in self[row, column].open_walls else '-') * cell_width
                maze_str += '+'
            maze_str += '\n'
        return maze_str

    @property
    def width(self) -> int:
        return self._grid.width

    @property
    def height(self) -> int:
        return self._grid.height

    def get_cell(self, row: int, column: int) -> Cell:
        return self._grid.get_cell(row, column)

    def neighbors(self, row: int, column: int) -> Set[Cell]:
        return self._grid.neighbors(row, column)

    def depth_first_search(self, start_row: int, start_column: int, visit_fn: Callable[[Cell], None]):
        self._grid.graph.depth_first_search(self[start_row, start_column], visit_fn)

    @staticmethod
    def open_wall(start_cell: Cell, end_cell: Cell) -> None:
        direction = Direction.between(start_cell, end_cell)
        start_cell.open_walls.add(direction)
        end_cell.open_walls.add(direction.opposite)
