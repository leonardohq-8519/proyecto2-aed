import os
import traceback
import faulthandler
import sys
import math

os.add_dll_directory(r"C:\msys64\mingw64\bin")

log_file = open("crash_log.txt", "w", encoding="utf-8")
faulthandler.enable(file=log_file)
faulthandler.enable()

def capturar_excepcion(exc_type, exc_value, exc_tb):
    mensaje = "".join(traceback.format_exception(exc_type, exc_value, exc_tb))
    print(mensaje, file=sys.stderr)
    log_file.write(mensaje)
    log_file.flush()

sys.excepthook = capturar_excepcion

import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QSlider, QSpinBox, QLabel, QFrame, QComboBox, QCheckBox
)
from PySide6.QtCore import Qt, QTimer

import graph_anim

class GraphVisualizer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Constructor y Visualizador de Grafos (C++ + PySide6)")
        self.resize(1000, 750)

        self.g = graph_anim.Graph()
        self.snapshots = []
        self.current_step = 0
        self.node_pos = {}      
        self.selected_node = None

        self._setup_ui()
        self.g.set_callback(self.record_snapshot)

        for u, v in [(1, 2), (1, 3), (2, 4)]:
            self.g.add_edge(u, v)

        if self.snapshots:
            self.current_step = len(self.snapshots) - 1
            self.render_snapshot(self.current_step)

    def _setup_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)

        builder_bar = QHBoxLayout()

        self.spin_node = QSpinBox()
        self.spin_node.setRange(0, 999)
        self.spin_node.setValue(5)
        btn_add_node = QPushButton("+ Nodo")
        btn_add_node.clicked.connect(self.ui_add_node)

        self.spin_u = QSpinBox()
        self.spin_u.setRange(0, 999)
        self.spin_u.setValue(1)
        self.spin_v = QSpinBox()
        self.spin_v.setRange(0, 999)
        self.spin_v.setValue(5)
        self.chk_directed = QCheckBox("Dirigida")
        self.chk_directed.setChecked(False)
        btn_add_edge = QPushButton("+ Arista")
        btn_add_edge.clicked.connect(self.ui_add_edge)

        self.combo_algo = QComboBox()
        self.combo_algo.addItems(["BFS", "Tarjan (Orden Topológico)"])

        self.spin_start = QSpinBox()
        self.spin_start.setRange(0, 999)
        self.spin_start.setValue(1)

        self.combo_algo.currentTextChanged.connect(
            lambda text: self.spin_start.setEnabled(text != "Tarjan (Orden Topológico)")
        )

        btn_run = QPushButton("▶ Ejecutar")
        btn_run.setStyleSheet("font-weight: bold;")
        btn_run.clicked.connect(self.ui_run_selected)

        btn_clear = QPushButton("🗑 Limpiar")
        btn_clear.clicked.connect(self.clear_graph)

        builder_bar.addWidget(QLabel("Nodo:"))
        builder_bar.addWidget(self.spin_node)
        builder_bar.addWidget(btn_add_node)
        builder_bar.addWidget(self._v_separator())

        builder_bar.addWidget(QLabel("Arista (u, v):"))
        builder_bar.addWidget(self.spin_u)
        builder_bar.addWidget(self.spin_v)
        builder_bar.addWidget(self.chk_directed)
        builder_bar.addWidget(btn_add_edge)
        builder_bar.addWidget(self._v_separator())

        builder_bar.addWidget(QLabel("Algoritmo:"))
        builder_bar.addWidget(self.combo_algo)
        builder_bar.addWidget(QLabel("Inicio:"))
        builder_bar.addWidget(self.spin_start)
        builder_bar.addWidget(btn_run)
        builder_bar.addStretch()
        builder_bar.addWidget(btn_clear)

        main_layout.addLayout(builder_bar)

        self.fig, self.ax = plt.subplots(figsize=(8, 6))
        self.canvas = FigureCanvasQTAgg(self.fig)
        self.canvas.mpl_connect("button_press_event", self.on_canvas_click)
        main_layout.addWidget(self.canvas)

        self.status_label = QLabel(
            "Tip: Haz clic en un espacio vacío para crear un nodo, o clic en dos nodos para unirlos."
        )
        main_layout.addWidget(self.status_label)

        controls = QHBoxLayout()
        self.btn_prev = QPushButton("⏮ Anterior")
        self.btn_play = QPushButton("▶ Play")
        self.btn_next = QPushButton("Siguiente ⏭")
        self.speed_slider = QSlider(Qt.Horizontal)
        self.speed_slider.setRange(100, 1500)
        self.speed_slider.setValue(500)

        controls.addWidget(self.btn_prev)
        controls.addWidget(self.btn_play)
        controls.addWidget(self.btn_next)
        controls.addWidget(QLabel("Velocidad:"))
        controls.addWidget(self.speed_slider)
        main_layout.addLayout(controls)

        self.timer = QTimer()
        self.timer.timeout.connect(self.next_step)
        self.btn_prev.clicked.connect(self.prev_step)
        self.btn_next.clicked.connect(self.next_step)
        self.btn_play.clicked.connect(self.toggle_play)
        self.speed_slider.valueChanged.connect(self.timer.setInterval)

    def _v_separator(self):
        line = QFrame()
        line.setFrameShape(QFrame.VLine)
        line.setFrameShadow(QFrame.Sunken)
        return line


    def ui_add_node(self):
        u = self.spin_node.value()
        self.add_node(u)
        self.spin_node.setValue(u + 1)

    def add_node(self, u, pos=None):
        if pos is not None:
            self.node_pos[u] = pos

        if hasattr(self.g, "add_node"):
            self.g.add_node(u)
        else:
            self.snapshots.append({
                "adj": {**{k: list(v) for k, v in self.g.adj.items()}, u: []},
                "active": -1,
                "visited": set(),
            })

        self.current_step = len(self.snapshots) - 1
        self.render_snapshot(self.current_step)
        self.status_label.setText(f"Nodo {u} añadido.")

    def ui_add_edge(self):
        u = self.spin_u.value()
        v = self.spin_v.value()
        self.add_edge(u, v)

    def add_edge(self, u, v):
        if u == v:
            self.status_label.setText("No se permiten auto-bucles (u == v).")
            return

        is_directed = self.chk_directed.isChecked()
        self.g.add_edge(u, v, is_directed)

        self.current_step = len(self.snapshots) - 1
        self.render_snapshot(self.current_step)

        flecha = "→" if is_directed else "—"
        self.status_label.setText(f"Arista ({u} {flecha} {v}) añadida.")

    def ui_run_bfs(self):
        start = self.spin_start.value()
        if start not in self.g.adj and start not in self.node_pos:
            self.status_label.setText(f"El nodo {start} no existe en el grafo.")
            return

        self.selected_node = None
        start_step = len(self.snapshots)
        self.g.bfs(start)

        if len(self.snapshots) > start_step:
            self.current_step = start_step
            self.render_snapshot(self.current_step)
            self.timer.start(self.speed_slider.value())
            self.btn_play.setText("⏸ Pausar")
            self.status_label.setText(f"Ejecutando BFS desde el nodo {start}...")

    def ui_run_tarjan(self):
        if not self.g.adj and not self.node_pos:
            self.status_label.setText("El grafo está vacío.")
            return

        self.timer.stop()
        self.selected_node = None
        start_step = len(self.snapshots)

        sccs = self.g.tarjan_scc()

        topo_sccs = sccs

        base_adj = {u: list(nbrs) for u, nbrs in self.g.adj.items()}
        progressive_scc_map = {}
        revealed_labels = []

        for scc_idx, component in enumerate(topo_sccs):
            for node in component:
                progressive_scc_map[node] = scc_idx

            comp_str = f"{{{', '.join(map(str, component))}}}"
            revealed_labels.append(comp_str)

            self.snapshots.append({
                "adj": base_adj,
                "active": -1,
                "visited": set(),
                "scc_map": dict(progressive_scc_map),
                "topo_text": "Orden Topológico: " + " → ".join(revealed_labels),
            })

        if len(self.snapshots) > start_step:
            self.current_step = start_step
            self.render_snapshot(self.current_step)
            self.timer.start(self.speed_slider.value())
            self.btn_play.setText("⏸ Pausar")
            self.status_label.setText("Calculando SCCs y Orden Topológico (Tarjan)...")

    def clear_graph(self):
        self.timer.stop()
        self.btn_play.setText("▶ Play")
        self.g = graph_anim.Graph()
        self.g.set_callback(self.record_snapshot)
        self.snapshots.clear()
        self.node_pos.clear()
        self.selected_node = None
        self.current_step = 0
        self.spin_node.setValue(1)

        self.ax.clear()
        self._configure_axes()
        self.canvas.draw()
        self.status_label.setText("Grafo limpiado.")


    def on_canvas_click(self, event):
        if event.inaxes != self.ax or event.button != 1:
            return

        clicked_node = None
        for node, (nx_pos, ny_pos) in self.node_pos.items():
            if math.hypot(event.xdata - nx_pos, event.ydata - ny_pos) < 0.12:
                clicked_node = node
                break

        if clicked_node is not None:
            if self.selected_node is None:
                self.selected_node = clicked_node
                self.status_label.setText(
                    f"Nodo {clicked_node} seleccionado: haz clic en otro nodo para conectar."
                )
                self.render_snapshot(self.current_step)
            elif self.selected_node == clicked_node:
                self.selected_node = None
                self.status_label.setText("Selección cancelada.")
                self.render_snapshot(self.current_step)
            else:
                u, v = self.selected_node, clicked_node
                self.selected_node = None
                self.add_edge(u, v)
        else:
            if self.selected_node is not None:
                self.selected_node = None
                self.render_snapshot(self.current_step)
                return

            new_id = max(self.node_pos.keys(), default=0) + 1
            self.spin_node.setValue(new_id + 1)
            self.add_node(new_id, pos=(event.xdata, event.ydata))

    def record_snapshot(self):
        self.snapshots.append({
            "adj": {u: list(nbrs) for u, nbrs in self.g.adj.items()},
            "active": self.g.active_node,
            "visited": set(self.g.visited),
            "scc_map": {},
            "topo_text": "",
        })

    def _configure_axes(self):
        self.ax.set_xlim(-1.2, 1.2)
        self.ax.set_ylim(-1.2, 1.2)
        self.ax.set_xticks([])
        self.ax.set_yticks([])

    def render_snapshot(self, idx):
        if not self.snapshots:
            return

        snap = self.snapshots[idx]
        G = nx.DiGraph()
        for u, neighbors in snap["adj"].items():
            G.add_node(u)
            for v in neighbors:
                G.add_edge(u, v)

        missing = [n for n in G.nodes if n not in self.node_pos]
        if missing:
            if not self.node_pos:
                self.node_pos.update(nx.spring_layout(G, seed=42))
            else:
                fixed = [n for n in G.nodes if n in self.node_pos]
                computed = nx.spring_layout(G, pos=self.node_pos, fixed=fixed, seed=42)
                for n in missing:
                    self.node_pos[n] = computed[n]

        scc_palette = [
            "#ff9999", "#99ff99", "#99ccff", "#ffcc99",
            "#cc99ff", "#ffff99", "#99ffff", "#f4a4c0"
        ]
        scc_map = snap.get("scc_map", {})

        colors, border_colors, border_widths = [], [], []
        for node in G.nodes:
            if node in scc_map:
                colors.append(scc_palette[scc_map[node] % len(scc_palette)])
            elif node == snap["active"]:
                colors.append("tomato")
            elif node in snap["visited"]:
                colors.append("lightgreen")
            else:
                colors.append("skyblue")

            if node == self.selected_node:
                border_colors.append("darkorange")
                border_widths.append(3.5)
            else:
                border_colors.append("#2b5c8f")
                border_widths.append(1.5)

        self.ax.clear()

        undirected_edges = []
        directed_edges = []

        for u, v in G.edges():
            if G.has_edge(v, u):
                if u < v:
                    undirected_edges.append((u, v))
            else:
                directed_edges.append((u, v))

        if undirected_edges:
            nx.draw_networkx_edges(
                G, self.node_pos, ax=self.ax, edgelist=undirected_edges,
                width=2, edge_color="#666666", arrows=False
            )

        if directed_edges:
            nx.draw_networkx_edges(
                G, self.node_pos, ax=self.ax, edgelist=directed_edges,
                width=2, edge_color="#2b5c8f", arrows=True, arrowsize=20,
                node_size=1100, connectionstyle="arc3,rad=0.06"
            )

        nx.draw_networkx_nodes(
            G, self.node_pos, ax=self.ax, node_color=colors,
            edgecolors=border_colors, linewidths=border_widths, node_size=1100
        )
        nx.draw_networkx_labels(G, self.node_pos, ax=self.ax, font_weight="bold")

        topo_text = snap.get("topo_text", "")
        if topo_text:
            self.ax.text(
                0.0, -1.12, topo_text, ha="center", va="center",
                fontsize=10, fontweight="bold",
                bbox=dict(boxstyle="round,pad=0.4", facecolor="#f0f4f8", edgecolor="#2b5c8f")
            )

        self._configure_axes()
        self.ax.set_title(f"Paso {idx + 1} / {len(self.snapshots)}")
        self.canvas.draw()

    def next_step(self):
        if self.current_step < len(self.snapshots) - 1:
            self.current_step += 1
            self.render_snapshot(self.current_step)
        else:
            self.timer.stop()
            self.btn_play.setText("▶ Play")

    def prev_step(self):
        self.timer.stop()
        self.btn_play.setText("▶ Play")
        if self.current_step > 0:
            self.current_step -= 1
            self.render_snapshot(self.current_step)

    def toggle_play(self):
        if self.timer.isActive():
            self.timer.stop()
            self.btn_play.setText("▶ Play")
        elif self.snapshots:
            if self.current_step >= len(self.snapshots) - 1:
                self.current_step = 0
            self.timer.start(self.speed_slider.value())
            self.btn_play.setText("⏸ Pausar")

    def ui_run_selected(self):
        algo = self.combo_algo.currentText()
        if algo == "BFS":
            self.ui_run_bfs()
        elif algo == "Tarjan (Orden Topológico)":
            self.ui_run_tarjan()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = GraphVisualizer()
    win.show()
    sys.exit(app.exec())