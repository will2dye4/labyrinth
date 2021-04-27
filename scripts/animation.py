#!/usr/bin/env python

from typing import Any, List, Optional
import math
import random
import sys

from manim import *
from manim.__main__ import main

from labyrinth.generate import (
    DepthFirstSearchGenerator,
    KruskalsGenerator,
    MazeGenerator,
    MazeUpdate,
    MazeUpdateType,
    PrimsGenerator,
    WilsonsGenerator,
)
from labyrinth.grid import Cell, Direction
from labyrinth.maze import Maze
from labyrinth.solve import MazeSolver


def euclidean_distance(x0: float, y0: float, x1: float, y1: float) -> float:
    return math.sqrt((x1 - x0) ** 2 + (y1 - y0) ** 2)


def line_distance(x0: float, y0: float, line: Line) -> float:
    center_x, center_y, _ = line.get_center()
    return euclidean_distance(x0, y0, center_x, center_y)


class MazeScene(Scene):

    ANIMATION_RUN_TIME = 2

    DASHED_LINES = False

    INITIAL_VERTEX_COLOR = BLUE

    NUM_COLUMNS = 5
    NUM_ROWS = NUM_COLUMNS

    SHOW_TREE = True

    START_COORDS = LEFT * 3 + UP * 3

    SCALE_FACTOR = 1

    VERTEX_OFFSET = 1.5
    VERTEX_RADIUS = 0.5

    def __init__(self, generator: Optional[MazeGenerator] = DepthFirstSearchGenerator()) -> None:
        super().__init__()
        self.walls = []

        self.vertices = {}
        self.edges = {}

        self.maze = Maze(width=self.NUM_COLUMNS, height=self.NUM_ROWS, generator=generator)
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
        vertex = Circle(radius=self.vertex_radius) \
            .move_to(coords) \
            .set_stroke(WHITE) \
            .set_fill(self.INITIAL_VERTEX_COLOR, opacity=1)
        self.vertices[row, column] = vertex
        return vertex

    def create_edge(self, start_vertex: Circle, end_vertex: Circle, dashed: Optional[bool] = None) -> Line:
        if dashed is None:
            dashed = self.DASHED_LINES
        line_type = DashedLine if dashed else Line
        return line_type(start_vertex.get_center(), end_vertex.get_center(), buff=self.vertex_radius)

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
        if not self.walls:
            self.create_grid()

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

    def animate_graph_destruction(self, lag_ratio: float = 0.1) -> None:
        vertex_group = AnimationGroup(*[FadeOut(vertex, run_time=self.ANIMATION_RUN_TIME / 4) for vertex in self.vertices.values()], lag_ratio=lag_ratio)
        edge_group = AnimationGroup(*[Uncreate(edge, run_time=self.ANIMATION_RUN_TIME / 2) for edge in self.edges.values()])
        self.play(vertex_group, edge_group)

    def animate_edge_removal(self, lag_ratio: float = 0, highlight: bool = True) -> None:
        edges = self.get_edges_to_remove()
        if highlight:
            self.play(*[edge.animate(run_time=self.ANIMATION_RUN_TIME / 2).set_stroke(color=RED) for edge in edges])
        self.play_all(*[Uncreate(edge, run_time=self.ANIMATION_RUN_TIME) for edge in edges], lag_ratio=lag_ratio)

    def animate_solution(self) -> None:
        self.play_all(*[vertex.animate(run_time=self.ANIMATION_RUN_TIME / 5).set_fill(GREEN, opacity=1) for vertex in self.get_solution()])

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


class MazeGenerationScene(MazeScene):

    DASHED_LINES = True

    FRONTIER_COLOR = GREEN
    GENERATE_PATH_COLOR = ORANGE
    INITIAL_VERTEX_COLOR = GRAY
    VERTEX_COLOR = DARK_BLUE

    GENERATOR_TYPE = DepthFirstSearchGenerator

    SHOW_TREE = False

    def __init__(self) -> None:
        super().__init__(generator=None)
        self.generator = self.GENERATOR_TYPE(event_listener=self.update_maze)
        self.path = []

    def get_fill_cell_animation(self, cell: Cell, color: Any) -> Animation:
        return self.vertices[cell.row, cell.column] \
            .animate(run_time=self.ANIMATION_RUN_TIME / 5) \
            .set_fill(color, opacity=1)

    def clear_path(self) -> None:
        if self.path:
            self.play(*[self.get_fill_cell_animation(cell, self.VERTEX_COLOR) for cell in self.path])
            self.path.clear()

    def fill_cell(self, cell: Cell, color: Any) -> None:
        self.play(self.get_fill_cell_animation(cell, color))

    def clear_cell(self, cell: Cell) -> None:
        self.fill_cell(cell, self.VERTEX_COLOR)

    def remove_wall(self, start_cell: Cell, end_cell: Cell) -> None:
        start_coords = (start_cell.row, start_cell.column)
        end_coords = (end_cell.row, end_cell.column)

        if (start_coords, end_coords) not in self.edges:
            start_coords, end_coords = end_coords, start_coords

        cells = (start_coords, end_coords)
        old_edge = self.edges[cells]
        new_edge = self.create_edge(self.vertices[start_coords], self.vertices[end_coords], dashed=False)
        self.edges[cells] = new_edge
        self.play(ReplacementTransform(old_edge, new_edge, run_time=self.ANIMATION_RUN_TIME / 5))

    def remove_edge(self, start_cell: Cell, end_cell: Cell) -> None:
        start_coords = (start_cell.row, start_cell.column)
        end_coords = (end_cell.row, end_cell.column)

        if (start_coords, end_coords) not in self.edges:
            start_coords, end_coords = end_coords, start_coords

        cells = (start_coords, end_coords)
        edge = self.edges.pop(cells)
        self.play(Uncreate(edge, run_time=self.ANIMATION_RUN_TIME / 5))

    def update_maze(self, state: MazeUpdate) -> None:
        if state.type == MazeUpdateType.WALL_REMOVED:
            if not self.path or state.start_cell != self.path[-1]:
                self.clear_path()
                self.path.append(state.start_cell)
                self.fill_cell(state.start_cell, self.GENERATE_PATH_COLOR)
            self.remove_wall(state.start_cell, state.end_cell)
            self.path.append(state.end_cell)
            self.fill_cell(state.end_cell, self.GENERATE_PATH_COLOR)
        elif state.type == MazeUpdateType.CELL_MARKED:
            self.clear_cell(state.start_cell)
            self.play(*[self.get_fill_cell_animation(cell, self.FRONTIER_COLOR) for cell in state.new_frontier_cells])
        elif state.type == MazeUpdateType.EDGE_REMOVED:
            self.clear_path()
            self.remove_edge(state.start_cell, state.end_cell)

        if state.type == MazeUpdateType.WALL_REMOVED:
            self.pause(self.ANIMATION_RUN_TIME / 10)

    def animate_maze_generation(self) -> None:
        self.clear_path()
        self.generator.generate(self.maze)
        self.clear_path()

    def construct(self):
        self.animate_graph_creation()
        self.pause()

        self.animate_maze_generation()
        self.pause()

        self.animate_edge_removal()
        self.pause()

        self.animate_grid_creation(style='order')
        self.pause()

        self.animate_graph_destruction()
        self.pause()


class DepthFirstSearchMazeGenerationScene(MazeGenerationScene):

    GENERATOR_TYPE = DepthFirstSearchGenerator


class KruskalsMazeGenerationScene(MazeGenerationScene):

    GENERATOR_TYPE = KruskalsGenerator

    def animate_edge_removal(self, lag_ratio: float = 0, highlight: bool = True) -> None:
        pass


class PrimsMazeGenerationScene(MazeGenerationScene):

    GENERATOR_TYPE = PrimsGenerator


class WilsonsMazeGenerationScene(MazeGenerationScene):

    GENERATOR_TYPE = WilsonsGenerator


if __name__ == '__main__':
    scene_name = sys.argv[1] if len(sys.argv) > 1 else GraphToGrid.__name__
    sys.argv[1:] = ['-p', '-ql', __file__, scene_name]
    main()
