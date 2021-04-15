from typing import Set, Tuple

from labyrinth.graph import Graph


class Cell:

    def __init__(self, row: int, column: int) -> None:
        self._row = row
        self._column = column
        self.open_walls = set()

    def __str__(self) -> str:
        return f'{self.__class__.__name__}{self.coordinates}'

    @property
    def row(self) -> int:
        return self._row

    @property
    def column(self) -> int:
        return self._column

    @property
    def coordinates(self) -> Tuple[int, int]:
        return self.row, self.column


class Grid:

    def __init__(self, width: int = 10, height: int = 10) -> None:
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
        return self.get_cell(*item)

    @property
    def width(self) -> int:
        return self._width

    @property
    def height(self) -> int:
        return self._height

    @property
    def graph(self) -> Graph[Cell]:
        return self._graph

    def get_cell(self, row: int, column: int) -> Cell:
        if not 0 <= row < self.height:
            raise ValueError(f'Invalid row {row!r}')
        if not 0 <= column < self.width:
            raise ValueError(f'Invalid column {column!r}')
        return self._cells[(row, column)]

    def neighbors(self, row: int, column: int) -> Set[Cell]:
        return self._graph.neighbors(self[row, column])
