"""Entry point for the labyrinth program."""

from typing import List, Tuple
import argparse
import os
import sys

from labyrinth.maze import Maze
from labyrinth.ui import MazeApp


class LabyrinthMain:
    """Main class for the labyrinth program."""

    def __init__(self, gui: bool = False) -> None:
        """Initialize a LabyrinthMain."""
        parsed_args = self.parse_args(sys.argv[1:])
        self.gui = gui or parsed_args.gui
        self.width, self.height = parsed_args.dimensions

    @classmethod
    def parse_args(cls, args: List[str]) -> argparse.Namespace:
        """Return a Namespace containing the program's configuration as parsed from the given arguments."""
        parser = argparse.ArgumentParser(description='Generate mazes.')
        parser.add_argument('dimensions', nargs='?', default='25x25', type=cls.parse_dimensions,
                            help='Dimensions of the maze to generate (e.g., 10x10)')
        parser.add_argument('-g', '--gui', '--ui', action='store_true',
                            help='Display a GUI showing the maze being generated')
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
        app = MazeApp(width=self.width, height=self.height)
        app.run()

    def run(self) -> None:
        """Run the program."""
        if self.gui:
            self.run_gui()
        else:
            print(Maze(self.width, self.height))


def main(gui: bool = False) -> None:
    """Entry point for the 'labyrinth' and 'maze' programs."""
    LabyrinthMain(gui=gui).run()


def gui() -> None:
    """Entry point for the 'labyrinth-ui' and 'maze-ui' programs."""
    main(gui=True)


if __name__ == '__main__':
    main()
