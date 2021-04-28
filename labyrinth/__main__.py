"""Entry point for the labyrinth program."""

from typing import List, Tuple
import argparse
import os
import sys

from labyrinth.generate import (
    DepthFirstSearchGenerator,
    KruskalsGenerator,
    PrimsGenerator,
    WilsonsGenerator,
)
from labyrinth.maze import Maze
from labyrinth.solve import MazeSolver
from labyrinth.ui import MazeApp, SizeCategory


class LabyrinthMain:
    """Main class for the labyrinth program."""

    ALGORITHM_CHOICES = {
        'dfs': DepthFirstSearchGenerator,
        'kruskal': KruskalsGenerator,
        'prim': PrimsGenerator,
        'wilson': WilsonsGenerator,
    }

    def __init__(self, gui: bool = False) -> None:
        """Initialize a LabyrinthMain."""
        parsed_args = self.parse_args(sys.argv[1:])
        self.gui = gui or parsed_args.gui or parsed_args.medium or parsed_args.large
        self.solve = parsed_args.solve
        self.generator = self.ALGORITHM_CHOICES[parsed_args.algorithm]()
        self.width, self.height = parsed_args.dimensions

        if parsed_args.medium:
            self.size_category = SizeCategory.MEDIUM
        elif parsed_args.large:
            self.size_category = SizeCategory.LARGE
        else:
            self.size_category = SizeCategory.SMALL

    @classmethod
    def parse_args(cls, args: List[str]) -> argparse.Namespace:
        """Return a Namespace containing the program's configuration as parsed from the given arguments."""
        parser = argparse.ArgumentParser(description='Generate mazes using a variety of different algorithms.')
        parser.add_argument('dimensions', nargs='?', default='25x25', type=cls.parse_dimensions,
                            help='Dimensions of the maze to generate (e.g., 10x10)')
        parser.add_argument('-a', '--algorithm', choices=sorted(cls.ALGORITHM_CHOICES.keys()), default='dfs',
                            help='The algorithm to use to generate the maze')

        # use a group to prevent passing --gui/--medium/--large and --solve at the same time
        group = parser.add_mutually_exclusive_group()
        group.add_argument('-g', '--gui', '--ui', action='store_true',
                           help='Display a GUI showing the maze being generated')
        group.add_argument('-m', '--medium', '--medium-size', action='store_true',
                           help='Open the GUI with medium sized cells instead of small (the default)')
        group.add_argument('-l', '--large', '--large-size', action='store_true',
                           help='Open the GUI with large sized cells instead of small (the default)')
        group.add_argument('-s', '--solve', action='store_true',
                           help='Show the solution to the maze (only applies to non-GUI mode)')

        return parser.parse_args(args)

    @staticmethod
    def parse_dimensions(dimension_str: str) -> Tuple[int, int]:
        """Parse the given dimension string into a two-tuple describing the maze's width and height."""
        dimensions = dimension_str.lower().split('x')
        if len(dimensions) != 2:
            raise ValueError('Dimensions must contain exactly one "x"!')
        width, height = dimensions
        return int(width), int(height)

    def run_gui(self) -> None:
        """Launch a graphical maze generator window."""
        os.environ['TK_SILENCE_DEPRECATION'] = '1'
        app = MazeApp(width=self.width, height=self.height, size_category=self.size_category, generator=self.generator)
        app.run()

    def run(self) -> None:
        """Run the program."""
        if self.gui:
            self.run_gui()
        else:
            maze = Maze(self.width, self.height, generator=self.generator)
            if self.solve:
                solver = MazeSolver()
                maze.path = solver.solve(maze)
            print(maze)


def main(gui: bool = False) -> None:
    """Entry point for the 'labyrinth' and 'maze' programs."""
    LabyrinthMain(gui=gui).run()


def gui() -> None:
    """Entry point for the 'labyrinth-ui' and 'maze-ui' programs."""
    main(gui=True)


if __name__ == '__main__':
    main()
