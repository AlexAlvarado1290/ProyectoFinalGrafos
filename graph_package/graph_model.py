"""
Modelo principal del grafo que integra todas las funcionalidades
"""
from typing import List, Tuple, Optional
from .graph import ManualGraph
from .algorithms import GraphTraversal
from .file_io import GraphFileIO


class GraphCompatibilityWrapper:
    
    def __init__(self, manual_graph: ManualGraph):
        self._graph = manual_graph
    
    def nodes(self):
        return self._graph.get_nodes()
    
    def edges(self, data=False):
        edges = self._graph.get_edges()
        if data:
            return [(u, v, {'weight': w}) for u, v, w in edges]
        return [(u, v) for u, v, w in edges]
    
    def neighbors(self, node):
        return self._graph.get_neighbors(node)
    
    def has_edge(self, u, v):
        return self._graph.has_edge(u, v)
    
    def add_node(self, node):
        self._graph.add_node(node)
    
    def add_edge(self, u, v, weight=1.0):
        self._graph.add_edge(u, v, weight)
    
    def remove_node(self, node):
        self._graph.remove_node(node)
    
    def remove_edge(self, u, v):
        self._graph.remove_edge(u, v)
    
    def clear(self):
        self._graph.clear()
    
    def __contains__(self, node):
        return node in self._graph
    
    def __len__(self):
        return len(self._graph)


class GraphModel:
    
    def __init__(self):
        self.manual_graph = ManualGraph()
        self.traversal = GraphTraversal(self.manual_graph)
        self.file_io = GraphFileIO()
    
    # ---------- I/O ----------
    def load_from_edges(self, edges: List[Tuple[str, str, float]]):
        self.file_io.load_from_edges(self.manual_graph, edges)

    def load_from_csv(self, path: str, fallback: Optional[List[Tuple[str, str, float]]] = None):
        if not self.file_io.load_from_csv(self.manual_graph, path) and fallback:
            self.file_io.load_from_edges(self.manual_graph, fallback)

    def save_to_csv(self, path: str):
        return self.file_io.save_to_csv(self.manual_graph, path)

    # ---------- Algoritmos ----------
    def bfs(self, start: str) -> List[str]:
        return self.traversal.bfs(start)

    def dfs(self, start: str) -> List[str]:
        return self.traversal.dfs(start)

    @property
    def G(self):
        return GraphCompatibilityWrapper(self.manual_graph)