"""Utility collection classes."""


class TreeSet:
    """
    A tree set is an implementation of a disjoint-set data structure.

    References:
        https://en.wikipedia.org/wiki/Disjoint-set_data_structure
        https://weblog.jamisbuck.org/2011/1/3/maze-generation-kruskal-s-algorithm
    """

    def __init__(self) -> None:
        """Initialize a TreeSet."""
        self.parent = None

    @property
    def root(self) -> 'TreeSet':
        """Return the root of this tree set."""
        if self.parent is None:
            return self
        return self.parent.root

    def is_connected(self, tree: 'TreeSet') -> bool:
        """Return True if this tree set is connected to the given tree set, False otherwise."""
        return self.root == tree.root

    def merge(self, tree: 'TreeSet') -> None:
        """Merge the given tree set into this tree set."""
        tree.root.parent = self
