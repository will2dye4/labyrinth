# About

Creating mazes by hand has long been a hobby of mine, since I was in elementary school. I always liked
solving mazes ever since I learned what they were, and I eventually realized that they were just as much
fun to make as they were to solve&mdash;if not more so! My dad and I would create mazes for each other,
trying our hardest to create a maze that was too puzzling for the other to solve. We would time ourselves
while solving each other's creations in a constant battle to prove who was the better maze solver. We
never did get a definitive answer to that question, but mazes have been a passion of mine ever since.

![Animation - Graph Basics](../images/animations/graph_basics.gif)

My passion for mazes was only further amplified when I discovered one day in a college math class that mazes
are perfect candidates for modeling with the branch of mathematics known as
[graph theory](https://en.wikipedia.org/wiki/Graph_theory). In its most basic form, a *graph* is a set of
objects (known as *vertices* or *nodes*) and a set of pairwise connections between objects (known as *edges*).
Graphs have all kinds of immensely useful practical applications, in areas as diverse as biology, computer
science, and linguistics. In addition to all of these extremely pragmatic applications of graph theory,
graphs can be fun, too&mdash;it turns out that it is possible to generate mazes using several well-known graph
theory algorithms! I have wanted to explore these algorithms and the connection between mazes and graphs ever since,
and this package is the realization of those aspirations.

In order to represent a rectangular maze as a graph, we simply create a vertex for each cell in the maze, and then
we add an edge between any two cells that are neighbors of each other. In this context, only cells directly to the
north, south, east, and west of a given cell are considered neighbors, since you typically aren't allowed to move
diagonally through mazes. Once we have this graph-based representation of the maze grid, generating the maze itself
is exactly equivalent to finding a *spanning tree* of the graph. A *tree* is a special type of graph that is 
*connected* (i.e., there exists a path between any two chosen vertices) and *acyclic* (i.e., there are no looping 
paths). A spanning tree is simply a tree that *spans* (or includes) all vertices of the graph.

![Animation - Creating a Spanning Tree of a Graph](../images/animations/graph_to_tree.gif)

The `labyrinth` package uses this graph theory&ndash;based approach to model mazes as a grid of connected cells.
To maintain efficient access to the neighbors of any given cell, the graph is stored using
[adjacency lists](https://en.wikipedia.org/wiki/Adjacency_list). The `labyrinth.graph` module is an
object-oriented implementation of the mathematical concept of graphs as described in the previous paragraph.
This module has no concept of mazes and can be used independently of the rest of this project for any number of
graph-based applications. The only requirement is that the objects being used as vertices must be hashable
(which most Python objects are by default).