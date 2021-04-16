"""Generate mazes using the random depth-first search algorithm."""

from dataclasses import dataclass
from enum import Enum
from typing import Callable, Optional
import abc

from labyrinth.grid import Cell
from labyrinth.utils.event import EventDispatcher


class MazeUpdateType(Enum):
    """Enumeration of all maze update event types."""
    WALL_REMOVED = 1


@dataclass
class MazeUpdate:
    """Data class holding the state of an update to a maze."""
    type: MazeUpdateType
    start_cell: Cell
    end_cell: Cell


class MazeGenerator(abc.ABC, EventDispatcher[MazeUpdate]):
    """Abstract base class for a maze generator."""

    def __init__(self, event_listener: Optional[Callable[[MazeUpdate], None]] = None) -> None:
        """Initialize a MazeGenerator with an optional event listener."""
        super().__init__(event_listener=event_listener)
        self.maze = None

    def on_wall_removed(self, start_cell: Cell, end_cell: Cell) -> None:
        """Invoke the event listener (if any) when a wall is removed from the maze."""
        state = MazeUpdate(MazeUpdateType.WALL_REMOVED, start_cell, end_cell)
        super().on_state_changed(state)

    def generate(self, maze: 'Maze') -> None:
        """Generate paths through the given maze."""
        self.maze = maze
        self.generate_maze()
        self.maze = None

    @abc.abstractmethod
    def generate_maze(self) -> None:
        """Generate paths through a maze."""
        raise NotImplemented


class RandomDepthFirstSearchGenerator(MazeGenerator):
    """
    MazeGenerator subclass that generates mazes using the recursive depth-first search algorithm.

    This algorithm is also known as the 'recursive backtrack' algorithm. The algorithm is equivalent to the following:

    def recursive_backtrack(maze, row=0, column=0):
        cell = maze[row, column]
        for neighbor in maze.neighbors(row, column):
            if not neighbor.open_walls:
                maze.open_wall(cell, neighbor)
                recursive_backtrack(maze, neighbor.row, neighbor.column)
    """

    def __init__(self, event_listener: Optional[Callable[[MazeUpdate], None]] = None) -> None:
        """Initialize a RandomDepthFirstSearchGenerator with an optional event listener."""
        super().__init__(event_listener)
        self.prev_cells = {}

    def cell_visitor(self, cell: Cell) -> None:
        """Visitor function for the depth-first search algorithm."""
        if cell in self.prev_cells:
            self.maze.open_wall(self.prev_cells[cell], cell)
            self.on_wall_removed(self.prev_cells[cell], cell)
        for neighbor in self.maze.neighbors(*cell.coordinates):
            if not neighbor.open_walls:
                self.prev_cells[neighbor] = cell

    def generate_maze(self) -> None:
        """Generate paths through a maze using random depth-first search."""
        self.maze.depth_first_search(0, 0, self.cell_visitor)
