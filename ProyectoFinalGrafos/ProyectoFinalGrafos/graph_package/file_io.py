import csv
import os
from typing import List, Tuple
from .graph import ManualGraph


class GraphFileIO:
    
    @staticmethod
    def load_from_csv(graph: ManualGraph, filename: str) -> bool:
        if not os.path.exists(filename):
            return False
        
        graph.clear()
        try:
            with open(filename, 'r', encoding='utf-8') as file:
                reader = csv.reader(file)
                for row in reader:
                    if len(row) >= 3:
                        u, v, weight = row[0].strip(), row[1].strip(), float(row[2])
                        graph.add_edge(u, v, weight)
            return True
        except Exception as e:
            print(f"Error cargando CSV: {e}")
            return False
    
    @staticmethod
    def save_to_csv(graph: ManualGraph, filename: str) -> bool:
        try:
            with open(filename, 'w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                for u, v, weight in graph.get_edges():
                    writer.writerow([u, v, weight])
            return True
        except Exception as e:
            print(f"Error guardando CSV: {e}")
            return False
    
    @staticmethod
    def load_from_edges(graph: ManualGraph, edges: List[Tuple[str, str, float]]):
        graph.clear()
        for u, v, weight in edges:
            graph.add_edge(u.strip(), v.strip(), weight)