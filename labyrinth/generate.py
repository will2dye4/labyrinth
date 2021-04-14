from dataclasses import dataclass
from enum import Enum
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


class MazeGenerator(abc.ABC, EventDispatcher):

    def __init__(self, event_listener=None):
        super().__init__(event_listener=event_listener)
        self.maze = None

    def on_wall_removed(self, start_cell, end_cell):
        state = MazeUpdate(MazeUpdateType.WALL_REMOVED, start_cell, end_cell)
        super().on_state_changed(state)

    def generate(self, maze):
        self.maze = maze
        self.generate_maze()
        self.maze = None

    @abc.abstractmethod
    def generate_maze(self):
        raise NotImplemented


class RandomDepthFirstSearchGenerator(MazeGenerator):
    # def recursive_backtrack(maze, row=0, column=0):
    #     cell = maze[row, column]
    #     for neighbor in maze.neighbors(row, column):
    #         if not neighbor.open_walls:
    #             maze.open_wall(cell, neighbor)
    #             recursive_backtrack(maze, neighbor.row, neighbor.column)

    def __init__(self, event_listener=None):
        super().__init__(event_listener)
        self.prev_cells = {}

    def cell_visitor(self, cell):
        if cell in self.prev_cells:
            self.maze.open_wall(self.prev_cells[cell], cell)
            self.on_wall_removed(self.prev_cells[cell], cell)
        for neighbor in self.maze.neighbors(*cell.coordinates):
            if not neighbor.open_walls:
                self.prev_cells[neighbor] = cell

    def generate_maze(self):
        self.maze.depth_first_search(0, 0, self.cell_visitor)
