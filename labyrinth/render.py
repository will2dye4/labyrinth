"""Base class for rendering the generation of a maze in a graphical interface."""

from typing import Optional, Set
import abc

from labyrinth.generate import MazeUpdate, MazeUpdateType
from labyrinth.grid import Cell


class MazeRenderer(abc.ABC):
    """Abstract base class for a maze renderer (a subscriber to MazeUpdate events that renders the updates in a UI)."""

    DELAY_EVENT_TYPES = {MazeUpdateType.START_CELL_CHOSEN, MazeUpdateType.WALL_REMOVED}

    def update_maze(self, state: MazeUpdate) -> None:
        """Event listener for the maze renderer that updates the UI when the state changes."""
        if state.type == MazeUpdateType.START_CELL_CHOSEN:
            self.set_start_cell(state.start_cell)
        elif state.type == MazeUpdateType.WALL_REMOVED:
            end_of_path = self.get_end_of_current_path()
            if end_of_path is None or state.start_cell != end_of_path:
                self.clear_path()
                self.add_cell_to_generated_path(state.start_cell)
            self.remove_wall(state.start_cell, state.end_cell)
            self.add_cell_to_generated_path(state.end_cell)
        elif state.type == MazeUpdateType.CELL_MARKED:
            self.add_cells_to_frontier(state.new_frontier_cells)
            self.clear_path()
        elif state.type == MazeUpdateType.EDGE_REMOVED:
            self.clear_path()
            self.remove_edge(state.start_cell, state.end_cell)

        self.refresh()

        if state.type in self.DELAY_EVENT_TYPES:
            self.delay()

    @abc.abstractmethod
    def set_start_cell(self, cell: Cell) -> None:
        """Update the cell where the maze generator chose to start."""
        raise NotImplemented

    @abc.abstractmethod
    def clear_path(self) -> None:
        """Clear the current path of highlighted cells in the maze."""
        raise NotImplemented

    @abc.abstractmethod
    def add_cell_to_generated_path(self, cell: Cell) -> None:
        """Add the given cell to the path currently being generated."""
        raise NotImplemented

    @abc.abstractmethod
    def get_end_of_current_path(self) -> Optional[Cell]:
        """Return the cell at the end of the path currently being generated, if any."""
        raise NotImplemented

    @abc.abstractmethod
    def add_cells_to_frontier(self, frontier_cells: Set[Cell]) -> None:
        """Add the given cells to the frontier of the maze."""
        raise NotImplemented

    @abc.abstractmethod
    def remove_wall(self, start_cell: Cell, end_cell: Cell) -> None:
        """Remove the wall between the given start cell and end cell, also clearing any color from the cells."""
        raise NotImplemented

    @abc.abstractmethod
    def remove_edge(self, start_cell: Cell, end_cell: Cell) -> None:
        """Remove the edge between the given start cell and end cell (if rendering the maze as a graph)."""
        raise NotImplemented

    @abc.abstractmethod
    def delay(self) -> None:
        """Delay rendering to allow the user to see the latest updates."""
        raise NotImplemented

    @abc.abstractmethod
    def refresh(self) -> None:
        """Refresh the UI after applying updates."""
        raise NotImplemented
