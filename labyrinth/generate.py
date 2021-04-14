import abc


class MazeGenerator(abc.ABC):

    def __init__(self, maze):
        self.maze = maze

    @abc.abstractmethod
    def generate(self):
        raise NotImplemented


class RandomDepthFirstSearchGenerator(MazeGenerator):
    # def recursive_backtrack(maze, row=0, column=0):
    #     cell = maze[row, column]
    #     for neighbor in maze.neighbors(row, column):
    #         if not neighbor.open_walls:
    #             maze.open_wall(cell, neighbor)
    #             recursive_backtrack(maze, neighbor.row, neighbor.column)

    def __init__(self, maze):
        super().__init__(maze)
        self.prev_cells = {}

    def cell_visitor(self, cell):
        if cell in self.prev_cells:
            self.maze.open_wall(self.prev_cells[cell], cell)
        for neighbor in self.maze.neighbors(*cell.coordinates):
            if not neighbor.open_walls:
                self.prev_cells[neighbor] = cell

    def generate(self):
        self.maze.depth_first_search(0, 0, self.cell_visitor)
