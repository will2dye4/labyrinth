#!/usr/bin/env python

from manim import *

from labyrinth.grid import Direction
from labyrinth.maze import Maze
from labyrinth.solve import MazeSolver


class MazeScene(Scene):

    ANIMATION_RUN_TIME = 1

    NUM_COLUMNS = 5
    NUM_ROWS = NUM_COLUMNS

    START_COORDS = LEFT * 3 + UP * 3

    VERTEX_OFFSET = 1.5
    VERTEX_RADIUS = 0.5

    def __init__(self):
        super().__init__()
        self.walls = []

        self.vertices = {}
        self.edges = {}

        self.maze = Maze(self.NUM_COLUMNS, self.NUM_ROWS)

    def create_grid(self):
        offset = 0.75
        top_left = self.START_COORDS + (UP * offset) + (LEFT * offset)
        top_right = top_left + (RIGHT * self.NUM_COLUMNS * self.VERTEX_OFFSET)
        bottom_left = top_left + (DOWN * self.NUM_ROWS * self.VERTEX_OFFSET)
        bottom_right = top_right + (DOWN * self.NUM_ROWS * self.VERTEX_OFFSET)

        def new_wall(start, end):
            wall = Line(start, end)
            wall.set_stroke(color=GOLD)
            return wall

        self.walls.append(new_wall(top_left, top_right))
        self.walls.append(new_wall(top_left, bottom_left))
        self.walls.append(new_wall(bottom_left, bottom_right))
        self.walls.append(new_wall(top_right, bottom_right))

        for row in range(self.NUM_ROWS):
            for column in range(self.NUM_COLUMNS):
                cell = self.maze[row, column]
                for neighbor in self.maze.neighbors(cell):
                    direction = Direction.between(cell, neighbor)
                    if direction not in cell.open_walls:
                        if direction == Direction.S:
                            start_coords = top_left + (RIGHT * column * self.VERTEX_OFFSET) + (DOWN * (row + 1) * self.VERTEX_OFFSET)
                            end_coords = start_coords + RIGHT * self.VERTEX_OFFSET
                            self.walls.append(new_wall(start_coords, end_coords))
                        elif direction == Direction.E:
                            start_coords = top_left + (RIGHT * (column + 1) * self.VERTEX_OFFSET) + (DOWN * row * self.VERTEX_OFFSET)
                            end_coords = start_coords + DOWN * self.VERTEX_OFFSET
                            self.walls.append(new_wall(start_coords, end_coords))

    def create_graph(self, as_tree=True):
        for row in range(self.NUM_ROWS):
            for column in range(self.NUM_COLUMNS):
                coords = (row, column)
                vertex = self.create_vertex(*coords)
                edges = []
                if row > 0:
                    prev_coords = (row - 1, column)
                    edges.append((self.create_edge(self.vertices[prev_coords], vertex), prev_coords))
                if column > 0:
                    prev_coords = (row, column - 1)
                    edges.append((self.create_edge(self.vertices[prev_coords], vertex), prev_coords))
                for edge, prev_coords in edges:
                    cell = self.maze[coords]
                    if as_tree:
                        prev_cell = self.maze[prev_coords]
                        if Direction.between(prev_cell, cell) in prev_cell.open_walls:
                            self.edges[(prev_coords, coords)] = edge
                    else:
                        self.edges[(prev_coords, coords)] = edge

    def create_vertex(self, row, column):
        coords = self.START_COORDS + (RIGHT * column * self.VERTEX_OFFSET) + (DOWN * row * self.VERTEX_OFFSET)
        vertex = Circle(radius=self.VERTEX_RADIUS).move_to(coords)
        vertex.set_stroke(WHITE)
        vertex.set_fill(BLUE, opacity=0.5)
        self.vertices[row, column] = vertex
        return vertex

    def create_edge(self, start_vertex, end_vertex):
        edge = Line(start_vertex.get_center(), end_vertex.get_center(), buff=self.VERTEX_RADIUS)
        return edge

    def get_edges_to_remove(self):
        edges = []
        for wall in self.maze.walls:
            start_cell, end_cell = wall
            direction = Direction.between(start_cell, end_cell)
            if direction not in start_cell.open_walls:
                edges.append(self.edges[((start_cell.row, start_cell.column), (end_cell.row, end_cell.column))])
        return edges

    def get_solution(self):
        solver = MazeSolver()
        return [self.vertices[cell.row, cell.column] for cell in solver.solve(self.maze)]


class GridToGraph(MazeScene):

    def construct(self):
        self.create_grid()
        self.create_graph()

        for wall in self.walls:
            self.play(Create(wall, run_time=self.ANIMATION_RUN_TIME / 10))
        self.wait(self.ANIMATION_RUN_TIME)

        self.play(*[Create(vertex, run_time=self.ANIMATION_RUN_TIME) for vertex in self.vertices.values()])
        self.play(*[Create(edge, run_time=self.ANIMATION_RUN_TIME) for edge in self.edges.values()])

        self.wait(self.ANIMATION_RUN_TIME)

        for vertex in self.get_solution():
            self.play(vertex.animate(run_time=self.ANIMATION_RUN_TIME / 5).set_fill(GREEN, opacity=0.5))
        self.wait(self.ANIMATION_RUN_TIME)


class GraphToGrid(MazeScene):

    def construct(self):
        self.create_grid()
        self.create_graph(as_tree=False)

        self.play(*[Create(vertex, run_time=self.ANIMATION_RUN_TIME) for vertex in self.vertices.values()])
        self.play(*[Create(edge, run_time=self.ANIMATION_RUN_TIME) for edge in self.edges.values()])

        self.wait(self.ANIMATION_RUN_TIME)

        self.play(*[Uncreate(edge, run_time=self.ANIMATION_RUN_TIME) for edge in self.get_edges_to_remove()])
        self.wait(self.ANIMATION_RUN_TIME)

        for wall in self.walls:
            self.play(Create(wall, run_time=self.ANIMATION_RUN_TIME / 10))
        self.wait(self.ANIMATION_RUN_TIME)

        for vertex in self.get_solution():
            self.play(vertex.animate(run_time=self.ANIMATION_RUN_TIME / 5).set_fill(GREEN, opacity=0.5))
        self.wait(self.ANIMATION_RUN_TIME)


if __name__ == '__main__':
    from manim.__main__ import main
    import sys
    sys.argv = ['-p', '-ql', __file__, GraphToGrid.__name__]
    main()
