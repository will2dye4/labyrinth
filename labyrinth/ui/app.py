"""Graphical user interface for the labyrinth program."""

from typing import Optional, Set, Tuple, Type
import time
import tkinter as tk

from labyrinth.generate import (
    DepthFirstSearchGenerator,
    KruskalsGenerator,
    MazeGenerator,
    MazeUpdateType,
    PrimsGenerator,
    WilsonsGenerator,
)
from labyrinth.grid import Cell, Direction
from labyrinth.maze import Maze
from labyrinth.render import MazeRenderer
from labyrinth.solve import MazeSolver
from labyrinth.ui.colors import (
    BACKGROUND_COLOR,
    CELL_BACKGROUND_COLOR,
    GENERATE_PATH_COLOR,
    FRONTIER_COLOR,
    INITIAL_CELL_COLOR,
    PATH_COLOR,
    VERTEX_COLOR,
)
from labyrinth.ui.common import Frame, Label, LEFT_CLICK, MOTION
from labyrinth.ui.menu import DisplayMode, MazeAppMenu, SizeCategory
from labyrinth.utils.abc import override


class MazeApp(Frame, MazeRenderer):
    """Class containing state and graphics elements for rendering the UI."""

    BORDER_WIDTH = 4
    BORDER_OFFSET = BORDER_WIDTH * 2

    DEFAULT_SIZE = SizeCategory.SMALL
    DEFAULT_DISPLAY_MODE = DisplayMode.GRID
    DEFAULT_GENERATOR = DepthFirstSearchGenerator

    DELAY_EVENT_TYPES = {MazeUpdateType.START_CELL_CHOSEN, MazeUpdateType.CELL_MARKED, MazeUpdateType.WALL_REMOVED}

    SUPPORTED_GENERATORS = {
        DepthFirstSearchGenerator: "Depth First Search",
        KruskalsGenerator: "Kruskal's Algorithm",
        PrimsGenerator: "Prim's Algorithm",
        WilsonsGenerator: "Wilson's Algorithm",
    }

    TICK_DELAY_MILLIS = 500

    def __init__(self, master: tk.Tk = None, width: int = 10, height: int = 10,
                 generator: Optional[MazeGenerator] = None, size_category: Optional[SizeCategory] = None,
                 validate_moves: bool = True) -> None:
        """Initialize a MazeApp instance."""
        if master is None:
            master = tk.Tk()
            master.title('Maze Generator')

        super().__init__(master)

        self.width = width
        self.height = height
        self.validate_moves = validate_moves

        self.generating_maze = False
        self.drawing_path = False
        self.using_dialog_box = False
        self.solving_maze = False
        self.maze_generated = False
        self._generator = generator
        self.solver = MazeSolver()
        self.menu = None
        self.maze = None
        self.generation_start_cell = None
        self.frontier_cells = set()
        self.path = []

        window = self.winfo_toplevel()
        window.configure(bg=BACKGROUND_COLOR)
        window.minsize(width=700, height=100)

        self.pack()
        canvas_frame = Frame()
        canvas_frame.pack(side='left')
        self.create_horizontal_spacer()
        self.menu = MazeAppMenu(self, size_category=size_category)
        self.canvas = self.create_canvas(canvas_frame)
        self.stats = self.create_stats_display(canvas_frame)
        self.menu.pack(side='left')

        self.start_time = None
        self.end_time = None
        self.generate_new_maze(generate=False)

    @property
    def cell_width(self) -> int:
        """Return the current cell width."""
        size = self.DEFAULT_SIZE if self.menu is None else self.menu.size_category
        return size.value[0]

    @property
    def cell_height(self) -> int:
        """Return the current cell height."""
        return self.cell_width

    @property
    def canvas_width(self) -> int:
        """Return the current canvas width."""
        return self.cell_width * self.width + self.BORDER_OFFSET

    @property
    def canvas_height(self) -> int:
        """Return the current canvas height."""
        return self.cell_height * self.height + self.BORDER_OFFSET

    @property
    def vertex_radius(self) -> int:
        """Return the current vertex radius."""
        size = self.DEFAULT_SIZE if self.menu is None else self.menu.size_category
        return size.value[1]

    @property
    def vertex_diameter(self) -> int:
        """Return the current vertex diameter."""
        return self.vertex_radius * 2

    @property
    def generator_type(self) -> Type[MazeGenerator]:
        if self.menu is not None and self.menu.generator_type is not None:
            return self.menu.generator_type
        if self._generator is not None:
            return self._generator.__class__
        return self.DEFAULT_GENERATOR

    @property
    def generator(self) -> MazeGenerator:
        """Return an instance of a MazeGenerator subclass to use for generating mazes."""
        if self._generator is None or self._generator.__class__ != self.generator_type:
            self._generator = self.generator_type()
        return self._generator

    @property
    def display_mode(self) -> DisplayMode:
        return self.DEFAULT_DISPLAY_MODE if self.menu is None else self.menu.display_mode

    @property
    def is_solved(self) -> bool:
        """Return True if the current maze is solved, False otherwise."""
        return self.path and (self.path[-1].row, self.path[-1].column) == (self.height - 1, self.width - 1)

    @property
    def elapsed_time(self) -> float:
        """Return the amount of time elapsed since the current maze was fully generated."""
        if self.start_time is not None:
            end_time = self.end_time or time.time()
            return end_time - self.start_time
        return 0

    def create_canvas(self, parent: Frame) -> tk.Canvas:
        """Create and return a graphics canvas representing the grid of cells in the maze."""
        canvas = tk.Canvas(parent, width=self.canvas_width, height=self.canvas_height, borderwidth=0,
                           bg=CELL_BACKGROUND_COLOR)
        canvas.bind(LEFT_CLICK, self.click_handler)
        canvas.bind(MOTION, self.motion_handler)
        canvas.pack(side='top')
        return canvas

    def refresh_canvas(self) -> None:
        """Refresh the canvas in response to maze size changes."""
        if self.width != self.maze.width or self.height != self.maze.height:
            self.generate_new_maze(generate=False)
        if self.canvas_width != self.canvas['width'] or self.canvas_height != self.canvas['height']:
            self.canvas.configure(width=self.canvas_width, height=self.canvas_height)
            self.display_maze()

    @staticmethod
    def create_stats_display(parent: Frame) -> Label:
        """Create and return a graphics element containing statistics about the current maze."""
        stats = Label(parent, padx=10, pady=10, width=62)
        stats.pack(side='top')
        return stats

    @staticmethod
    def create_horizontal_spacer() -> None:
        Label(width=2).pack(side='left')

    @staticmethod
    def get_wall_tag(row: int, column: int, direction: Direction) -> str:
        """Return a formatted tag suitable for use when drawing maze walls on the canvas."""
        return f'{row}_{column}_{direction.name}'

    @staticmethod
    def get_cell_tag(row: int, column: int) -> str:
        """Return a formatted tag suitable for use when drawing frontier cells on the canvas."""
        return f'{row}_{column}'

    def click_handler(self, event: tk.Event) -> None:
        """Event handler for click events on the canvas."""
        if self.generating_maze or self.solving_maze:
            return
        if self.drawing_path:
            self.drawing_path = False
            if self.end_time is None and self.is_solved:
                self.end_time = time.time()
        else:
            coordinates = self.get_selected_cell_coordinates(event)
            self.select_cell(*coordinates)
            self.drawing_path = True

    def motion_handler(self, event: tk.Event) -> None:
        """Event handler for mouse motion events on the canvas."""
        if self.generating_maze or self.solving_maze:
            return
        if self.drawing_path:
            coordinates = self.get_selected_cell_coordinates(event)
            if self.path and coordinates != self.path[-1].coordinates:
                if len(self.path) > 1 and coordinates == self.path[-2].coordinates:
                    # moved back one, deselect the most recent cell
                    self.select_cell(*self.path[-1].coordinates)
                else:
                    self.select_cell(*coordinates)

    def generate_new_maze(self, event: Optional[tk.Event] = None, generate: bool = True) -> None:
        """Create a new blank maze, and optionally generate paths through it."""
        if self.generating_maze or self.solving_maze:
            return

        self.clear_path()
        self.frontier_cells.clear()
        self.generation_start_cell = None
        self.maze = Maze(self.width, self.height, generator=None)
        self.maze_generated = False
        self.start_time = None
        self.display_maze()

        if generate:
            self.generate_current_maze()

    def generate_current_maze(self, event: Optional[tk.Event] = None) -> None:
        """Generate paths through the current maze."""
        if self.menu.animate:
            self.generator.event_listener = self.update_maze
        else:
            self.generator.event_listener = None

        self.generating_maze = True
        self.clear_path()
        self.generator.generate(self.maze)
        self.clear_path()
        self.generating_maze = False
        self.maze_generated = True

        if not self.menu.animate or self.display_mode == DisplayMode.GRAPH:
            self.display_maze()

        self.start_time = time.time()
        self.end_time = None

    def create_maze_grid(self) -> None:
        """Populate the canvas with all of the walls in the current maze."""
        for obj in self.canvas.find_all():
            self.canvas.delete(obj)

        for row in range(self.height):
            for column in range(self.width):
                cell = self.maze[row, column]
                x0 = self.cell_width * column + self.BORDER_OFFSET
                y0 = self.cell_height * row + self.BORDER_OFFSET
                x1 = x0 + self.cell_width
                y1 = y0 + self.cell_height
                directions = {
                    Direction.N: ((x0, y0, x1, y0), lambda r, c: r == 0),
                    Direction.S: ((x0, y1, x1, y1), lambda r, c: r == self.height - 1),
                    Direction.E: ((x1, y0, x1, y1), lambda r, c: c == self.width - 1),
                    Direction.W: ((x0, y0, x0, y1), lambda r, c: c == 0),
                }
                for direction in directions:
                    coordinates, width_predicate = directions[direction]
                    width = 1
                    if direction not in cell.open_walls:
                        if width_predicate(row, column):
                            width = self.BORDER_WIDTH
                        wall_tag = self.get_wall_tag(row, column, direction)
                        self.canvas.create_line(*coordinates, width=width, fill=BACKGROUND_COLOR, tags=wall_tag)
                    cell_tag = self.get_cell_tag(row, column)
                    if cell in self.frontier_cells:
                        self.fill_cell(cell, FRONTIER_COLOR, cell_tag)
                    elif cell in self.path:
                        color = GENERATE_PATH_COLOR if self.generating_maze else PATH_COLOR
                        self.fill_cell(cell, color)
                    elif not cell.open_walls and cell != self.generation_start_cell:
                        self.fill_cell(cell, INITIAL_CELL_COLOR, cell_tag)

    def create_maze_graph(self) -> None:
        """Populate the canvas with a visual representation of the graph underlying the current maze."""
        for obj in self.canvas.find_all():
            self.canvas.delete(obj)

        for row in range(self.height):
            for column in range(self.width):
                cell = self.maze[row, column]
                cell_x0 = self.cell_width * column + self.BORDER_OFFSET
                cell_y0 = self.cell_height * row + self.BORDER_OFFSET
                pad_x = (self.cell_width - self.vertex_diameter) // 2
                pad_y = (self.cell_height - self.vertex_diameter) // 2
                vertex_x0 = cell_x0 + pad_x
                vertex_y0 = cell_y0 + pad_y
                vertex_x1 = vertex_x0 + self.vertex_diameter
                vertex_y1 = vertex_y0 + self.vertex_diameter
                tag = self.get_cell_tag(*cell.coordinates)
                if self.generating_maze and cell == self.generation_start_cell:
                    color = VERTEX_COLOR
                elif cell in self.frontier_cells:
                    color = FRONTIER_COLOR
                elif cell.open_walls:
                    if cell in self.path:
                        color = GENERATE_PATH_COLOR if self.generating_maze else PATH_COLOR
                    else:
                        color = VERTEX_COLOR
                else:
                    color = INITIAL_CELL_COLOR
                self.canvas.create_oval(vertex_x0, vertex_y0, vertex_x1, vertex_y1, fill=color, tags=tag)
                for direction in {Direction.E, Direction.S}:
                    neighbor = self.maze.neighbor(cell, direction)
                    if (self.maze_generated and direction in cell.open_walls) or (not self.maze_generated and neighbor):
                        dash = () if self.maze_generated or direction in cell.open_walls else (2,)
                        if direction == Direction.E:
                            edge_x0 = vertex_x1
                            edge_y0 = vertex_y0 + self.vertex_radius
                            edge_x1 = 1 + edge_x0 + pad_x * 2
                            edge_y1 = edge_y0
                        elif direction == Direction.S:
                            edge_x0 = vertex_x0 + self.vertex_radius
                            edge_y0 = vertex_y1
                            edge_x1 = edge_x0
                            edge_y1 = 1 + edge_y0 + pad_y * 2
                        else:
                            raise ValueError(f'Unexpected direction {direction.name}!')
                        tag = self.get_wall_tag(cell.row, cell.column, direction)
                        opposite_tag = self.get_wall_tag(neighbor.row, neighbor.column, direction.opposite)
                        self.canvas.create_line(edge_x0, edge_y0, edge_x1, edge_y1, width=2, fill=BACKGROUND_COLOR,
                                                dash=dash, tags=(tag, opposite_tag))

    def display_maze(self) -> None:
        """Display the current maze on the canvas."""
        if self.display_mode == DisplayMode.GRID:
            self.create_maze_grid()
        else:
            self.create_maze_graph()

    def solve_maze(self, event: Optional[tk.Event] = None) -> None:
        """Solve the current maze."""
        if self.solving_maze or self.generating_maze or self.using_dialog_box or not self.maze.start_cell.open_walls:
            return

        self.solving_maze = True
        self.start_time = None
        self.clear_path()
        path = self.solver.solve(self.maze)
        for cell in path:
            self.path.append(cell)
            self.fill_cell(cell, PATH_COLOR)
            if self.menu.animate:
                self.canvas.update()
                time.sleep(self.menu.delay_millis / 1000)
        self.solving_maze = False

    def get_selected_cell_coordinates(self, event: tk.Event) -> Tuple[int, int]:
        """Return the coordinates of the selected cell based on the (x, y) position of the given event."""
        row = max(0, min(event.y // self.cell_height, self.height - 1))
        column = max(0, min(event.x // self.cell_width, self.width - 1))
        return row, column

    def select_cell(self, row: int, column: int) -> None:
        """Select (or deselect) the maze cell at the given row and column, toggling its color and updating the path."""
        clicked_cell = self.maze[row, column]
        add = True

        if not self.path:
            if self.validate_moves and clicked_cell != self.maze.start_cell:
                # print('Path must start at (0, 0)')
                return
        else:
            last_cell = self.path[-1]
            if clicked_cell in self.path:
                if self.validate_moves and clicked_cell != last_cell:
                    # print('Can only undo the last move')
                    return
                add = False
            elif self.validate_moves and clicked_cell not in self.maze.neighbors(last_cell):
                # print('Path must be continuous')
                return
            elif self.validate_moves:
                direction = Direction.between(last_cell, clicked_cell)
                if direction not in last_cell.open_walls:
                    # print(f'Invalid move (through {direction.name} wall)')
                    return

        if add:
            self.fill_cell(clicked_cell, PATH_COLOR)
            self.path.append(clicked_cell)
        else:
            self.clear_cell(clicked_cell)
            self.path = self.path[:-1]

    def fill_cell(self, cell: Cell, color: str, tag: str = 'path'):
        """Fill the given cell in the maze with the given color."""
        if self.display_mode == DisplayMode.GRID:
            row_offset = 2 if cell.row in {0, self.height - 1} else 1
            column_offset = 2 if cell.column in {0, self.width - 1} else 1
            x0 = self.cell_width * cell.column + self.BORDER_OFFSET + column_offset
            y0 = self.cell_height * cell.row + self.BORDER_OFFSET + row_offset
            x1 = x0 + self.cell_width - (2 if cell.column == self.width - 1 else 1) * column_offset
            y1 = y0 + self.cell_height - (2 if cell.row == self.height - 1 else 1) * row_offset
            self.canvas.create_rectangle(x0, y0, x1, y1, fill=color, width=0, tags=tag)
        else:
            self.canvas.itemconfigure(self.get_cell_tag(*cell.coordinates), fill=color)

    def clear_cell(self, cell: Cell) -> None:
        """Reset the given cell back to its default state on the canvas."""
        tag = self.get_cell_tag(*cell.coordinates)
        if self.display_mode == DisplayMode.GRID:
            self.canvas.delete(tag)
            self.fill_cell(cell, CELL_BACKGROUND_COLOR)
        else:
            self.canvas.itemconfigure(tag, fill=VERTEX_COLOR)

    @override
    def set_start_cell(self, cell: Cell) -> None:
        """Update the cell where the maze generator chose to start."""
        self.generation_start_cell = cell
        self.clear_cell(cell)

    @override
    def clear_path(self) -> None:
        """Clear the current path of highlighted cells in the maze."""
        if self.display_mode == DisplayMode.GRID:
            self.canvas.delete('path')
        else:
            for cell in self.path:
                self.canvas.itemconfigure(self.get_cell_tag(*cell.coordinates), fill=VERTEX_COLOR)
        self.path.clear()

    @override
    def add_cell_to_generated_path(self, cell: Cell) -> None:
        """Fill the given cell with the 'generate path' color."""
        if cell in self.frontier_cells:
            self.frontier_cells.remove(cell)
        self.path.append(cell)
        self.fill_cell(cell, GENERATE_PATH_COLOR)

    @override
    def get_end_of_current_path(self) -> Optional[Cell]:
        """Return the cell at the end of the path currently being generated, if any."""
        return self.path[-1] if self.path else None

    @override
    def add_cells_to_frontier(self, frontier_cells: Set[Cell]) -> None:
        """Fill the given frontier cells with the frontier color and add them to the set of frontier cells."""
        if frontier_cells:
            self.frontier_cells |= frontier_cells
            for cell in frontier_cells:
                self.fill_cell(cell, FRONTIER_COLOR, tag=self.get_cell_tag(*cell.coordinates))

    @override
    def remove_wall(self, start_cell: Cell, end_cell: Cell) -> None:
        """Remove the wall between the given start cell and end cell, also clearing any color from the cells."""
        direction = Direction.between(start_cell, end_cell)
        wall_tag = self.get_wall_tag(start_cell.row, start_cell.column, direction)
        opposite_wall_tag = self.get_wall_tag(end_cell.row, end_cell.column, direction.opposite)
        if self.display_mode == DisplayMode.GRID:
            self.canvas.delete(wall_tag)
            self.canvas.delete(opposite_wall_tag)
            start_cell_tag = self.get_cell_tag(start_cell.row, start_cell.column)
            self.canvas.delete(start_cell_tag)
            end_cell_tag = self.get_cell_tag(end_cell.row, end_cell.column)
            self.canvas.delete(end_cell_tag)
        else:
            for tag in {wall_tag, opposite_wall_tag}:
                self.canvas.itemconfigure(tag, dash=())

    @override
    def remove_edge(self, start_cell: Cell, end_cell: Cell) -> None:
        """Remove the edge between the given start cell and end cell (if rendering the maze as a graph)."""
        if self.display_mode == DisplayMode.GRAPH:
            direction = Direction.between(start_cell, end_cell)
            tag = self.get_wall_tag(start_cell.row, start_cell.column, direction)
            self.canvas.delete(tag)
            opposite_tag = self.get_wall_tag(end_cell.row, end_cell.column, direction.opposite)
            self.canvas.delete(opposite_tag)

    @override
    def delay(self) -> None:
        """Delay rendering to allow the user to see the latest updates."""
        time.sleep(self.menu.delay_millis / 1000)

    @override
    def refresh(self) -> None:
        """Refresh the canvas after applying updates."""
        self.canvas.update()

    def tick(self) -> None:
        """Update the UI on a regular interval."""
        self.stats['text'] = (f'Maze Size: {self.width} x {self.height}         '
                              f'Current Path Length: {len(self.path)}        '
                              f'Elapsed Time: {int(self.elapsed_time)} sec')
        self.after(self.TICK_DELAY_MILLIS, self.tick)

    def run(self) -> None:
        """Run the GUI."""
        self.tick()
        super().mainloop()


if __name__ == '__main__':
    MazeApp(width=25, height=25).run()
