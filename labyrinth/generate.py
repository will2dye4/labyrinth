from dataclasses import dataclass
from enum import Enum
from typing import Callable, Optional
import abc

from labyrinth.grid import Cell
from labyrinth.utils.event import EventDispatcher


class MazeUpdateType(Enum):
    WALL_REMOVED = 1


@dataclass
class MazeUpdate:
    type: MazeUpdateType
    start_cell: Cell
    end_cell: Cell


class MazeGenerator(abc.ABC, EventDispatcher[MazeUpdate]):

    def __init__(self, event_listener: Optional[Callable[[MazeUpdate], None]] = None) -> None:
        super().__init__(event_listener=event_listener)
        self.maze = None

    def on_wall_removed(self, start_cell: Cell, end_cell: Cell) -> None:
        state = MazeUpdate(MazeUpdateType.WALL_REMOVED, start_cell, end_cell)
        super().on_state_changed(state)

    def generate(self, maze: 'Maze') -> None:
        self.maze = maze
        self.generate_maze()
        self.maze = None

    @abc.abstractmethod
    def generate_maze(self) -> None:
        raise NotImplemented


class RandomDepthFirstSearchGenerator(MazeGenerator):
    # def recursive_backtrack(maze, row=0, column=0):
    #     cell = maze[row, column]
    #     for neighbor in maze.neighbors(row, column):
    #         if not neighbor.open_walls:
    #             maze.open_wall(cell, neighbor)
    #             recursive_backtrack(maze, neighbor.row, neighbor.column)

    def __init__(self, event_listener: Optional[Callable[[MazeUpdate], None]] = None) -> None:
        super().__init__(event_listener)
        self.prev_cells = {}

    def cell_visitor(self, cell: Cell) -> None:
        if cell in self.prev_cells:
            self.maze.open_wall(self.prev_cells[cell], cell)
            self.on_wall_removed(self.prev_cells[cell], cell)
        for neighbor in self.maze.neighbors(*cell.coordinates):
            if not neighbor.open_walls:
                self.prev_cells[neighbor] = cell

    def generate_maze(self) -> None:
        self.maze.depth_first_search(0, 0, self.cell_visitor)
