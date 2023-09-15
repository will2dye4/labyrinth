# labyrinth - Python maze generator and solver

This package contains utilities for generating and solving [mazes](https://en.wikipedia.org/wiki/Maze)
using a variety of different algorithms.

## About

![Animation - Graph to Grid](https://raw.githubusercontent.com/will2dye4/labyrinth/master/images/animations/graph_to_grid.gif)

See the [docs](https://github.com/will2dye4/labyrinth/blob/master/docs/about.md) for a history of
this project and an introduction to the mathematical underpinnings of the maze generation and
solution algorithms implemented in this package.

## Installation

The easiest way to install the package is to download it from [PyPI](https://pypi.org) using `pip`.
Note that `labyrinth` depends on [Python](https://www.python.org/downloads/) 3.7 or newer; please
ensure that you have a semi-recent version of Python installed before proceeding.

Run the following command in a shell (a UNIX-like environment is assumed):

```
$ pip install labyrinth-py
```

The package does not have any dependencies besides Python itself. If you wish to
sandbox your installation inside a virtual environment, you may choose to use
[virtualenvwrapper](https://virtualenvwrapper.readthedocs.io/en/latest/) or a similar
utility to do so.

When successfully installed, a program called `maze` and another program called `maze-ui`
will be placed on your `PATH`. See the Usage section below for details about how to use
these programs.

## Usage

The `maze` program is a command-line interface for generating mazes.

At any time, you can use the `-h` or `--help` flags to see a summary of options that
the program accepts.

```
$ maze -h
usage: maze [-h] [-a {dfs,kruskal,prim,wilson}] [-g | -m | -l | -s] [dimensions]

Generate mazes using a variety of different algorithms.

positional arguments:
  dimensions            Dimensions of the maze to generate (e.g., 10x10)

optional arguments:
  -h, --help            show this help message and exit
  -a {dfs,kruskal,prim,wilson}, --algorithm {dfs,kruskal,prim,wilson}
                        The algorithm to use to generate the maze
  -g, --gui, --ui       Display a GUI showing the maze being generated
  -m, --medium, --medium-size
                        Open the GUI with medium sized cells instead of small (the default)
  -l, --large, --large-size
                        Open the GUI with large sized cells instead of small (the default)
  -s, --solve           Show the solution to the maze (only applies to non-GUI mode)
```

Typical usage is `maze <dimensions>`, where `<dimensions>` is a string like `10x10`
describing the dimensions of the maze to generate (width x height). The program will
generate a random maze of the given size and print an ASCII representation of the maze
to the console. Add the `-s` (`--solve`) flag to display the solution to the maze as well.

### Algorithms

By default, `maze` will use a depth-first search algorithm to generate the maze.
To specify a different algorithm, use the `-a` or `--algorithm` flags to `maze`. The
available algorithms are `dfs`, `kruskal`, `prim`, and `wilson`. See the
[docs](https://github.com/will2dye4/labyrinth/blob/master/docs/generation_algorithms.md)
for a description of each of these algorithms.

### Output

When running in non-GUI mode (the default), the `maze` program prints output to the console. Sample
output from running the `maze` program with a custom size is as follows.

```
$ maze 20x10
+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+
|               |           |           |       |       |               |       |
+---+---+---+   +---+   +   +---+   +   +   +   +   +   +   +---+   +---+   +   +
|           |           |           |       |   |   |   |   |   |           |   |
+   +---+   +---+---+---+---+---+---+---+---+   +   +   +   +   +---+---+---+   +
|   |                       |       |       |   |   |           |           |   |
+   +   +---+---+---+---+   +   +   +   +---+   +   +---+---+---+   +---+   +   +
|   |   |                   |   |       |       |   |           |   |   |       |
+---+   +---+---+---+---+   +   +   +---+   +---+   +   +---+   +   +   +---+   +
|       |       |       |       |   |       |       |       |       |           |
+   +   +   +   +   +   +   +---+---+   +---+---+---+---+   +---+---+---+---+   +
|   |   |   |       |   |   |       |           |           |               |   |
+   +   +   +---+---+   +---+   +   +---+---+   +   +---+---+   +---+---+   +---+
|   |   |       |   |           |           |   |                       |       |
+   +---+---+   +   +---+---+---+---+   +---+   +---+---+   +---+---+---+   +   +
|           |       |                   |       |       |   |           |   |   |
+   +---+   +---+   +   +   +---+---+---+   +---+   +   +---+   +---+   +   +   +
|   |   |           |   |   |               |       |           |       |   |   |
+   +   +---+---+---+   +---+   +---+---+---+---+   +---+---+---+   +---+---+   +
|                   |                               |                           |
+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+
```

The following is an example of using the `-a` flag to specify a maze generation
algorithm (see above) and the `-s` flag to show the solution to the maze.

```
$ maze 20x10 -a kruskal -s
+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+
| X   X   X |   |       |       |       |           |       |   |   |           |
+   +---+   +   +   +---+   +---+   +   +---+   +   +---+   +   +   +---+   +---+
|   |     X   X   X |   |   |   |   |   |       |       |       |   |   |   |   |
+   +---+---+---+   +   +   +   +   +---+   +---+---+---+---+   +   +   +   +   +
|   |   |   |   | X |                           |       |       |               |
+---+   +   +   +   +---+---+---+---+---+---+   +   +   +   +---+---+   +---+   +
|   |   |   |   | X |   |   |       |               |       |   |   |   |       |
+   +   +   +   +   +   +   +   +---+---+---+---+---+---+   +   +   +   +   +---+
|           |     X |       |                           |       |   |   |       |
+---+---+   +---+   +   +   +---+   +---+---+---+---+   +   +---+   +   +---+---+
|   |             X |   |   |       |             X   X     |           |   |   |
+   +---+---+   +   +---+   +---+---+---+   +---+   +   +---+---+   +---+   +   +
|               | X   X |   |   |   |   |   |   | X | X   X |               |   |
+   +---+---+   +   +   +   +   +   +   +---+   +   +---+   +---+---+---+   +   +
|   |   |   |   |   | X   X   X   X   X |       | X |   | X |       |           |
+   +   +   +   +   +   +---+---+---+   +---+   +   +   +   +   +---+   +---+---+
|           |   |   |   |       | X   X |         X     | X   X   X   X   X   X |
+   +   +   +   +   +   +   +---+   +---+---+---+   +   +   +---+---+---+---+   +
|   |   |   |   |   |       |     X   X   X   X   X |   |       |             X |
+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+
```

#### Exit Codes

When the program runs successfully, it exits with a code of zero (0). If the program
encounters an error in parsing the arguments that were passed to it, it exits with a code
of two (2).

### GUI Mode

In order to visualize the process of generating mazes, the program also has a GUI mode,
which can be activated with the `-g` (`--gui`) flag to `maze`, or by simply invoking `maze-ui`
instead of `maze`. By default, the GUI will render the maze with small cells, but the `-m` (`--medium`)
or `-l` (`--large`) flags may be passed instead of the `-g` flag to increase the size of the cells.
When running in GUI mode, only error output is printed to the console, and a window will open containing
a visual representation of the maze and controls for generating new mazes using the different algorithms
described [here](https://github.com/will2dye4/labyrinth/blob/master/docs/generation_algorithms.md).
Once a maze has been generated, clicking and dragging from the top left corner of the maze allows the user
to solve the maze if they wish; the goal is to reach the bottom right corner. While a maze is being
generated or solved, the GUI also displays statistics that show the size of the maze, the length of the
current path through the maze, and how much time has elapsed since the maze was generated (i.e., how long
it has taken you to solve it!).

By default, the generation of new mazes will be animated, showing the current path being added to the maze
at each step of the process, but this behavior can be disabled by unchecking the `Animate` box on
the right side of the GUI. When animation is enabled, the `Speed` slider can also be adjusted
to increase or decrease the delay between steps in the animation. Clicking the `Algorithm...` button
will open a dialog box for selecting which algorithm should be used to generate mazes (see above).
Clicking the `Maze Size...` button will open a dialog box for adjusting the size of the maze. Both the
dimensions of the maze and the size of the cells can be customized. The maximum allowed maze size is 100 x 100.

When the `Graph Mode` box is checked, the conventional grid view of the maze will be replaced by a
representation of the graph structure underlying the maze. This mode can be toggled on and off as desired
to compare the traditional visual representation of the maze to the vertices and edges that the program
is actually using to model the maze.

In addition to generating mazes, `maze-ui` is also capable of solving mazes. Once a maze has been
generated, clicking the `Solve` button will show the path through the maze (from the top left corner
to the bottom right corner). If animation is enabled (see above), the drawing of the correct path will
be animated, although the actual process of finding the solution&mdash;which is based on a depth-first
search of a "junction graph" of the maze&mdash;is not animated.

A few screenshots of the program running in GUI mode are shown below.

![Maze UI - Grid Mode (solved)](https://raw.githubusercontent.com/will2dye4/labyrinth/master/images/grid_mode_solved.png)

![Maze UI - Graph Mode (solved)](https://raw.githubusercontent.com/will2dye4/labyrinth/master/images/graph_mode_solved.png)

![Maze UI - Grid Mode (Prim's generator)](https://raw.githubusercontent.com/will2dye4/labyrinth/master/images/grid_mode_prims_generator.png)

![Maze UI - Graph Mode (Kruskal's generator)](https://raw.githubusercontent.com/will2dye4/labyrinth/master/images/graph_mode_kruskals_generator.png)

![Maze UI - Grid Mode (large cells)](https://raw.githubusercontent.com/will2dye4/labyrinth/master/images/grid_mode_large_cells.png)

![Maze UI - Graph Mode (large cells)](https://raw.githubusercontent.com/will2dye4/labyrinth/master/images/graph_mode_large_cells.png)

## References

This project owes a massive debt of gratitude to the
[series of articles on maze generation](https://weblog.jamisbuck.org/2011/2/7/maze-generation-algorithm-recap)
featured on [Jamis Buck's blog](https://weblog.jamisbuck.org). The step-by-step breakdown of various
algorithms, along with simple diagrams and animations showing how the algorithms work, were invaluable in
creating my own adaptations of these algorithms. The 
[article on maze-solving algorithms](https://www.kidscodecs.com/maze-solving-algorithms/) on the website of
[*Beanz* magazine](https://www.kidscodecs.com) also came in handy for understanding the concept of the
"junction graph" and using tree traversal to solve mazes.

In addition to the articles linked to above, I also found the following resources helpful while working
on this project:

* https://en.wikipedia.org/wiki/Maze_generation_algorithm
* https://en.wikipedia.org/wiki/Maze_solving_algorithm
* https://tkdocs.com/shipman/
