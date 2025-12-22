import sys
import os
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QDockWidget,
    QTextEdit, QListWidget, QTabWidget, QToolBar, QScrollArea, QLabel,
    QMessageBox, QInputDialog, QMenu, QSizePolicy
)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QAction, QPixmap

# Custom Modules
from ui.IconFactory import IconFactory
from ui.Canvas import PetriNetView
from ui.ProjectManager import ProjectManager

class PetriNetEditor(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Petri Net Architect")
        self.resize(1500, 900)
        self.setStyleSheet("QMainWindow { background-color: #f0f2f5; }")

        # --- 1. Init Logic Helpers ---
        self.manager = ProjectManager()
        self.current_filename = None

        # --- 2. Central View (Canvas) ---
        self.canvas = PetriNetView(self) # Pass 'self' so canvas can call update_stats()
        self.setCentralWidget(self.canvas)

        # --- 3. UI Setup ---
        self.setup_toolbar()
        self.setup_left_sidebar()
        self.setup_right_sidebar()

        # Initial stats
        self.update_stats()

    # ========================== UI SETUP ==========================
    def setup_toolbar(self):
        tb = QToolBar("Main")
        tb.setIconSize(QSize(32, 32))
        tb.setMovable(False)
        self.addToolBar(Qt.ToolBarArea.TopToolBarArea, tb)

        # File Actions
        self._add_act(tb, "new", "New", self.new_project)
        self._add_act(tb, "save", "Save", self.save_project)
        tb.addSeparator()

        # Tools
        self.act_grp = []
        self.act_grp.append(self._add_act(tb, "circle", "Place", lambda: self.set_mode("circle"), True))
        self.act_grp.append(self._add_act(tb, "square", "Trans", lambda: self.set_mode("square"), True))
        self.act_grp.append(self._add_act(tb, "arrow", "Arc", lambda: self.set_mode("arrow"), True))
        self.act_grp.append(self._add_act(tb, "erase", "Erase", lambda: self.set_mode("erase"), True))
        tb.addSeparator()
        self._add_act(tb, "stop", "Select", lambda: self.set_mode(None))

        # Spacer
        w = QWidget()
        w.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        tb.addWidget(w)

        # Analysis
        self._add_act(tb, "graph", "Build Graph", self.run_analysis)

    def _add_act(self, toolbar, icon, tip, func, checkable=False):
        act = QAction(IconFactory.create_icon(icon), tip, self)
        act.setToolTip(tip)
        act.setCheckable(checkable)
        act.triggered.connect(func)
        toolbar.addAction(act)
        return act

    def setup_left_sidebar(self):
        dock = QDockWidget("Explorer", self)
        dock.setAllowedAreas(Qt.DockWidgetArea.LeftDockWidgetArea)
        tabs = QTabWidget()

        # Tab 1: Projects
        self.proj_list = QListWidget()
        self.refresh_file_list()
        self.proj_list.itemDoubleClicked.connect(self.load_project)
        self.proj_list.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.proj_list.customContextMenuRequested.connect(self.show_file_menu)
        tabs.addTab(self.proj_list, "Projects")

        # Tab 2: Stats
        self.stats_txt = QTextEdit()
        self.stats_txt.setReadOnly(True)
        tabs.addTab(self.stats_txt, "Net Info")

        dock.setWidget(tabs)
        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, dock)

    def setup_right_sidebar(self):
        dock = QDockWidget("Analysis", self)
        dock.setAllowedAreas(Qt.DockWidgetArea.RightDockWidgetArea)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        self.img_lbl = QLabel("No graph yet")
        self.img_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.img_lbl.setStyleSheet("background: white;")
        scroll.setWidget(self.img_lbl)

        dock.setWidget(scroll)
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, dock)

    # ========================== LOGIC INTERFACE ==========================

    def set_mode(self, mode):
        self.canvas.set_mode(mode)
        # Handle UI Button states
        for act in self.act_grp: act.setChecked(False)
        if mode == "circle": self.act_grp[0].setChecked(True)
        elif mode == "square": self.act_grp[1].setChecked(True)
        elif mode == "arrow": self.act_grp[2].setChecked(True)
        elif mode == "erase": self.act_grp[3].setChecked(True)
        self.statusBar().showMessage(f"Mode: {mode if mode else 'Select'}")

    def update_stats(self):
        """Called by Canvas when shapes change"""
        c, s, a = len(self.canvas.circles), len(self.canvas.squares), len(self.canvas.arrows)
        txt = f"<b>Net Statistics</b><br>Places: {c}<br>Transitions: {s}<br>Arcs: {a}<hr>"
        for item in self.canvas.circles:
            txt += f"{item['label']}: {item['item'].tokens} tokens<br>"
        self.stats_txt.setHtml(txt)

    def run_analysis(self):
        self.statusBar().showMessage("Building...")
        QApplication.processEvents()
        try:
            img_path = self.manager.build_graph(self.canvas)
            pix = QPixmap(img_path)
            self.img_lbl.setPixmap(pix)
            self.statusBar().showMessage("Graph Built!")
        except Exception as e:
            self.statusBar().showMessage(f"Error: {e}")

    # ========================== FILE OPS ==========================

    def new_project(self):
        if QMessageBox.question(self, "New", "Discard changes?", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No) == QMessageBox.StandardButton.Yes:
            self.canvas.clear_all()
            self.current_filename = None
            self.update_stats()

    def save_project(self):
        if not self.current_filename:
            name, ok = QInputDialog.getText(self, "Save", "Name:")
            if not ok or not name: return
            self.current_filename = name

        saved_name = self.manager.save_file(self.current_filename, self.canvas)
        self.current_filename = saved_name
        self.refresh_file_list()
        self.statusBar().showMessage(f"Saved {saved_name}")

    def load_project(self, item):
        self.current_filename = item.text()
        self.manager.load_file(self.current_filename, self.canvas, self)
        self.update_stats()
        self.statusBar().showMessage(f"Loaded {self.current_filename}")

    def refresh_file_list(self):
        self.proj_list.clear()
        files = [f for f in os.listdir(self.manager.projects_dir) if f.endswith(".json")]
        self.proj_list.addItems(files)

    def show_file_menu(self, pos):
        item = self.proj_list.itemAt(pos)
        if item:
            menu = QMenu(self)
            act = QAction("Delete", self)
            act.triggered.connect(lambda: [os.remove(os.path.join(self.manager.projects_dir, item.text())), self.refresh_file_list()])
            menu.addAction(act)
            menu.exec(self.proj_list.mapToGlobal(pos))

if __name__ == "__main__":
    app = QApplication(sys.argv)
    editor = PetriNetEditor()
    editor.showMaximized()
    sys.exit(app.exec())