from labyrinth.graph import Graph


class Cell:

    def __init__(self, row, column):
        self._row = row
        self._column = column
        self.open_walls = set()

    @property
    def row(self):
        return self._row

    @property
    def column(self):
        return self._column

    @property
    def coordinates(self):
        return self.row, self.column


class Grid:

    def __init__(self, width=10, height=10):
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

    def __getitem__(self, item):
        return self.get_cell(*item)

    @property
    def width(self):
        return self._width

    @property
    def height(self):
        return self._height

    def get_cell(self, row, column):
        if not 0 <= row < self.height:
            raise ValueError(f'Invalid row {row}')
        if not 0 <= column < self.width:
            raise ValueError(f'Invalid column {column}')
        return self._cells[(row, column)]

    def neighbors(self, row, column):
        return self._graph.neighbors(self[row, column])
