"""Graphical user interface for the labyrinth program."""

from typing import Optional, Tuple, Type
import time
import tkinter as tk

from labyrinth.generate import (
    MazeGenerator,
    MazeUpdate,
    MazeUpdateType,
    PrimsGenerator,
    RandomDepthFirstSearchGenerator,
)
from labyrinth.grid import Cell
from labyrinth.maze import Direction, Maze


class MazeApp(tk.Frame):
    """Class containing state and graphics elements for rendering the UI."""

    BORDER_WIDTH = 4
    BORDER_OFFSET = BORDER_WIDTH * 2

    CELL_WIDTH = 35
    CELL_HEIGHT = CELL_WIDTH

    FONT = ('Arial', 20)

    BACKGROUND_COLOR = '#444444'
    FRONTIER_COLOR = '#97F593'
    GENERATE_PATH_COLOR = '#F5A676'
    PATH_COLOR = '#C3E3F7'
    TEXT_COLOR = 'white'

    DEFAULT_STEP_DELAY_MILLIS = 50
    TICK_DELAY_MILLIS = 500

    DEFAULT_GENERATOR = RandomDepthFirstSearchGenerator
    SUPPORTED_GENERATORS = [PrimsGenerator, RandomDepthFirstSearchGenerator]

    def __init__(self, master: tk.Tk = None, width: int = 10, height: int = 10, validate_moves: bool = True,
                 delay_millis: int = DEFAULT_STEP_DELAY_MILLIS) -> None:
        """Initialize a MazeApp instance."""
        if master is None:
            master = tk.Tk()
            master.title('Maze Generator')

        super().__init__(master)

        self.width = width
        self.height = height
        self.validate_moves = validate_moves
        self.delay_millis = delay_millis

        self.generating_maze = False
        self.drawing_path = False
        self.choosing_algorithm = False
        self.generator = None
        self.maze = None
        self.path = []

        window = self.winfo_toplevel()
        window.configure(bg=self.BACKGROUND_COLOR)
        window.minsize(width=700, height=100)

        self.pack()
        canvas_frame = tk.Frame(bg=self.BACKGROUND_COLOR)
        canvas_frame.pack(side='left')
        self.canvas = self.create_canvas(canvas_frame)
        self.stats = self.create_stats_display(canvas_frame)
        self.algorithm_var = tk.StringVar()
        self.animate_var = tk.IntVar()
        self.speed_scale = None
        self.create_menu()

        self.start_time = None
        self.end_time = None
        self.generate_new_maze(generate=False)

    @property
    def animate(self) -> bool:
        """Return a boolean indicating whether animation of maze generation is currently enabled."""
        return self.animate_var.get() == 1

    @animate.setter
    def animate(self, value: bool) -> None:
        """Setter for the animate property."""
        self.animate_var.set(1 if value else 0)

    @property
    def generator_type(self) -> Type[MazeGenerator]:
        """Return a MazeGenerator subclass indicating the current maze generator type."""
        class_name = self.algorithm_var.get()
        for generator_cls in self.SUPPORTED_GENERATORS:
            if generator_cls.__name__ == class_name:
                return generator_cls
        return self.DEFAULT_GENERATOR

    @generator_type.setter
    def generator_type(self, value: Type[MazeGenerator]) -> None:
        """Setter for the generator_type property."""
        if self.generator is None or value != self.generator.__class__:
            self.algorithm_var.set(value.__name__)
            self.generator = value()

    def create_canvas(self, parent: tk.Frame) -> tk.Canvas:
        """Create and return a graphics canvas representing the grid of cells in the maze."""
        width = self.CELL_WIDTH * self.width + self.BORDER_OFFSET
        height = self.CELL_HEIGHT * self.height + self.BORDER_OFFSET
        canvas = tk.Canvas(parent, width=width, height=height, borderwidth=0)
        canvas.bind('<Button-1>', self.click_handler)
        canvas.bind('<Motion>', self.motion_handler)
        canvas.pack(side='top')
        return canvas

    @classmethod
    def create_stats_display(cls, parent: tk.Frame) -> tk.Label:
        """Create and return a graphics element containing statistics about the current maze."""
        stats = tk.Label(parent, pady=5, bg=cls.BACKGROUND_COLOR, fg=cls.TEXT_COLOR, font=cls.FONT)
        stats.pack(side='top')
        return stats

    def create_menu(self) -> None:
        """Create a graphics element containing controls for the user to interact with the program."""
        menu = tk.Frame(bg=self.BACKGROUND_COLOR, pady=10)

        new_button = tk.Label(menu, bg=self.BACKGROUND_COLOR, fg=self.PATH_COLOR, font=self.FONT, padx=20, pady=10,
                              text='[ New Maze ]', cursor='hand2')
        new_button.bind('<Button-1>', self.generate_new_maze)
        new_button.pack(side='top')

        algorithm_button = tk.Label(menu, bg=self.BACKGROUND_COLOR, fg=self.PATH_COLOR, font=self.FONT, padx=20,
                                    pady=10, text='[ Algorithm ]', cursor='hand2')
        algorithm_button.bind('<Button-1>', self.choose_algorithm)
        algorithm_button.pack(side='top')

        animate_button = tk.Checkbutton(menu, bg=self.BACKGROUND_COLOR, fg=self.TEXT_COLOR, font=self.FONT, pady=20,
                                        text='Animate', variable=self.animate_var, command=self.toggle_animate)
        animate_button.pack(side='top')
        self.animate = True

        self.speed_scale = tk.Scale(menu, bg=self.BACKGROUND_COLOR, fg=self.TEXT_COLOR, orient=tk.HORIZONTAL,
                                    length=150, from_=10, to=100, showvalue=0, command=self.update_animation_delay)
        self.speed_scale.pack(side='top')

        delay_label = tk.Label(menu, bg=self.BACKGROUND_COLOR, fg=self.TEXT_COLOR, font=self.FONT, text='Delay')
        delay_label.pack(side='top')

        menu.pack(side='left')

    @staticmethod
    def get_wall_tag(row: int, column: int, direction: Direction) -> str:
        """Return a formatted tag suitable for use when drawing maze walls on the canvas."""
        return f'{row}_{column}_{direction.name}'

    @staticmethod
    def get_frontier_tag(row: int, column: int) -> str:
        """Return a formatted tag suitable for use when drawing frontier cells on the canvas."""
        return f'{row}_{column}'

    def click_handler(self, event: tk.Event) -> None:
        """Event handler for click events on the canvas."""
        if self.generating_maze:
            return
        if self.drawing_path:
            self.drawing_path = False
            if self.end_time is None and self.path and \
                    (self.path[-1].row, self.path[-1].column) == (self.height - 1, self.width - 1):
                self.end_time = time.time()
        else:
            coordinates = self.get_selected_cell_coordinates(event)
            self.select_cell(*coordinates)
            self.drawing_path = True

    def motion_handler(self, event: tk.Event) -> None:
        """Event handler for mouse motion events on the canvas."""
        if self.generating_maze:
            return
        if self.drawing_path:
            coordinates = self.get_selected_cell_coordinates(event)
            if self.path and coordinates != self.path[-1].coordinates:
                if len(self.path) > 1 and coordinates == self.path[-2].coordinates:
                    # moved back one, deselect the most recent cell
                    self.select_cell(*self.path[-1].coordinates)
                else:
                    self.select_cell(*coordinates)

    def toggle_animate(self) -> None:
        """Event handler invoked when the 'Animate' checkbox's state is toggled."""
        self.speed_scale['state'] = tk.NORMAL if self.animate else tk.DISABLED

    def update_animation_delay(self, delay_in_millis: int = DEFAULT_STEP_DELAY_MILLIS) -> None:
        """Update the current animation delay (in milliseconds) to the given value."""
        self.delay_millis = int(delay_in_millis)

    def choose_algorithm(self, event: tk.Event) -> None:
        """Open a dialog box allowing the user to change the maze generation algorithm."""
        if self.choosing_algorithm:
            return

        self.choosing_algorithm = True
        algorithm_window = tk.Toplevel(bg=self.BACKGROUND_COLOR)
        algorithm_window.title('Choose Maze Generation Algorithm')
        algorithm_window.transient(self)

        dfs_button = self.create_algorithm_radio_button(algorithm_window, 'Random Depth First Search',
                                                        RandomDepthFirstSearchGenerator)
        dfs_button.pack(side='top')
        prims_button = self.create_algorithm_radio_button(algorithm_window, 'Prim\'s Algorithm', PrimsGenerator)
        prims_button.pack(side='top')

        def dismiss_algorithm_window(e: Optional[tk.Event] = None) -> None:
            algorithm_window.withdraw()
            self.choosing_algorithm = False

        ok_button = tk.Label(algorithm_window, bg=self.BACKGROUND_COLOR, fg=self.PATH_COLOR, font=self.FONT, padx=20,
                             pady=10, text='[ OK ]', cursor='hand2')
        ok_button.bind('<Button-1>', dismiss_algorithm_window)
        ok_button.pack(side='top')

        algorithm_window.protocol('WM_DELETE_WINDOW', dismiss_algorithm_window)

    def create_algorithm_radio_button(self, parent: tk.Toplevel, text: str, generator_cls: Type[MazeGenerator]) -> tk.Radiobutton:
        button = tk.Radiobutton(parent, bg=self.BACKGROUND_COLOR, fg=self.TEXT_COLOR, font=self.FONT, padx=20, pady=5,
                                selectcolor=self.PATH_COLOR, variable=self.algorithm_var, text=text,
                                value=generator_cls.__name__, command=self.update_maze_generator)
        if generator_cls == self.generator_type:
            button.select()
        return button

    def update_maze_generator(self) -> None:
        """Event handler invoked when a maze algorithm is selected."""
        self.generator = self.generator_type()

    def generate_new_maze(self, event: Optional[tk.Event] = None, generate: bool = True) -> None:
        """Create a new blank maze, and optionally generate paths through it."""
        self.clear_path()
        self.maze = Maze(self.width, self.height, generator=None)
        self.start_time = None
        self.create_maze_grid()

        if generate:
            self.generate_current_maze()

    def generate_current_maze(self, event: Optional[tk.Event] = None) -> None:
        """Generate paths through the current maze."""
        if self.generator is None:
            self.generator_type = self.DEFAULT_GENERATOR

        if self.animate:
            self.generator.event_listener = self.update_maze
        else:
            self.generator.event_listener = None

        self.generating_maze = True
        self.clear_path()
        self.generator.generate(self.maze)
        self.clear_path()
        self.generating_maze = False

        if not self.animate:
            self.create_maze_grid()

        self.start_time = time.time()
        self.end_time = None

    def update_maze(self, state: MazeUpdate) -> None:
        """Event listener for the maze generator that updates the UI when the state changes."""
        if state.type == MazeUpdateType.WALL_REMOVED:
            direction = Direction.between(state.start_cell, state.end_cell)
            wall_tag = self.get_wall_tag(state.start_cell.row, state.start_cell.column, direction)
            self.canvas.delete(wall_tag)
            opposite_wall_tag = self.get_wall_tag(state.end_cell.row, state.end_cell.column, direction.opposite)
            self.canvas.delete(opposite_wall_tag)
            if not self.path or state.start_cell != self.path[-1]:
                self.clear_path()
                self.path.append(state.start_cell)
                self.fill_cell(state.start_cell, self.GENERATE_PATH_COLOR)
            self.path.append(state.end_cell)
            self.fill_cell(state.end_cell, self.GENERATE_PATH_COLOR)
        elif state.type == MazeUpdateType.CELL_MARKED:
            self.canvas.delete(self.get_frontier_tag(*state.start_cell.coordinates))
            for cell in state.new_frontier_cells:
                self.fill_cell(cell, self.FRONTIER_COLOR, tag=self.get_frontier_tag(*cell.coordinates))

        self.canvas.update()

        if state.type == MazeUpdateType.WALL_REMOVED:
            time.sleep(self.delay_millis / 1000)

    def create_maze_grid(self) -> None:
        """Populate the canvas with all of the walls in the current maze."""
        for obj in self.canvas.find_all():
            self.canvas.delete(obj)

        for row in range(self.height):
            for column in range(self.width):
                cell = self.maze[row, column]
                x0 = self.CELL_WIDTH * column + self.BORDER_OFFSET
                y0 = self.CELL_HEIGHT * row + self.BORDER_OFFSET
                x1 = x0 + self.CELL_WIDTH
                y1 = y0 + self.CELL_HEIGHT
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
                        tag = self.get_wall_tag(row, column, direction)
                        self.canvas.create_line(*coordinates, width=width, tags=tag)

    def get_selected_cell_coordinates(self, event: tk.Event) -> Tuple[int, int]:
        """Return the coordinates of the selected cell based on the (x, y) position of the given event."""
        row = max(0, min(event.y // self.CELL_HEIGHT, self.height - 1))
        column = max(0, min(event.x // self.CELL_WIDTH, self.width - 1))
        return row, column

    def select_cell(self, row: int, column: int) -> None:
        """Select (or deselect) the maze cell at the given row and column, toggling its color and updating the path."""
        clicked_cell = self.maze[row, column]
        add = True

        if not self.path:
            if self.validate_moves and (row, column) != (0, 0):
                # print('Path must start at (0, 0)')
                return
        else:
            last_cell = self.path[-1]
            if clicked_cell in self.path:
                if self.validate_moves and clicked_cell != last_cell:
                    # print('Can only undo the last move')
                    return
                add = False
            elif self.validate_moves and clicked_cell not in self.maze.neighbors(last_cell.row, last_cell.column):
                # print('Path must be continuous')
                return
            elif self.validate_moves:
                direction = Direction.between(last_cell, clicked_cell)
                if direction not in last_cell.open_walls:
                    # print(f'Invalid move (through {direction.name} wall)')
                    return

        color = self.PATH_COLOR if add else 'white'
        self.fill_cell(clicked_cell, color)

        if add:
            self.path.append(clicked_cell)
        else:
            self.path = self.path[:-1]

    def fill_cell(self, cell: Cell, color: str, tag: str = 'path'):
        """Fill the given cell in the maze with the given color."""
        row_offset = 2 if cell.row in {0, self.height - 1} else 1
        column_offset = 2 if cell.column in {0, self.width - 1} else 1
        x0 = self.CELL_WIDTH * cell.column + self.BORDER_OFFSET + column_offset
        y0 = self.CELL_HEIGHT * cell.row + self.BORDER_OFFSET + row_offset
        x1 = x0 + self.CELL_WIDTH - (2 if cell.column == self.width - 1 else 1) * column_offset
        y1 = y0 + self.CELL_HEIGHT - (2 if cell.row == self.height - 1 else 1) * row_offset
        self.canvas.create_rectangle(x0, y0, x1, y1, fill=color, width=0, tags=tag)

    def clear_path(self) -> None:
        """Clear the current path of highlighted cells in the maze."""
        self.path.clear()
        self.canvas.delete('path')

    @property
    def elapsed_time(self) -> float:
        """Return the amount of time elapsed since the current maze was fully generated."""
        if self.start_time is not None:
            end_time = self.end_time or time.time()
            return end_time - self.start_time
        return 0

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
