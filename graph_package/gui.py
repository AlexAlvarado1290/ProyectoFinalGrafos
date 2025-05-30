"""
Interfaz gráfica para el programa de grafos
"""
import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog, ttk
from typing import Dict, List, Optional, Tuple
from .graph_model import GraphModel
from .config import DEFAULT_CSV, SAMPLE_EDGES

try:
    import matplotlib
    import csv
    matplotlib.use("TkAgg")
    import matplotlib.pyplot as plt
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    import networkx as nx
    GUI_AVAILABLE = True
except ModuleNotFoundError:
    GUI_AVAILABLE = False
    plt = None
    FigureCanvasTkAgg = None
    nx = None


class GraphApp:
    def __init__(self, master: tk.Tk):
        if not GUI_AVAILABLE:
            raise ImportError("Matplotlib y NetworkX son requeridos para la GUI")
            
        self.master = master
        self.master.title("Departamento de Guatemala – Grafo de municipios (Implementación Manual)")

        self.model = GraphModel()
        self.model.load_from_csv(DEFAULT_CSV, SAMPLE_EDGES)

        self.fig, self.ax = plt.subplots(figsize=(7, 6))
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.master)
        self.canvas.get_tk_widget().grid(row=0, column=0, rowspan=10, sticky="nsew")

        self._build_controls()

        self.pos: Dict[str, Tuple[float, float]] = {}
        self.visited_nodes: List[str] = []
        self.step_index = 0
        self.animation_running = False

        self._draw_graph()
        print("[INFO] Aplicación iniciada con implementación manual del grafo")

    def _build_controls(self):
        ctrl = tk.Frame(self.master)
        ctrl.grid(row=0, column=1, sticky="n")

        title_label = tk.Label(ctrl, text="Grafos Guatemala", font=("Arial", 12, "bold"))
        title_label.pack(pady=(5, 10))

        tk.Label(ctrl, text="Municipio inicial").pack(pady=(5, 0))
        self.start_var = tk.StringVar()
        self.start_cb = ttk.Combobox(ctrl, textvariable=self.start_var, state="readonly")
        self.start_cb.pack(pady=2, fill="x")

        ttk.Button(ctrl, text=" BFS", command=lambda: self._run_traversal(self.model.bfs)).pack(fill="x", pady=2)
        ttk.Button(ctrl, text=" DFS", command=lambda: self._run_traversal(self.model.dfs)).pack(fill="x", pady=2)
        ttk.Separator(ctrl, orient="horizontal").pack(fill="x", pady=5)

        tk.Label(ctrl, text="Edición", font=("Arial", 10, "bold")).pack(pady=(5, 2))
        ttk.Button(ctrl, text=" Agregar municipio", command=self._add_node).pack(fill="x", pady=2)
        ttk.Button(ctrl, text=" Eliminar municipio", command=self._remove_node).pack(fill="x", pady=2)
        ttk.Button(ctrl, text=" Agregar carretera", command=self._add_edge).pack(fill="x", pady=2)
        ttk.Button(ctrl, text=" Eliminar carretera", command=self._remove_edge).pack(fill="x", pady=2)
        ttk.Separator(ctrl, orient="horizontal").pack(fill="x", pady=5)

        tk.Label(ctrl, text="Archivo", font=("Arial", 10, "bold")).pack(pady=(5, 2))
        ttk.Button(ctrl, text="📂 Cargar CSV", command=self._load_csv).pack(fill="x", pady=2)
        ttk.Button(ctrl, text="💾 Guardar CSV", command=self._save_csv).pack(fill="x", pady=2)
        
        ttk.Separator(ctrl, orient="horizontal").pack(fill="x", pady=5)
        tk.Label(ctrl, text="Información", font=("Arial", 10, "bold")).pack(pady=(5, 2))
        self.info_label = tk.Label(ctrl, text="", justify="left", font=("Arial", 8))
        self.info_label.pack(pady=2, fill="x")

        self.master.columnconfigure(0, weight=1)
        self.master.rowconfigure(0, weight=1)

        self._refresh_combo()
        self._update_info()

    def _combo_dialog(self, title: str, prompt: str, values: List[str]) -> Optional[str]:
        if not values:
            return None
        dlg = tk.Toplevel(self.master)
        dlg.title(title)
        dlg.grab_set()
        dlg.geometry("300x150")
        dlg.resizable(False, False)
        
        tk.Label(dlg, text=prompt).pack(padx=10, pady=5)
        sel_var = tk.StringVar(value=values[0])
        cb = ttk.Combobox(dlg, textvariable=sel_var, values=values, state="readonly")
        cb.pack(padx=10, pady=5, fill="x")
        cb.focus_set()

        result: Optional[str] = None

        def on_ok():
            nonlocal result
            result = sel_var.get()
            dlg.destroy()

        def on_cancel():
            dlg.destroy()

        btn_frame = tk.Frame(dlg)
        btn_frame.pack(pady=10)
        ttk.Button(btn_frame, text="Aceptar", command=on_ok).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Cancelar", command=on_cancel).pack(side="right", padx=5)
        
        dlg.wait_window()
        return result

    def _sorted_nodes(self) -> List[str]:
        return sorted(self.model.G.nodes())

    def _refresh_combo(self):
        nodes = self._sorted_nodes()
        self.start_cb["values"] = nodes
        if self.start_var.get() not in nodes and nodes:
            self.start_var.set(nodes[0])

    def _update_info(self):
        """Actualizar información del grafo"""
        nodes = len(self.model.G)
        edges = len(list(self.model.G.edges()))
        info_text = f"Municipios: {nodes}\nCarreteras: {edges}"
        self.info_label.config(text=info_text)

    def _invalidate_layout(self):
        self.pos.clear()

    def _load_csv(self):
        path = filedialog.askopenfilename(filetypes=[("CSV", "*.csv")])
        if not path:
            return
        try:
            self.validar_archivo(path)
            self.model.load_from_csv(path)
            self._refresh_combo()
            self._update_info()
            self._invalidate_layout()
            self._draw_graph()
            messagebox.showinfo("Cargar", f"Grafo cargado desde {path}")
        except Exception as e:
            messagebox.showerror("Error de carga de archivo", e)
    def _save_csv(self):
     #  path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV", "*.csv")])
        path = DEFAULT_CSV
        if path:
            if self.model.save_to_csv(path):
                messagebox.showinfo("Guardar", f"Grafo guardado en {path}")
            else:
                messagebox.showerror("Error", "No se pudo guardar el archivo")

    def _add_node(self):
        name = simpledialog.askstring("Agregar municipio", "Nombre del municipio:")
        if not name:
            return
        name = name.strip()
        if name == "" or name in self.model.G:
            messagebox.showinfo("Municipio existente", f"El municipio '{name}' ya existe.")
            return
        
        self.model.G.add_node(name)
        self._refresh_combo()
        self._update_info()

        if len(self.model.G) > 1:
            response = messagebox.askyesno("Conectar", f"¿Desea conectar '{name}' con otro municipio?")
            if response:
                dest = self._combo_dialog("Conectar municipio", f"Conectar '{name}' con:", 
                                        [n for n in self._sorted_nodes() if n != name])
                if dest:
                    dist = simpledialog.askfloat("Distancia", f"Distancia km entre '{name}' y '{dest}':")
                    if dist is not None and dist > 0:
                        self.model.G.add_edge(name, dest, weight=dist)

        self._invalidate_layout()
        self._draw_graph()

    def _remove_node(self):
        node = self._combo_dialog("Eliminar municipio", "Seleccione municipio:", self._sorted_nodes())
        if node and node in self.model.G:
            self.model.G.remove_node(node)
            self._refresh_combo()
            self._update_info()
            self._invalidate_layout()
            self._draw_graph()

    def _add_edge(self):
        nodes = self._sorted_nodes()
        if len(nodes) < 2:
            messagebox.showinfo("Información", "Se necesitan al menos dos municipios.")
            return
        
        src = self._combo_dialog("Agregar carretera", "Municipio origen:", nodes)
        if not src:
            return
        
        dst = self._combo_dialog("Agregar carretera", "Municipio destino:", 
                               [n for n in nodes if n != src])
        if not dst:
            return
        
        if self.model.G.has_edge(src, dst):
            messagebox.showerror("Error", "La carretera ya existe.")
            return
        
        dist = simpledialog.askfloat("Distancia", f"Distancia km entre '{src}' y '{dst}':")
        if dist is None or dist <= 0:
            messagebox.showerror("Error", "Distancia debe ser mayor a 0.")
            return
        
        self.model.G.add_edge(src, dst, weight=dist)
        self._update_info()
        self._invalidate_layout()
        self._draw_graph()

    def _remove_edge(self):
        nodes = self._sorted_nodes()
        if len(nodes) < 2:
            return
        
        src = self._combo_dialog("Eliminar carretera", "Municipio origen:", nodes)
        if not src:
            return
        
        dst = self._combo_dialog("Eliminar carretera", "Municipio destino:", 
                               [n for n in nodes if n != src])
        if not dst:
            return
        
        if self.model.G.has_edge(src, dst):
            self.model.G.remove_edge(src, dst)
            self._update_info()
            self._invalidate_layout()
            self._draw_graph()
        else:
            messagebox.showerror("Error", "La carretera no existe.")

    def _draw_graph(self, highlight: Optional[List[str]] = None):
        nx_graph = self.model.manual_graph.to_networkx()
        if nx_graph is None:
            self.ax.clear()
            self.ax.text(0.5, 0.5, "NetworkX no disponible\npara visualización", 
                       ha='center', va='center', transform=self.ax.transAxes)
            self.canvas.draw()
            return

        if set(self.pos) != set(nx_graph.nodes()):
            if self.pos:
                fixed = {n: self.pos[n] for n in self.pos if n in nx_graph}
                self.pos = nx.spring_layout(nx_graph, seed=42, pos=fixed, fixed=list(fixed))
            else:
                self.pos = nx.spring_layout(nx_graph, seed=42)

        self.ax.clear()
        
        node_colors = []
        for node in nx_graph.nodes():
            if highlight and node in highlight:
                node_colors.append("orange")
            else:
                node_colors.append("#1f78b4")

        nx.draw_networkx(nx_graph, pos=self.pos, ax=self.ax, 
                       node_color=node_colors, with_labels=True, 
                       font_size=8, node_size=500)
        
        labels = nx.get_edge_attributes(nx_graph, "weight")
        nx.draw_networkx_edge_labels(nx_graph, pos=self.pos, 
                                   edge_labels=labels, ax=self.ax, font_size=7)
        
        self.ax.set_title("Grafo de Municipios (Implementación Manual)")
        self.ax.axis("off")
        self.canvas.draw()

    def _run_traversal(self, fn):
        start = self.start_var.get()
        if not start:
            messagebox.showwarning("Advertencia", "Seleccione un municipio inicial.")
            return
        
        try:
            print(f"\n[INFO] Ejecutando {fn.__name__.upper()} desde {start}")
            self.visited_nodes = fn(start)
            print(f"[INFO] Resultado: {self.visited_nodes}")
        except ValueError as e:
            messagebox.showerror("Error", str(e))
            return
        
        self._start_animation()

    def _start_animation(self):
        if self.animation_running:
            return
        self.step_index = 0
        self.animation_running = True
        self._animate_step()

    def _animate_step(self):
        if self.step_index <= len(self.visited_nodes):
            current_highlight = self.visited_nodes[:self.step_index]
            self._draw_graph(highlight=current_highlight)
            self.step_index += 1
            self.master.after(1000, self._animate_step)
        else:
            self.animation_running = False
            print("[INFO] Animación completada")

    def validar_archivo(self, path: str):
        with open(path, newline='', encoding='utf-8') as f:
            reader = csv.reader(f)
            for i, row in enumerate(reader, start=1):
                if len(row) != 3:
                    raise ValueError(f"Línea {i}: se esperaban 3 columnas, pero se encontraron {len(row)}.")
                u, v, w = row
                u, v = u.strip(), v.strip()
                if not u or not v:
                    raise ValueError(f"Línea {i}: los nombres de los nodos no pueden estar vacíos.")
                try:
                    weight = float(w)
                except ValueError:
                    raise ValueError(f"Línea {i}: el peso '{w}' no es un número válido.")