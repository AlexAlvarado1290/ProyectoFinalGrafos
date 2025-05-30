from typing import Dict, List, Tuple


class ManualGraph:
    
    def __init__(self):
        self.adjacency_list: Dict[str, Dict[str, float]] = {}
    
    
    def add_node(self, node: str):
        if node not in self.adjacency_list:
            self.adjacency_list[node] = {}
    
    def add_edge(self, u: str, v: str, weight: float = 1.0):
        self.add_node(u)
        self.add_node(v)
        
        self.adjacency_list[u][v] = weight
        self.adjacency_list[v][u] = weight
    
    def remove_node(self, node: str):
        if node not in self.adjacency_list:
            return
        
        for neighbor in list(self.adjacency_list[node].keys()):
            self.remove_edge(node, neighbor)
        
        del self.adjacency_list[node]
    
    def remove_edge(self, u: str, v: str):
        if u in self.adjacency_list and v in self.adjacency_list[u]:
            del self.adjacency_list[u][v]
        if v in self.adjacency_list and u in self.adjacency_list[v]:
            del self.adjacency_list[v][u]
    
    def has_edge(self, u: str, v: str) -> bool:
        return (u in self.adjacency_list and 
                v in self.adjacency_list[u])
    
    def get_weight(self, u: str, v: str) -> float:
        if self.has_edge(u, v):
            return self.adjacency_list[u][v]
        return float('inf')
    
    def get_neighbors(self, node: str) -> List[str]:
        if node in self.adjacency_list:
            return list(self.adjacency_list[node].keys())
        return []
    
    def get_nodes(self) -> List[str]:
        return list(self.adjacency_list.keys())
    
    def get_edges(self) -> List[Tuple[str, str, float]]:
        edges = []
        visited = set()
        
        for u in self.adjacency_list:
            for v, weight in self.adjacency_list[u].items():
                edge = tuple(sorted([u, v]))
                if edge not in visited:
                    visited.add(edge)
                    edges.append((u, v, weight))
        
        return edges
    
    def clear(self):
        self.adjacency_list.clear()
    
    def __contains__(self, node: str) -> bool:
        return node in self.adjacency_list
    
    def __len__(self) -> int:
        return len(self.adjacency_list)
    
    def to_networkx(self):
        try:
            import networkx as nx
        except ModuleNotFoundError:
            return None
            
        G = nx.Graph()
        
        for node in self.get_nodes():
            G.add_node(node)

        for u, v, weight in self.get_edges():
            G.add_edge(u, v, weight=weight)
        
        return G