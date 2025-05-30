from typing import List
from .graph import ManualGraph


class GraphTraversal:
    
    def __init__(self, graph: ManualGraph):
        self.graph = graph
    
    def bfs(self, start: str) -> List[str]:
        if start not in self.graph.adjacency_list:
            raise ValueError(f"Nodo '{start}' no existe en el grafo")
        
        visited = []
        queue = [start]
        seen = {start}
        
        
        while queue:
            current = queue.pop(0)
            visited.append(current)
            neighbors = sorted(self.graph.get_neighbors(current))
            for neighbor in neighbors:
                if neighbor not in seen:
                    seen.add(neighbor)
                    queue.append(neighbor)
                    print(f"[BFS DEBUG] Agregando a cola: {neighbor}")
            
            print(f"[BFS DEBUG] Cola actual: {queue}")
        
        print(f"[BFS DEBUG] Orden final: {visited}")
        return visited
    
    def dfs(self, start: str) -> List[str]:
        if start not in self.graph.adjacency_list:
            raise ValueError(f"Nodo '{start}' no existe en el grafo")
        
        visited = []
        stack = [start]
        seen = {start}
        
        print(f"[DFS DEBUG] Iniciando desde: {start}")
        
        while stack:
            current = stack.pop()
            visited.append(current)
            print(f"[DFS DEBUG] Visitando: {current}")
            
            neighbors = sorted(self.graph.get_neighbors(current), reverse=True)
            for neighbor in neighbors:
                if neighbor not in seen:
                    seen.add(neighbor)
                    stack.append(neighbor)
                    print(f"[DFS DEBUG] Agregando a pila: {neighbor}")
            
            print(f"[DFS DEBUG] Pila actual: {stack}")
        
        print(f"[DFS DEBUG] Orden final: {visited}")
        return visited