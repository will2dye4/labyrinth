from collections import defaultdict, deque


class Graph:

    def __init__(self, vertices=None, edges=None, bidirectional=True):
        self._adjacencies = {}
        self._bidirectional = bidirectional

        if vertices is not None:
            for vertex in vertices:
                self.add_vertex(vertex)

        if edges is not None:
            for edge in edges:
                self.add_edge(*edge)

    @property
    def bidirectional(self):
        return self._bidirectional

    @property
    def vertices(self):
        return set(self._adjacencies.keys())

    @property
    def size(self):
        return len(self._adjacencies)

    def neighbors(self, vertex):
        self._ensure_vertices(vertex)
        return self._adjacencies[vertex]

    def add_vertex(self, vertex):
        if vertex not in self._adjacencies:
            self._adjacencies[vertex] = set()

    def remove_vertex(self, vertex):
        self._ensure_vertices(vertex)
        neighbors = self._adjacencies[vertex]
        # removing a vertex implies removing the edges connected to that vertex
        for neighbor in neighbors:
            self._adjacencies[neighbor].remove(vertex)
        del self._adjacencies[vertex]

    def add_edge(self, left, right):
        self._ensure_vertices(left, right)
        self._adjacencies[left].add(right)
        if self._bidirectional:
            self._adjacencies[right].add(left)

    def remove_edge(self, left, right):
        self._ensure_vertices(left, right)
        self._adjacencies[left].remove(right)
        if self._bidirectional:
            self._adjacencies[right].remove(left)

    def has_edge(self, left, right):
        self._ensure_vertices(left, right)
        return right in self._adjacencies[left]

    def breadth_first_search(self, start_vertex, visit_fn=print):
        self._ensure_vertices(start_vertex)
        visited = defaultdict(bool)
        queue = deque([start_vertex])
        while queue:
            vertex = queue.popleft()
            if not visited[vertex]:
                visit_fn(vertex)
                visited[vertex] = True
                for neighbor in self.neighbors(vertex):
                    if not visited[neighbor]:
                        queue.append(neighbor)

    def depth_first_search(self, start_vertex, visit_fn=print):
        self._ensure_vertices(start_vertex)
        visited = defaultdict(bool)
        stack = [start_vertex]
        while stack:
            vertex = stack.pop()
            if not visited[vertex]:
                visit_fn(vertex)
                visited[vertex] = True
                for neighbor in self.neighbors(vertex):
                    if not visited[neighbor]:
                        stack.append(neighbor)

    def _ensure_vertices(self, *vertices):
        for vertex in vertices:
            if vertex not in self._adjacencies:
                raise ValueError(f'Invalid vertex {vertex:r}')
