#!/usr/bin/env python

from typing import List
import math
import random
import sys

from manim import *
from manim.__main__ import main

from labyrinth.grid import Direction
from labyrinth.maze import Maze
from labyrinth.solve import MazeSolver


def euclidean_distance(x0: float, y0: float, x1: float, y1: float) -> float:
    return math.sqrt((x1 - x0) ** 2 + (y1 - y0) ** 2)


def line_distance(x0: float, y0: float, line: Line) -> float:
    center_x, center_y, _ = line.get_center()
    return euclidean_distance(x0, y0, center_x, center_y)


class MazeScene(Scene):

    ANIMATION_RUN_TIME = 2

    NUM_COLUMNS = 5
    NUM_ROWS = NUM_COLUMNS

    SHOW_TREE = True

    START_COORDS = LEFT * 3 + UP * 3

    SCALE_FACTOR = 1

    VERTEX_OFFSET = 1.5
    VERTEX_RADIUS = 0.5

    def __init__(self) -> None:
        super().__init__()
        self.walls = []

        self.vertices = {}
        self.edges = {}

        self.maze = Maze(self.NUM_COLUMNS, self.NUM_ROWS)
        self.create_grid()
        self.create_graph()

    @property
    def vertex_offset(self) -> float:
        return self.VERTEX_OFFSET * self.SCALE_FACTOR

    @property
    def vertex_radius(self) -> float:
        return self.VERTEX_RADIUS * self.SCALE_FACTOR

    def create_grid(self) -> None:
        offset = 0.75
        top_left = self.START_COORDS + (UP * offset) + (LEFT * offset)
        top_right = top_left + (RIGHT * self.NUM_COLUMNS * self.vertex_offset)
        bottom_left = top_left + (DOWN * self.NUM_ROWS * self.vertex_offset)
        bottom_right = top_right + (DOWN * self.NUM_ROWS * self.vertex_offset)

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
                            start_coords = top_left + (RIGHT * column * self.vertex_offset) + (DOWN * (row + 1) * self.vertex_offset)
                            end_coords = start_coords + RIGHT * self.vertex_offset
                            self.walls.append(new_wall(start_coords, end_coords))
                        elif direction == Direction.E:
                            start_coords = top_left + (RIGHT * (column + 1) * self.vertex_offset) + (DOWN * row * self.vertex_offset)
                            end_coords = start_coords + DOWN * self.vertex_offset
                            self.walls.append(new_wall(start_coords, end_coords))

    def create_graph(self) -> None:
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
                    if self.SHOW_TREE:
                        prev_cell = self.maze[prev_coords]
                        if Direction.between(prev_cell, cell) in prev_cell.open_walls:
                            self.edges[(prev_coords, coords)] = edge
                    else:
                        self.edges[(prev_coords, coords)] = edge

    def create_vertex(self, row: int, column: int) -> Circle:
        coords = self.START_COORDS + (RIGHT * column * self.vertex_offset) + (DOWN * row * self.vertex_offset)
        vertex = Circle(radius=self.vertex_radius).move_to(coords)
        vertex.set_stroke(WHITE)
        vertex.set_fill(BLUE, opacity=0.5)
        self.vertices[row, column] = vertex
        return vertex

    def create_edge(self, start_vertex: Circle, end_vertex: Circle) -> Line:
        return Line(start_vertex.get_center(), end_vertex.get_center(), buff=self.vertex_radius)

    def get_edges_to_remove(self) -> List[Line]:
        edges = []
        for wall in self.maze.walls:
            start_cell, end_cell = wall
            direction = Direction.between(start_cell, end_cell)
            if direction not in start_cell.open_walls:
                edges.append(self.edges[((start_cell.row, start_cell.column), (end_cell.row, end_cell.column))])
        return edges

    def get_solution(self) -> List[Circle]:
        solver = MazeSolver()
        return [self.vertices[cell.row, cell.column] for cell in solver.solve(self.maze)]

    def play_all(self, *animations, lag_ratio: float = 1) -> None:
        self.play(AnimationGroup(*animations, lag_ratio=lag_ratio))

    def pause(self, duration: float = ANIMATION_RUN_TIME):
        self.wait(duration)

    def animate_grid_creation(self, style: str = 'distance_from_start', lag_ratio: float = 1) -> None:
        num_outer_walls = 4
        self.play(*[Create(wall, run_time=self.ANIMATION_RUN_TIME / 2) for wall in self.walls[:num_outer_walls]])

        inner_walls = self.walls[num_outer_walls:]
        if style == 'distance_from_center':
            inner_walls.sort(key=lambda l: line_distance(0, 0, l))
        elif style == 'distance_from_start':
            inner_walls.sort(key=lambda l: line_distance(self.START_COORDS[0], self.START_COORDS[1], l))
        elif style == 'random':
            random.shuffle(inner_walls)
        elif style != 'order':
            raise ValueError(f'Invalid style: {style}')

        self.play_all(*[Create(wall, run_time=self.ANIMATION_RUN_TIME / 10) for wall in inner_walls], lag_ratio=lag_ratio)

    def animate_graph_creation(self, lag_ratio: float = 0.1) -> None:
        self.play_all(*[FadeIn(vertex, run_time=self.ANIMATION_RUN_TIME / 4) for vertex in self.vertices.values()], lag_ratio=lag_ratio)
        self.play(*[Create(edge, run_time=self.ANIMATION_RUN_TIME) for edge in self.edges.values()])

    def animate_edge_removal(self, lag_ratio: float = 0, highlight: bool = True) -> None:
        edges = self.get_edges_to_remove()
        if highlight:
            self.play(*[edge.animate(run_time=self.ANIMATION_RUN_TIME / 2).set_stroke(color=RED) for edge in edges])
        self.play_all(*[Uncreate(edge, run_time=self.ANIMATION_RUN_TIME) for edge in edges], lag_ratio=lag_ratio)

    def animate_solution(self) -> None:
        self.play_all(*[vertex.animate(run_time=self.ANIMATION_RUN_TIME / 5).set_fill(GREEN, opacity=0.5) for vertex in self.get_solution()])

    def transform_grid_to_graph(self) -> None:
        grid_group = VGroup(*self.walls)
        graph_group = VGroup(*(list(self.vertices.values()) + list(self.edges.values())))
        self.play(ReplacementTransform(grid_group, graph_group, run_time=self.ANIMATION_RUN_TIME))


class GridToGraph(MazeScene):

    def construct(self) -> None:
        self.animate_grid_creation()
        self.pause()

        self.animate_graph_creation()
        self.pause()

        self.animate_solution()
        self.pause()


class GraphToGrid(MazeScene):

    SHOW_TREE = False

    def construct(self) -> None:
        self.animate_graph_creation()
        self.pause()

        self.animate_edge_removal()
        self.pause()

        self.animate_grid_creation(style='order')
        self.pause()

        self.animate_solution()
        self.pause()


class DrawGraph(MazeScene):

    NUM_COLUMNS = 10
    NUM_ROWS = NUM_COLUMNS

    SHOW_TREE = False

    START_COORDS = LEFT * 3 + UP * 3.3

    SCALE_FACTOR = 0.5

    def construct(self) -> None:
        self.animate_graph_creation(lag_ratio=0.01)
        self.pause()

        self.animate_edge_removal(lag_ratio=0.01)
        self.pause()

        self.animate_solution()
        self.pause()


class DrawMaze(MazeScene):

    NUM_COLUMNS = 10
    NUM_ROWS = NUM_COLUMNS

    SCALE_FACTOR = 0.5

    def construct(self) -> None:
        self.animate_grid_creation(lag_ratio=0.2)
        self.pause()


class TransformGridToGraph(MazeScene):

    def construct(self) -> None:
        self.animate_grid_creation(style='random', lag_ratio=0.2)
        self.pause()

        self.transform_grid_to_graph()
        self.pause()


class GraphBasics(MazeScene):

    def construct(self) -> None:
        vertices = [
            self.create_vertex(2, 1),
            self.create_vertex(1, 3),
            self.create_vertex(3, 3),
        ]

        edges = [
            self.create_edge(vertices[0], vertices[1]),
            self.create_edge(vertices[0], vertices[2]),
            self.create_edge(vertices[1], vertices[2]),
        ]

        vertices_label = Text('Vertices').move_to(UP * 2 + LEFT * 2)
        edges_label = Text('Edges').move_to(DOWN * 2 + LEFT * 2)

        self.play_all(*[FadeIn(vertex, run_time=self.ANIMATION_RUN_TIME) for vertex in vertices], lag_ratio=0.2)
        self.play_all(*[Create(edge, run_time=self.ANIMATION_RUN_TIME) for edge in edges], lag_ratio=0.5)
        self.pause()

        vertex_group = AnimationGroup(*[Indicate(vertex, run_time=self.ANIMATION_RUN_TIME) for vertex in vertices])
        self.play(Write(vertices_label), vertex_group)
        self.play(FadeOut(vertices_label))
        self.pause()

        edge_group = AnimationGroup(*[Indicate(edge, run_time=self.ANIMATION_RUN_TIME) for edge in edges])
        self.play(Write(edges_label), edge_group)
        self.play(FadeOut(edges_label))
        self.pause()


if __name__ == '__main__':
    scene_name = sys.argv[1] if len(sys.argv) > 1 else GraphToGrid.__name__
    sys.argv[1:] = ['-p', '-ql', __file__, scene_name]
    main()
