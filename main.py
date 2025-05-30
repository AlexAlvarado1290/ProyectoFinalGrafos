# """municipios_grafo_app.py — versión 30 may 2025
# -------------------------------------------------
# App para modelar los municipios del departamento de Guatemala como un grafo
# interactivo con animación BFS / DFS.

# Últimos cambios
# ───────────────
# • Al **agregar municipio** o **agregar carretera**, los nodos origen/destino se
#   eligen mediante *Combobox* para evitar errores de tipeo.
# • Se corrigieron todos los recortes de código y errores de sintaxis.
# • Probado en Python 3.10 + con NetworkX 3.x y Matplotlib 3.x.

# Requisitos
# ──────────
# ```bash
# pip install networkx matplotlib
# ```

# Uso
# ───
# ```bash
# python municipios_grafo_app.py         # GUI
# python municipios_grafo_app.py --nogui # solo lógica / pruebas rápidas
# ```
# """
# from __future__ import annotations

# import csv
# import os
# import sys
# from typing import Dict, List, Optional, Tuple

# import networkx as nx

# # ────────────────────────── Dependencias GUI ──────────────────────────
# TK_AVAILABLE = True
# try:
#     import tkinter as tk
#     from tkinter import filedialog, messagebox, simpledialog, ttk  # type: ignore
# except ModuleNotFoundError:
#     TK_AVAILABLE = False

# try:
#     import matplotlib
#     matplotlib.use("TkAgg" if TK_AVAILABLE else "Agg")
#     import matplotlib.pyplot as plt
#     from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg  # type: ignore
# except ModuleNotFoundError:
#     plt = None  # type: ignore
#     FigureCanvasTkAgg = None  # type: ignore

# # ───────────────────────── Datos de ejemplo ──────────────────────────
# DEFAULT_CSV = "edges.csv"
# SAMPLE_EDGES: List[Tuple[str, str, float]] = [
#     ("Guatemala City", "Mixco", 11),
#     ("Guatemala City", "Villa Nueva", 13),
#     ("Guatemala City", "Chinautla", 10),
#     ("Guatemala City", "Santa Catarina Pinula", 11),
#     ("Mixco", "San Lucas Sacatepequez", 13),
#     ("Mixco", "Villa Nueva", 18),
#     ("Villa Nueva", "Amatitlan", 16),
#     ("Villa Nueva", "San Miguel Petapa", 8),
#     ("San Miguel Petapa", "Amatitlan", 10),
#     ("Chinautla", "San Jose del Golfo", 19),
# ]

# # ─────────────────────────── Modelo de grafo ─────────────────────────
# class GraphModel:
#     def __init__(self):
#         self.G = nx.Graph()

#     # ---------- I/O ----------
#     def load_from_edges(self, edges: List[Tuple[str, str, float]]):
#         self.G.clear()
#         for u, v, w in edges:
#             self.G.add_edge(u.strip(), v.strip(), weight=float(w))

#     def load_from_csv(self, path: str, fallback: Optional[List[Tuple[str, str, float]]] = None):
#         if os.path.exists(path):
#             with open(path, newline="", encoding="utf-8") as f:
#                 edges = [(s, d, float(w)) for s, d, w in csv.reader(f)]
#             self.load_from_edges(edges)
#         elif fallback is not None:
#             self.load_from_edges(fallback)

#     def save_to_csv(self, path: str):
#         with open(path, "w", newline="", encoding="utf-8") as f:
#             writer = csv.writer(f)
#             for u, v, data in self.G.edges(data=True):
#                 writer.writerow([u, v, data.get("weight", 0)])

#     # ---------- Algoritmos ----------
#     def bfs(self, start: str) -> List[str]:
#         self._validate_node(start)
#         visited, queue, seen = [], [start], {start}
#         while queue:
#             cur = queue.pop(0)
#             visited.append(cur)
#             for n in self.G.neighbors(cur):
#                 if n not in seen:
#                     seen.add(n)
#                     queue.append(n)
#         return visited

#     def dfs(self, start: str) -> List[str]:
#         self._validate_node(start)
#         visited, stack, seen = [], [start], {start}
#         while stack:
#             cur = stack.pop()
#             visited.append(cur)
#             for n in self.G.neighbors(cur):
#                 if n not in seen:
#                     seen.add(n)
#                     stack.append(n)
#         return visited

#     def _validate_node(self, node: str):
#         if node not in self.G:
#             raise ValueError(f"Nodo desconocido: {node}")

# # ───────────────────────────── GUI ────────────────────────────────
# if TK_AVAILABLE:

#     class GraphApp:
#         def __init__(self, master: tk.Tk):
#             self.master = master
#             self.master.title("Departamento de Guatemala – Grafo de municipios")

#             # Modelo + datos iniciales
#             self.model = GraphModel()
#             self.model.load_from_csv(DEFAULT_CSV, SAMPLE_EDGES)

#             # Figura
#             self.fig, self.ax = plt.subplots(figsize=(7, 6))  # type: ignore[arg-type]
#             self.canvas = FigureCanvasTkAgg(self.fig, master=self.master)  # type: ignore[arg-type]
#             self.canvas.get_tk_widget().grid(row=0, column=0, rowspan=10, sticky="nsew")

#             self._build_controls()

#             self.pos: Dict[str, Tuple[float, float]] = {}
#             self.visited_nodes: List[str] = []
#             self.step_index = 0
#             self.animation_running = False

#             self._draw_graph()

#         # ───────────────── UI Helpers ─────────────────
#         def _build_controls(self):
#             ctrl = tk.Frame(self.master)
#             ctrl.grid(row=0, column=1, sticky="n")

#             # Inicio de recorrido
#             tk.Label(ctrl, text="Municipio inicial").pack(pady=(5, 0))
#             self.start_var = tk.StringVar()
#             self.start_cb = ttk.Combobox(ctrl, textvariable=self.start_var, state="readonly")
#             self.start_cb.pack(pady=2, fill="x")

#             ttk.Button(ctrl, text="BFS", command=lambda: self._run_traversal(self.model.bfs)).pack(fill="x", pady=2)
#             ttk.Button(ctrl, text="DFS", command=lambda: self._run_traversal(self.model.dfs)).pack(fill="x", pady=2)
#             ttk.Separator(ctrl, orient="horizontal").pack(fill="x", pady=5)

#             # Edición
#             ttk.Button(ctrl, text="Agregar municipio", command=self._add_node).pack(fill="x", pady=2)
#             ttk.Button(ctrl, text="Eliminar municipio", command=self._remove_node).pack(fill="x", pady=2)
#             ttk.Button(ctrl, text="Agregar carretera", command=self._add_edge).pack(fill="x", pady=2)
#             ttk.Button(ctrl, text="Eliminar carretera", command=self._remove_edge).pack(fill="x", pady=2)
#             ttk.Separator(ctrl, orient="horizontal").pack(fill="x", pady=5)

#             # CSV
#             ttk.Button(ctrl, text="Cargar CSV", command=self._load_csv).pack(fill="x", pady=2)
#             ttk.Button(ctrl, text="Guardar CSV", command=self._save_csv).pack(fill="x", pady=2)

#             # Configurar resize
#             self.master.columnconfigure(0, weight=1)
#             self.master.rowconfigure(0, weight=1)

#             self._refresh_combo()

#         # -------- Combobox helper --------
#         def _combo_dialog(self, title: str, prompt: str, values: List[str]) -> Optional[str]:
#             if not values:
#                 return None
#             dlg = tk.Toplevel(self.master)
#             dlg.title(title)
#             dlg.grab_set()
#             tk.Label(dlg, text=prompt).pack(padx=10, pady=5)
#             sel_var = tk.StringVar(value=values[0])
#             cb = ttk.Combobox(dlg, textvariable=sel_var, values=values, state="readonly")
#             cb.pack(padx=10, pady=5)
#             cb.focus_set()

#             result: Optional[str] = None

#             def on_ok():
#                 nonlocal result
#                 result = sel_var.get()
#                 dlg.destroy()

#             ttk.Button(dlg, text="Aceptar", command=on_ok).pack(side="left", padx=(20, 5), pady=10)
#             ttk.Button(dlg, text="Cancelar", command=dlg.destroy).pack(side="right", padx=(5, 20), pady=10)
#             dlg.wait_window()
#             return result

#         # -------- Varios helpers --------
#         def _sorted_nodes(self) -> List[str]:
#             return sorted(self.model.G.nodes())

#         def _refresh_combo(self):
#             self.start_cb["values"] = self._sorted_nodes()
#             if self.start_var.get() not in self.model.G and self.model.G.nodes():
#                 self.start_var.set(next(iter(self.model.G.nodes())))

#         def _invalidate_layout(self):
#             self.pos.clear()

#         # ────────────────── CSV I/O ──────────────────
#         def _load_csv(self):
#             path = filedialog.askopenfilename(filetypes=[("CSV", "*.csv")])
#             if path:
#                 self.model.load_from_csv(path)
#                 self._refresh_combo()
#                 self._invalidate_layout()
#                 self._draw_graph()

#         def _save_csv(self):
#             path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV", "*.csv")])
#             if path:
#                 self.model.save_to_csv(path)
#                 messagebox.showinfo("Guardar", f"Grafo guardado en {path}")

#         # ──────────────────── NODOS ────────────────────
#         def _add_node(self):
#             name = simpledialog.askstring("Agregar municipio", "Nombre del municipio:")
#             if not name:
#                 return
#             name = name.strip()
#             if name == "" or name in self.model.G:
#                 messagebox.showinfo("Municipio existente", f"El municipio '{name}' ya existe.")
#                 return
#             self.model.G.add_node(name)
#             self._refresh_combo()

#             if len(self.model.G) > 1:
#                 dest = self._combo_dialog("Conectar municipio", f"Conectar '{name}' con:", [n for n in self._sorted_nodes() if n != name])
#                 if dest:
#                     dist = simpledialog.askfloat("Distancia", f"Distancia km entre '{name}' y '{dest}':")
#                     if dist is not None:
#                         self.model.G.add_edge(name, dest, weight=dist)

#             self._invalidate_layout()
#             self._draw_graph()

#         def _remove_node(self):
#             node = self._combo_dialog("Eliminar municipio", "Seleccione municipio:", self._sorted_nodes())
#             if node and node in self.model.G:
#                 self.model.G.remove_node(node)
#                 self._refresh_combo()
#                 self._invalidate_layout()
#                 self._draw_graph()

#         # ──────────────────── ARISTAS ────────────────────
#         def _add_edge(self):
#             nodes = self._sorted_nodes()
#             if len(nodes) < 2:
#                 messagebox.showinfo("Información", "Se necesitan al menos dos municipios.")
#                 return
#             src = self._combo_dialog("Agregar carretera", "Municipio origen:", nodes)
#             if not src:
#                 return
#             dst = self._combo_dialog("Agregar carretera", "Municipio destino:", [n for n in nodes if n != src])
#             if not dst:
#                 return
#             if self.model.G.has_edge(src, dst):
#                 messagebox.showerror("Error", "La carretera ya existe.")
#                 return
#             dist = simpledialog.askfloat("Distancia", f"Distancia km entre '{src}' y '{dst}':")
#             if dist is None:
#                 return
#             self.model.G.add_edge(src, dst, weight=dist)
#             self._invalidate_layout()
#             self._draw_graph()

#         def _remove_edge(self):
#             nodes = self._sorted_nodes()
#             if len(nodes) < 2:
#                 return
#             src = self._combo_dialog("Eliminar carretera", "Municipio origen:", nodes)
#             if not src:
#                 return
#             dst = self._combo_dialog("Eliminar carretera", "Municipio destino:", [n for n in nodes if n != src])
#             if not dst:
#                 return
#             if self.model.G.has_edge(src, dst):
#                 self.model.G.remove_edge(src, dst)
#                 self._invalidate_layout()
#                 self._draw_graph()
#             else:
#                 messagebox.showerror("Error", "La carretera no existe.")

#         # ─────────────── Dibujo & animación ───────────────
#         def _draw_graph(self, highlight: Optional[List[str]] = None):
#             if set(self.pos) != set(self.model.G):
#                 if self.pos:
#                     fixed = {n: self.pos[n] for n in self.pos if n in self.model.G}
#                     self.pos = nx.spring_layout(self.model.G, seed=42, pos=fixed, fixed=list(fixed))
#                 else:
#                     self.pos = nx.spring_layout(self.model.G, seed=42)

#             self.ax.clear()
#             node_colors = ["orange" if highlight and n in highlight else "#1f78b4" for n in self.model.G.nodes()]
#             nx.draw_networkx(self.model.G, pos=self.pos, ax=self.ax, node_color=node_colors, with_labels=True, font_size=8)
#             labels = nx.get_edge_attributes(self.model.G, "weight")
#             nx.draw_networkx_edge_labels(self.model.G, pos=self.pos, edge_labels=labels, ax=self.ax, font_size=7)
#             self.ax.axis("off")
#             self.canvas.draw()

#         # ─────────────── Recorridos animados ───────────────
#         def _run_traversal(self, fn):
#             start = self.start_var.get()
#             if not start:
#                 messagebox.showwarning("Advertencia", "Seleccione un municipio inicial.")
#                 return
#             try:
#                 self.visited_nodes = fn(start)
#             except ValueError as e:
#                 messagebox.showerror("Error", str(e))
#                 return
#             self._start_animation()

#         def _start_animation(self):
#             if self.animation_running:
#                 return
#             self.step_index = 0
#             self.animation_running = True
#             self._animate_step()

#         def _animate_step(self):
#             if self.step_index <= len(self.visited_nodes):
#                 self._draw_graph(highlight=self.visited_nodes[: self.step_index])
#                 self.step_index += 1
#                 self.master.after(800, self._animate_step)
#             else:
#                 self.animation_running = False

# # ────────────────────────── MAIN ──────────────────────────
# if __name__ == "__main__":
#     if "--nogui" in sys.argv or not TK_AVAILABLE:
#         print("[INFO] Ejecutando en modo sin GUI…")
#         model = GraphModel()
#         model.load_from_csv(DEFAULT_CSV, SAMPLE_EDGES)
#         print("Nodos:", model.G.nodes())
#         print("Aristas:", model.G.edges(data=True))
#         sys.exit()

#     root = tk.Tk()  # type: ignore[arg-type]
#     GraphApp(root)  # type: ignore[arg-type]
#     root.mainloop()

from __future__ import annotations

import sys
import tkinter as tk
from graph_package import (
    GraphApp, 
    GUI_AVAILABLE
)


def main():
    
    if not GUI_AVAILABLE:
        print("[ERROR] GUI no disponible.")
        print("Instale las dependencias requeridas:")
        print("  pip install matplotlib networkx tkinter")
        print("\nLa aplicación requiere interfaz gráfica para funcionar.")
        sys.exit(1)
    
    try:
        root = tk.Tk()
        root.geometry("1000x700")
        app = GraphApp(root)
        print("[INFO] Aplicación GUI iniciada correctamente")
        root.mainloop()
        
    except ImportError as e:
        print(f"[ERROR] Faltan dependencias requeridas: {e}")
        print("Instale con: pip install matplotlib networkx")
        sys.exit(1)
        
    except Exception as e:
        print(f"[ERROR] Error al iniciar la aplicación: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()