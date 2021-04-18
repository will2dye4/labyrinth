"""Generate mazes using the random depth-first search algorithm."""

from dataclasses import dataclass
from enum import Enum
from typing import Callable, Optional, Set
import abc
import random

from labyrinth.grid import Cell
from labyrinth.utils.event import EventDispatcher


class MazeUpdateType(Enum):
    """Enumeration of all maze update event types."""
    WALL_REMOVED = 1
    CELL_MARKED = 2


@dataclass
class MazeUpdate:
    """Data class holding the state of an update to a maze."""
    type: MazeUpdateType
    start_cell: Cell
    end_cell: Optional[Cell] = None
    new_frontier_cells: Optional[Set[Cell]] = None


class MazeGenerator(abc.ABC, EventDispatcher[MazeUpdate]):
    """Abstract base class for a maze generator."""

    def __init__(self, event_listener: Optional[Callable[[MazeUpdate], None]] = None) -> None:
        """Initialize a MazeGenerator with an optional event listener."""
        super().__init__(event_listener=event_listener)
        self.maze = None

    def on_wall_removed(self, start_cell: Cell, end_cell: Cell) -> None:
        """Invoke the event listener (if any) when a wall is removed from the maze."""
        state = MazeUpdate(type=MazeUpdateType.WALL_REMOVED, start_cell=start_cell, end_cell=end_cell)
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
    MazeGenerator subclass that generates mazes using the random depth-first search (DFS) algorithm.

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


class PrimsGenerator(MazeGenerator):
    """MazeGenerator subclass that generates mazes using a modified version of Prim's algorithm."""

    def __init__(self, event_listener: Optional[Callable[[MazeUpdate], None]] = None) -> None:
        """Initialize a PrimsGenerator with an optional event listener."""
        super().__init__(event_listener)
        self.included_cells = set()
        self.frontier = set()

    def on_cell_marked(self, cell: Cell, new_frontier_cells: Set[Cell]):
        state = MazeUpdate(type=MazeUpdateType.CELL_MARKED, start_cell=cell, new_frontier_cells=new_frontier_cells)
        self.on_state_changed(state)

    def mark(self, cell: Cell) -> None:
        """Mark a cell as being part of the maze, and add its neighbors to the set of frontier cells."""
        self.included_cells.add(cell)
        new_frontier_cells = set(n for n in self.maze.neighbors(*cell.coordinates) if not n.open_walls)
        self.frontier |= new_frontier_cells
        self.on_cell_marked(cell, new_frontier_cells)

    def generate_maze(self) -> None:
        """Generate paths through a maze using a modified version of Prim's algorithm."""
        start_cell = self.maze[random.randrange(self.maze.height), random.randrange(self.maze.width)]
        self.mark(start_cell)
        while self.frontier:
            next_cell = self.frontier.pop()
            neighbor = next(cell for cell in self.maze.neighbors(*next_cell.coordinates) if cell in self.included_cells)
            self.maze.open_wall(next_cell, neighbor)
            self.on_wall_removed(next_cell, neighbor)
            self.mark(next_cell)
