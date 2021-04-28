"""Classes representing the menu and dialog boxes in the UI."""

from enum import Enum
from typing import Any, Optional, Type
import tkinter as tk

from labyrinth.generate import MazeGenerator
from labyrinth.ui.colors import BACKGROUND_COLOR
from labyrinth.ui.common import Checkbutton, Entry, Frame, Label, LabelButton, Radiobutton, Scale


class DisplayMode(Enum):
    GRID = 1
    GRAPH = 2


class SizeCategory(Enum):
    # values are (cell_width, vertex_radius)
    SMALL = (35, 10)
    MEDIUM = (50, 15)
    LARGE = (75, 20)


class DialogBox(tk.Toplevel):
    """DialogBox is a dialog box in the UI allowing users to configure the application."""

    def __init__(self, menu: 'MazeAppMenu', title: str, **kwargs) -> None:
        """Initialize a DialogBox."""
        super().__init__(bg=BACKGROUND_COLOR, padx=60, pady=10, **kwargs)
        self.title(title)
        self.transient(menu)
        self.menu = menu
        self.menu.app.using_dialog_box = True
        self.protocol('WM_DELETE_WINDOW', self.dismiss)

    def dismiss(self, event: Optional[tk.Event] = None) -> None:
        """Dismiss (close) the dialog box."""
        self.withdraw()
        self.menu.app.using_dialog_box = False


class MazeAppMenu(Frame):
    """Class containing state and graphics for rendering the menu portion of the UI."""

    MIN_SPEED = 1
    MAX_SPEED = 6
    DEFAULT_SPEED = MAX_SPEED

    MAX_MAZE_SIZE = 100

    def __init__(self, app: 'MazeApp', size_category: Optional[SizeCategory] = None, **kwargs) -> None:
        """Initialize a MazeAppMenu."""
        super().__init__(padx=10, pady=10, **kwargs)
        self.app = app

        self.algorithm_var = tk.StringVar()
        self.maze_size_var = tk.StringVar()
        self.maze_width_var = tk.StringVar()
        self.maze_height_var = tk.StringVar()
        self.animate_var = tk.IntVar()
        self.graph_mode_var = tk.IntVar()
        self.delay_millis = 0
        self.speed_scale = None

        self.pack()
        self.create_menu()

        self.update_animation_delay()
        self.size_category = size_category
        self.generator_type = self.app.generator.__class__
        self.maze_width = self.app.width
        self.maze_height = self.app.height

    @property
    def animate(self) -> bool:
        """Return a boolean indicating whether animation of maze generation is currently enabled."""
        return self.animate_var.get() == 1

    @animate.setter
    def animate(self, value: bool) -> None:
        """Setter for the animate property."""
        self.animate_var.set(1 if value else 0)

    @property
    def display_mode(self) -> DisplayMode:
        """Return the current display mode (grid or graph)."""
        return DisplayMode.GRAPH if self.graph_mode_var.get() == 1 else DisplayMode.GRID

    @display_mode.setter
    def display_mode(self, value: DisplayMode) -> None:
        """Setter for the display mode property."""
        self.graph_mode_var.set(1 if value == DisplayMode.GRAPH else 0)

    @property
    def generator_type(self) -> Optional[Type[MazeGenerator]]:
        """Return a MazeGenerator subclass indicating the current maze generator type."""
        class_name = self.algorithm_var.get()
        if not class_name:
            return None
        return next(
            (cls for cls in self.app.SUPPORTED_GENERATORS if cls.__name__ == class_name),
            self.app.DEFAULT_GENERATOR
        )

    @generator_type.setter
    def generator_type(self, value: Type[MazeGenerator]) -> None:
        """Setter for the generator_type property."""
        self.algorithm_var.set(value.__name__)

    @property
    def size_category(self) -> SizeCategory:
        """Return the current maze size category."""
        size_name = self.maze_size_var.get()
        return next((size for size in SizeCategory if size.name == size_name), self.app.DEFAULT_SIZE)

    @size_category.setter
    def size_category(self, value: Optional[SizeCategory]) -> None:
        """Setter for the size category property."""
        if value is not None:
            self.maze_size_var.set(value.name)

    @property
    def maze_width(self) -> int:
        """Return the current maze width (number of columns)."""
        return int(self.maze_width_var.get())

    @maze_width.setter
    def maze_width(self, value: int) -> None:
        """Setter for the maze width property."""
        self.maze_width_var.set(str(value))

    @property
    def maze_height(self) -> int:
        """Return the current maze height (number of rows)."""
        return int(self.maze_height_var.get())

    @maze_height.setter
    def maze_height(self, value: int) -> None:
        """Setter for the maze height property."""
        self.maze_height_var.set(str(value))

    def create_menu(self) -> None:
        """Create a graphics element containing controls for the user to interact with the application."""
        new_button = LabelButton(self, 'New Maze', click_handler=self.app.generate_new_maze)
        new_button.pack(side='top')

        self.create_spacer()

        algorithm_button = LabelButton(self, 'Algorithm...', click_handler=self.choose_algorithm)
        algorithm_button.pack(side='top')

        self.create_spacer()

        size_button = LabelButton(self, 'Maze Size...', click_handler=self.choose_size)
        size_button.pack(side='top')

        self.create_spacer()

        solve_button = LabelButton(self, 'Solve', click_handler=self.app.solve_maze)
        solve_button.pack(side='top')

        self.create_spacer(height=3)

        graph_mode_button = Checkbutton(self, text='Graph Mode', variable=self.graph_mode_var,
                                        command=self.app.display_maze)
        graph_mode_button.pack(side='top')

        self.create_spacer()

        animate_button = Checkbutton(self, text='Animate', variable=self.animate_var, command=self.toggle_animate)
        animate_button.pack(side='top')
        self.animate = True

        self.create_spacer(height=2)

        self.speed_scale = Scale(self, orient=tk.HORIZONTAL, length=150, from_=self.MIN_SPEED, to=self.MAX_SPEED,
                                 command=self.update_animation_delay)
        self.speed_scale.set(self.DEFAULT_SPEED)
        self.speed_scale.pack(side='top')

        delay_label = Label(self, text='Speed')
        delay_label.pack(side='top')

    def create_spacer(self, parent: Optional[Any] = None, height: int = 1) -> None:
        """Create a vertical spacer between adjacent UI elements."""
        if parent is None:
            parent = self

        spacer = Label(parent, height=height)
        spacer.pack(side='top')

    def toggle_animate(self) -> None:
        """Event handler invoked when the 'Animate' checkbox's state is toggled."""
        self.speed_scale['state'] = tk.NORMAL if self.animate else tk.DISABLED

    def update_animation_delay(self, speed: int = DEFAULT_SPEED) -> None:
        """Update the current animation delay (in milliseconds) based on the given speed (1 - 5)."""
        delay_in_millis = 2 ** (11 - int(speed))
        self.delay_millis = delay_in_millis

    def choose_algorithm(self, event: tk.Event) -> None:
        """Open a dialog box allowing the user to change the maze generation algorithm."""
        if self.app.using_dialog_box or self.app.generating_maze or self.app.solving_maze:
            return

        algorithm_window = DialogBox(self, 'Choose Maze Generation Algorithm')

        for generator_cls, button_name in self.app.SUPPORTED_GENERATORS.items():
            button = Radiobutton(algorithm_window, variable=self.algorithm_var, text=button_name,
                                 value=generator_cls.__name__)
            if generator_cls == self.generator_type:
                button.select()
            button.pack(side='top')

        self.create_spacer(algorithm_window)

        ok_button = LabelButton(algorithm_window, 'OK', click_handler=algorithm_window.dismiss)
        ok_button.pack(side='top')

    def choose_size(self, event: tk.Event) -> None:
        """Open a dialog box allowing the user to change the maze size."""
        if self.app.using_dialog_box or self.app.generating_maze or self.app.solving_maze:
            return

        size_window = DialogBox(self, 'Choose Maze Size')

        dimension_label = Label(size_window, text='Maze Dimensions')
        dimension_label.pack(side='top')

        dimension_frame = Frame(size_window)
        dimension_frame.pack(side='top')

        width_textbox = Entry(dimension_frame, justify=tk.CENTER, width=3, validate='focusout',
                              validatecommand=(self.register(self.validate_width), '%P'),
                              textvariable=self.maze_width_var)
        width_textbox.pack(side='left')

        x_label = Label(dimension_frame, padx=20, pady=20, text='x')
        x_label.pack(side='left')

        height_textbox = Entry(dimension_frame, justify=tk.CENTER, width=3, validate='focusout',
                               validatecommand=(self.register(self.validate_height), '%P'),
                               textvariable=self.maze_height_var)
        height_textbox.pack(side='left')

        self.create_spacer(size_window)

        size_label = Label(size_window, pady=10, text='Grid Size')
        size_label.pack(side='top')

        for size in SizeCategory:
            button = Radiobutton(size_window, variable=self.maze_size_var, text=size.name.title(), value=size.name,
                                 command=self.app.refresh_canvas)
            if size == self.size_category:
                button.select()
            button.pack(side='top')

        self.create_spacer(size_window)

        ok_button = LabelButton(size_window, 'OK', click_handler=size_window.dismiss)
        ok_button.pack(side='top')

    def validate_width(self, new_width: str) -> bool:
        """Validator for the maze width text box."""
        width = self.validate_dimension(new_width)
        if width is None:
            return False
        if width != self.app.width:
            self.app.width = width
            self.app.refresh_canvas()
        return True

    def validate_height(self, new_height: str) -> bool:
        """Validator for the maze height text box."""
        height = self.validate_dimension(new_height)
        if height is None:
            return False
        if height != self.app.height:
            self.app.height = height
            self.app.refresh_canvas()
        return True

    def validate_dimension(self, new_dimension: str) -> Optional[int]:
        """Validator for the maze width and maze height text boxes."""
        try:
            dimension = int(new_dimension)
            if 0 < dimension <= self.MAX_MAZE_SIZE:
                return dimension
        except ValueError:
            pass
        return None
