"""Solve mazes using a depth-first search algorithm."""

from collections import defaultdict
from typing import List

from labyrinth.graph import Graph
from labyrinth.grid import Cell, Direction
from labyrinth.maze import Maze


class MazeSolver:
    """A MazeSolver is capable of solving simply connected mazes."""

    def __init__(self) -> None:
        """Initialize a MazeSolver."""
        self.maze = None
        self.junction_graph = None
        self.prev_cells = None

    def construct_junction_graph(self) -> Graph[Cell]:
        """Construct and return a graph representing all junctions in the maze."""
        if self.maze is None:
            raise ValueError('No current maze to construct a junction graph from!')

        junction_graph = Graph()
        visited = defaultdict(bool)

        def cell_visitor(cell: Cell) -> None:
            visited[cell] = True
            for neighbor in self.maze.neighbors(cell):
                direction = Direction.between(cell, neighbor)
                if direction in cell.open_walls and not visited[neighbor]:
                    while self.is_corridor_cell(neighbor):
                        neighbor = self.maze.neighbor(neighbor, direction)
                    junction_graph.add_vertex(cell)
                    junction_graph.add_vertex(neighbor)
                    junction_graph.add_edge(cell, neighbor)

        self.maze.depth_first_search(self.maze.start_cell, cell_visitor)
        return junction_graph

    @staticmethod
    def is_corridor_cell(cell: Cell) -> bool:
        """Return True if the given cell forms a corridor, False otherwise."""
        open_walls = list(cell.open_walls)
        return len(open_walls) == 2 and open_walls[0].opposite == open_walls[1]

    def is_in_solution(self, cell: Cell) -> bool:
        """Return True if the given cell is part of the solution to the maze, False otherwise."""
        while cell in self.prev_cells:
            cell = self.prev_cells[cell]
        return cell == self.maze.start_cell

    @staticmethod
    def junction_direction(start_junction: Cell, end_junction: Cell) -> Direction:
        """Return the direction between the given junction cells."""
        dx = end_junction.column - start_junction.column
        dy = end_junction.row - start_junction.row
        if dy == 0:
            return Direction.E if dx > 0 else Direction.W
        return Direction.S if dy > 0 else Direction.N

    def junction_visitor(self, cell: Cell) -> None:
        """Visitor function for the depth-first search algorithm."""
        for neighbor in self.junction_graph.neighbors(cell):
            direction = self.junction_direction(cell, neighbor)
            if direction in cell.open_walls and self.is_in_solution(neighbor):
                self.prev_cells[cell] = neighbor
                break

    def solve(self, maze: Maze) -> List[Cell]:
        """Find and return a path through the given maze."""
        self.maze = maze
        path = self.solve_maze()
        self.maze = None
        return path

    def solve_maze(self) -> List[Cell]:
        """Find and return a path through the current maze."""
        self.prev_cells = {}
        self.junction_graph = self.construct_junction_graph()
        self.junction_graph.depth_first_search(self.maze.start_cell, self.junction_visitor)

        end_cell = self.maze.end_cell
        path = [end_cell]
        prev_cell = end_cell
        cell = self.prev_cells.get(end_cell)

        while path[-1] != self.maze.start_cell:
            if Direction.between(prev_cell, cell) is None:
                # fill in corridors
                direction = self.junction_direction(prev_cell, cell)
                neighbor = self.maze.neighbor(prev_cell, direction)
                while neighbor != cell:
                    path.append(neighbor)
                    neighbor = self.maze.neighbor(neighbor, direction)
            path.append(cell)
            prev_cell = cell
            cell = self.prev_cells.get(cell)

        return list(reversed(path))


if __name__ == '__main__':
    maze = Maze()
    solver = MazeSolver()
    path = solver.solve(maze)
    print(maze)
    print(f'Solution: {[cell.coordinates for cell in path]}')
