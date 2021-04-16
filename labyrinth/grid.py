"""Classes for creating and working with grids of cells."""

from typing import Set, Tuple

from labyrinth.graph import Graph


class Cell:
    """Class representing a cell in a grid."""

    def __init__(self, row: int, column: int) -> None:
        """Initialize a Cell."""
        self._row = row
        self._column = column
        self.open_walls = set()

    def __str__(self) -> str:
        """Return a string representation of the cell."""
        return f'{self.__class__.__name__}{self.coordinates}'

    @property
    def row(self) -> int:
        """Return the cell's row number."""
        return self._row

    @property
    def column(self) -> int:
        """Return the cell's column number."""
        return self._column

    @property
    def coordinates(self) -> Tuple[int, int]:
        """Return the cell's row and column as a two-tuple."""
        return self.row, self.column


class Grid:
    """Class representing a grid of cells as a graph."""

    def __init__(self, width: int = 10, height: int = 10) -> None:
        """Initialize a Grid."""
        self._width = width
        self._height = height
        self._cells = {}
        self._graph = Graph()
        for row in range(height):
            for column in range(width):
                coordinates = (row, column)
                cell = Cell(*coordinates)
                self._cells[coordinates] = cell
                self._graph.add_vertex(cell)
                if row > 0:
                    self._graph.add_edge(cell, self[row - 1, column])
                if column > 0:
                    self._graph.add_edge(cell, self[row, column - 1])

    def __getitem__(self, item: Tuple[int, int]) -> Cell:
        """Return the cell in the grid at the given coordinates."""
        return self.get_cell(*item)

    @property
    def width(self) -> int:
        """Return the width (number of columns) of the grid."""
        return self._width

    @property
    def height(self) -> int:
        """Return the height (number of rows) of the grid."""
        return self._height

    @property
    def graph(self) -> Graph[Cell]:
        """Return the graph representation underlying this grid."""
        return self._graph

    def get_cell(self, row: int, column: int) -> Cell:
        """Return the cell in the grid at the given row and column."""
        if not 0 <= row < self.height:
            raise ValueError(f'Invalid row {row!r}')
        if not 0 <= column < self.width:
            raise ValueError(f'Invalid column {column!r}')
        return self._cells[(row, column)]

    def neighbors(self, row: int, column: int) -> Set[Cell]:
        """Return a set of all neighbors of the cell in the grid at the given row and column."""
        return self._graph.neighbors(self[row, column])
