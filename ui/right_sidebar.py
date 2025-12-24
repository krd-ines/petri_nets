import sys
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, 
    QGroupBox, QGraphicsView, QFrame, QTextEdit, QDialog, 
    QFileDialog, QMessageBox
)
from PyQt6.QtCore import Qt, QRectF, QPointF, QSize
from PyQt6.QtGui import QPainter, QFont, QColor, QImage

# Custom Module Imports
from ui.IconFactory import IconFactory
from tree.algo import build_tree_with_history 
from ui.graph import build_scene_from_graph
from tree.properties import is_bounded, is_net_live, is_resettable, is_quasi_live

class AnalysisPanel(QFrame):
    """The main sidebar panel for Petri Net tree analysis."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumWidth(400)
        self.setStyleSheet("QFrame { background-color: #f8f9fa; border-left: 1px solid #dee2e6; }")
        
        self.history = []
        self.current_step = 0
        self.net = None
        self.initial_marking = None
        
        self.init_ui()

    def init_ui(self):
        """Modular UI construction."""
        self.main_layout = QHBoxLayout(self)
        self.main_layout.setContentsMargins(10, 10, 10, 10)
        self.main_layout.setSpacing(12)

        self.setup_left_column()   
        self.setup_right_column()
        self.setup_connections()

    def setup_left_column(self):
        """Setup for the graph view and step-by-step navigation."""
        left_col = QVBoxLayout()
        left_col.setSpacing(10)

        self.view = QGraphicsView()
        self.view.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.view.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)
        self.view.setStyleSheet("background-color: white; border: 1px solid #dee2e6; border-radius: 4px;")
        self.view.setMinimumHeight(400) 
        left_col.addWidget(self.view, stretch=10)

        step_container = QFrame()
        step_container.setStyleSheet("background-color: #ffffff; border: 1px solid #dee2e6; border-radius: 4px;")
        step_container.setFixedHeight(120)
        step_layout = QVBoxLayout(step_container)
        
        nav_layout = QHBoxLayout()
        self.btn_prev = QPushButton("◀ Back")
        self.btn_next = QPushButton("Next ▶")
        
        btn_style = "QPushButton { padding: 8px; font-weight: bold; } QPushButton:pressed { padding-top: 10px; }"
        for b in [self.btn_prev, self.btn_next]:
            b.setCursor(Qt.CursorShape.PointingHandCursor)
            b.setStyleSheet(btn_style)

        self.step_counter = QLabel("0 / 0")
        self.step_counter.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.step_counter.setStyleSheet("font-weight: bold; color: #495057; border: none; font-size: 13px;")
        
        nav_layout.addWidget(self.btn_prev)
        nav_layout.addStretch(1)
        nav_layout.addWidget(self.step_counter)
        nav_layout.addStretch(1)
        nav_layout.addWidget(self.btn_next)
        step_layout.addLayout(nav_layout)
        
        self.step_text = QLabel("Ready...")
        self.step_text.setWordWrap(True)
        self.step_text.setStyleSheet("color: #6c757d; font-style: italic; font-size: 14px; border: none;")
        step_layout.addWidget(self.step_text)
        
        left_col.addWidget(step_container)
        self.main_layout.addLayout(left_col)

    def setup_right_column(self):
        """Setup for control buttons, properties, and legend."""
        right_col = QVBoxLayout()
        #right_col.setSpacing(10)

        self._setup_action_buttons(right_col)
        self._setup_toolbar(right_col)
        self._setup_properties_panel(right_col)
        self._setup_legend_panel(right_col)
        
        right_col.addStretch(1) 
        self.main_layout.addLayout(right_col)

    def _setup_action_buttons(self, layout):
        base = "QPushButton { font-weight: bold; border-radius: 8px; padding: 10px; color: white; }"
        
        self.btn_step_init = QPushButton("Step Build")
        self.btn_step_init.setStyleSheet(base + "QPushButton { background-color: #2980b9; } QPushButton:hover { background-color: #3498db; }")
        
        self.btn_full = QPushButton("Full Build")
        self.btn_full.setStyleSheet(base + "QPushButton { background-color: #27ae60; } QPushButton:hover { background-color: #2ecc71; }")
        
        self.btn_maximize = QPushButton("Full View")
        self.btn_maximize.setStyleSheet(base + "QPushButton { background-color: #f39c12; } QPushButton:hover { background-color: #f1c40f; }")

        for b in [self.btn_step_init, self.btn_full, self.btn_maximize]:
            b.setCursor(Qt.CursorShape.PointingHandCursor)
            b.setFixedHeight(42)
            layout.addWidget(b)

    def _setup_toolbar(self, layout):
        tool_layout = QHBoxLayout()
        style = "QPushButton { background-color: #fff; border: 1px solid #ced4da; border-radius: 4px; }"
        
        self.btn_zoom_in = self._create_icon_btn("zoom_in", "Zoom In", style)
        self.btn_zoom_out = self._create_icon_btn("zoom_out", "Zoom Out", style)
        self.btn_zoom_reset = self._create_icon_btn("reset_zoom", "Reset Zoom", style)
        self.btn_save_img = self._create_icon_btn("save_image", "Save Image", style)

        for b in [self.btn_zoom_in, self.btn_zoom_out, self.btn_zoom_reset, self.btn_save_img]:
            tool_layout.addWidget(b)
        layout.addLayout(tool_layout)

    def _create_icon_btn(self, icon, tip, style):
        btn = QPushButton()
        btn.setIcon(IconFactory.create_icon(icon))
        btn.setIconSize(QSize(24, 24))
        btn.setToolTip(tip)
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn.setStyleSheet(style + " QPushButton:hover { background-color: #e9ecef; border-color: #adb5bd; }")
        btn.setFixedSize(40, 40)
        return btn

    def _setup_properties_panel(self, layout):
        group = QGroupBox("Properties")
        # Added specific font-size and margin to the group title
        group.setStyleSheet("""
            QGroupBox { 
                font-weight: bold; 
                font-size: 15px;
                color: #2c3e50; 
                padding-top: 25px; 
                border: 1px solid #dcdde1;
                border-radius: 6px;
                margin-top: 10px;
            }
        """)
        vbox = QVBoxLayout(group)
        vbox.setSpacing(8)

        self.prop_bounded = QLabel("-")
        self.prop_quasi_live = QLabel("-")
        self.prop_live = QLabel("-")
        self.prop_resettable = QLabel("-")
        
        def add_row(name, widget):
            f = QFrame()
            # Restore the clean white-card look
            f.setStyleSheet("""
                QFrame { 
                    background: #ffffff; 
                    border: 1px solid #f1f2f6; 
                    border-radius: 5px; 
                    padding: 5px; 
                }
            """)
            l = QHBoxLayout(f)
            title = QLabel(f"<b>{name}:</b>")
            title.setStyleSheet("color: #34495e; font-size: 13px; border: none;")
            l.addWidget(title)
            l.addStretch()
            l.addWidget(widget)
            vbox.addWidget(f)

        add_row("Bounded", self.prop_bounded)
        add_row("Quasi-Live", self.prop_quasi_live)
        add_row("Live", self.prop_live)
        add_row("Resettable", self.prop_resettable)
        layout.addWidget(group)

    def _setup_legend_panel(self, layout):
        group = QGroupBox("Node Legend")
        group.setStyleSheet("""
            QGroupBox { 
                font-weight: bold; 
                font-size: 14px;
                color: #2c3e50; 
                border: 1px solid #eee; 
                margin-top: 15px; 
                padding-top: 20px;
            }
        """)
        vbox = QVBoxLayout(group)
        vbox.setSpacing(6)
        
        def add_item(color, text):
            row = QHBoxLayout()
            row.setContentsMargins(5, 2, 5, 2)
            box = QFrame()
            box.setFixedSize(16, 16)
            # Added a slight border-radius to the legend boxes for a modern look
            box.setStyleSheet(f"background: {color.name()}; border: 1px solid #555; border-radius: 3px;")
            
            lbl = QLabel(text)
            lbl.setStyleSheet("font-weight: bold; font-size: 13px; color: #2c3e50; border: none;")
            
            row.addWidget(box)
            row.addWidget(lbl)
            row.addStretch()
            vbox.addLayout(row)

        add_item(QColor(200, 200, 255), "New Marking")
        add_item(QColor(200, 255, 200), "Done Marking")
        add_item(QColor(255, 200, 200), "Dead-End")
        layout.addWidget(group)

    def setup_connections(self):
        self.btn_full.clicked.connect(self.run_full)
        self.btn_step_init.clicked.connect(self.run_step_init)
        self.btn_next.clicked.connect(self.go_next)
        self.btn_prev.clicked.connect(self.go_back)
        self.btn_zoom_in.clicked.connect(lambda: self.view.scale(1.2, 1.2))
        self.btn_zoom_out.clicked.connect(lambda: self.view.scale(1/1.2, 1/1.2))
        self.btn_zoom_reset.clicked.connect(self.reset_view)
        self.btn_maximize.clicked.connect(self.open_full_view)
        self.btn_save_img.clicked.connect(self.save_graph_as_image)

    # --- LOGIC METHODS ---

    def set_net_data(self, net, m0):
        self.net = net
        self.initial_marking = m0

    def run_full(self):
        if not self.net: return
        _, self.history = build_tree_with_history(self.net, self.initial_marking)
        self.current_step = len(self.history) - 1
        self.update_ui()

    def run_step_init(self):
        if not self.net: return
        _, self.history = build_tree_with_history(self.net, self.initial_marking)
        self.current_step = 0
        self.update_ui()

    def go_next(self):
        if self.current_step < len(self.history) - 1:
            self.current_step += 1
            self.update_ui()

    def go_back(self):
        if self.current_step > 0:
            self.current_step -= 1
            self.update_ui()

    def update_ui(self):
        if not self.history: return
        graph, msg = self.history[self.current_step]
        scene = build_scene_from_graph(graph)
        self.view.setScene(scene)
        
        rect = scene.itemsBoundingRect()
        if not rect.isNull():
            rect.adjust(-100, -100, 100, 100)
            scene.setSceneRect(rect)
            self.view.fitInView(rect, Qt.AspectRatioMode.KeepAspectRatio)
            if self.view.transform().m11() > 1.0: self.view.resetTransform()
            self.view.centerOn(rect.center())

        total = len(self.history) - 1
        self.step_counter.setText(f"{self.current_step} / {total}")
        self.step_text.setText(msg)
        self.btn_next.setEnabled(self.current_step < total)
        self.btn_prev.setEnabled(self.current_step > 0)
        
        if self.current_step == total: self.calculate_properties(graph)
        else: self.reset_properties_labels()

    def calculate_properties(self, graph):
        bound = is_bounded(graph)
        live = is_net_live(graph, self.net.transition())
        qlive = is_quasi_live(graph, self.net.transition())
        reset = is_resettable(graph)

        def set_lbl(lbl, val, text_override=None):
            color = "#27ae60" if val else "#e74c3c"
            lbl.setText(text_override if text_override else ("YES" if val else "NO"))
            lbl.setStyleSheet(f"color: {color}; font-weight: bold; border: none;")

        set_lbl(self.prop_bounded, bound, f"YES ({bound})" if bound else "NO")
        set_lbl(self.prop_live, live)
        set_lbl(self.prop_quasi_live, qlive)
        set_lbl(self.prop_resettable, reset)

    def reset_properties_labels(self):
        for lbl in [self.prop_bounded, self.prop_quasi_live, self.prop_live, self.prop_resettable]:
            lbl.setText("-")
            lbl.setStyleSheet("color: #adb5bd; font-weight: bold; border: none;")

    def reset_view(self):
        if self.view.scene():
            self.view.fitInView(self.view.scene().itemsBoundingRect().adjusted(-50, -50, 50, 50), Qt.AspectRatioMode.KeepAspectRatio)
            if self.view.transform().m11() > 1.0: self.view.resetTransform()

    def open_full_view(self):
        if self.view.scene():
            FullGraphWindow(self.view.scene(), self).exec()

    def save_graph_as_image(self):
        scene = self.view.scene()
        if not scene: return
        path, _ = QFileDialog.getSaveFileName(self, "Save Image", "", "PNG Files (*.png)")
        if path:
            rect = scene.itemsBoundingRect().adjusted(-20, -20, 20, 20)
            img = QImage(rect.size().toSize(), QImage.Format.Format_ARGB32)
            img.fill(Qt.GlobalColor.white)
            painter = QPainter(img)
            scene.render(painter, target=QRectF(img.rect()), source=rect)
            painter.end()
            img.save(path)

