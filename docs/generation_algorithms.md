# Maze Generation Algorithms

By default, `maze` will use a depth-first search algorithm to generate the maze.
To specify a different algorithm, use the `-a` or `--algorithm` flags to `maze`. The
available algorithms are `dfs`, `kruskal`, `prim`, and `wilson`. A description of each
of these algorithms follows.

## Depth-First Search (DFS)

![Animation - Depth First Search Algorithm](../images/animations/generation_algorithms/dfs.gif)

The **DFS (depth-first search) algorithm** generates paths through the maze using a
conventional [depth-first search](https://en.wikipedia.org/wiki/Depth-first_search)
through the maze's underlying graph. The search starts in the top left corner and 
repeatedly moves to a neighboring cell, creating a path as it goes. When the path reaches 
a dead end (i.e., moving to any neighboring cell would create a cycle), the algorithm 
backtracks to the most recent unvisited cell and starts again. Because of this backtracking
behavior, this algorithm is also sometimes referred to as the **recursive backtrack** algorithm.
The DFS algorithm tends to produce mazes with long, winding corridors but which are not 
particularly difficult to solve.

## Kruskal's Algorithm

![Animation - Kruskal's Algorithm](../images/animations/generation_algorithms/kruskal.gif)

The version of **Kruskal's algorithm** implemented here is a modified version of
[Kruskal's algorithm](https://en.wikipedia.org/wiki/Kruskal%27s_algorithm) for finding
minimum spanning trees of connected graphs. Because the maze graph is unweighted,
the algorithm is modified to select edges at random rather than based on lowest weight,
but otherwise the algorithm is the same: at each step, an edge between two neighboring
cells is selected, and the walls between the cells are removed if the two cells belong to
disjoint paths through the maze. Kruskal's algorithm tends to produce mazes with many
short cul-de-sacs and dead ends which are moderately difficult to solve.

## Prim's Algorithm

![Animation - Prim's Algorithm](../images/animations/generation_algorithms/prim.gif)

The version of **Prim's algorithm** implemented here is a modified version of
[Prim's algorithm](https://en.wikipedia.org/wiki/Prim%27s_algorithm), which, like
Kruskal's algorithm, finds minimum spanning trees of connected graphs. As with Kruskal's
algorithm, Prim's algorithm has been modified to select edges at random rather than by
weight. Prim's algorithm starts by selecting a random cell in the graph and marking it as
being part of the maze. It then adds all of that cell's neighbors to a set called the "frontier."
At each subsequent step, a cell is randomly chosen from the set of frontier cells and added to the
maze, and all of that cell's neighbors are added to the set of frontier cells. The process
continues until there are no frontier cells left, meaning that all cells are part of the maze.
Prim's algorithm, like Kruskal's algorithm, tends to produce mazes with many cul-de-sacs and
dead ends.

## Wilson's Algorithm

![Animation - Wilson's Algorithm](../images/animations/generation_algorithms/wilson.gif)

**Wilson's algorithm** is somewhat similar to Kruskal's and Prim's algorithms, but unlike those
algorithms, Wilson's algorithm generates [uniform spanning trees](https://en.wikipedia.org/wiki/Loop-erased_random_walk#Uniform_spanning_tree)
and therefore tends to produce mazes which are a bit more visually pleasing than those generated
by the previous two algorithms. Wilson's algorithm works by performing repeated loop-erased random
walks through the graph, creating entire passages and adding them to the maze at once. (For more
details about loop-erased random walks and uniform spanning trees, see the Wikipedia link earlier
in this paragraph.)
