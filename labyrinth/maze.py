"""Classes for creating and working with mazes."""

from enum import Enum
from typing import Callable, Optional, Set, Tuple

from labyrinth.generate import MazeGenerator, RandomDepthFirstSearchGenerator
from labyrinth.grid import Cell, Grid


class Direction(Enum):
    """Enumeration of the directions allowed for movement within a maze."""
    N = (0, -1)
    S = (0, 1)
    E = (1, 0)
    W = (-1, 0)

    @property
    def dx(self) -> int:
        """Return the change in x (column) when moving in this direction."""
        return self.value[0]

    @property
    def dy(self) -> int:
        """Return the change in y (row) when moving in this direction."""
        return self.value[1]

    @property
    def opposite(self) -> 'Direction':
        """Return the direction opposite to this direction."""
        return next(d for d in self.__class__ if (d.dx, d.dy) == (-self.dx, -self.dy))

    @classmethod
    def between(cls, start_cell: Cell, end_cell: Cell) -> 'Direction':
        """Return the direction between the given start and end cells, which are assumed to be adjacent."""
        dx = end_cell.column - start_cell.column
        dy = end_cell.row - start_cell.row
        return next(d for d in cls if (d.dx, d.dy) == (dx, dy))


class Maze:
    """Representation of a maze as a graph with a grid structure."""

    def __init__(self, width: int = 10, height: int = 10,
                 generator: Optional[MazeGenerator] = RandomDepthFirstSearchGenerator()) -> None:
        """Initialize a Maze."""
        self._grid = Grid(width, height)
        if generator:
            generator.generate(self)

    def __getitem__(self, item: Tuple[int, int]) -> Cell:
        """Return the cell in the maze at the given coordinates."""
        return self._grid[item]

    def __str__(self) -> str:
        """Return a string representation of the maze."""
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
        """Return the width (number of columns) of this maze."""
        return self._grid.width

    @property
    def height(self) -> int:
        """Return the height (number of rows) of this maze."""
        return self._grid.height

    def get_cell(self, row: int, column: int) -> Cell:
        """Return the cell in the maze at the given row and column."""
        return self._grid.get_cell(row, column)

    def neighbors(self, row: int, column: int) -> Set[Cell]:
        """Return a set of all neighbors of the cell in the maze at the given row and column."""
        return self._grid.neighbors(row, column)

    def depth_first_search(self, start_row: int, start_column: int, visit_fn: Callable[[Cell], None]):
        """Perform a depth-first search of the maze, starting from the cell at the given row and column."""
        self._grid.graph.depth_first_search(self[start_row, start_column], visit_fn)

    @staticmethod
    def open_wall(start_cell: Cell, end_cell: Cell) -> None:
        """Open (remove) the walls between the given start and end cells, which are assumed to be adjacent."""
        direction = Direction.between(start_cell, end_cell)
        start_cell.open_walls.add(direction)
        end_cell.open_walls.add(direction.opposite)
