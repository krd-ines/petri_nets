import sys
import os
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget,
                             QVBoxLayout, QHBoxLayout, QLabel,
                             QToolBar, QDockWidget, QInputDialog,
                             QMessageBox, QListWidget, QTabWidget, QTextEdit, QPushButton,
                             QMenu, QFrame, QGroupBox, QScrollArea)
from PyQt6.QtGui import QPainter, QPalette, QColor, QAction
from PyQt6.QtCore import Qt, QSize

# --- YOUR PROJECT IMPORTS ---
from snakes.nets import PetriNet, Place, Transition, Value
from tree.algo import build_tree_with_history
from ui.graph import build_scene_from_graph
from ui.right_sidebar import AnalysisPanel
from ui.toolbar import MainToolbar

# --- HER PROJECT IMPORTS ---
from ui.IconFactory import IconFactory
from ui.Canvas import PetriNetView
from ui.ProjectManager import ProjectManager
from ui.left_sidebar import ExplorerPanel
from tree.matrices import extract_pre_post
from ui.theme import StyleManager
from ui.help_dialog import HelpDialog

class PetriNetApp(QMainWindow):
    def __init__(self):
        super().__init__()
        print("[INIT] Starting Petri Net Architect...")
        self.ajuster_taille_ecran()
        self.setWindowTitle("Petri Net Architect")
        self.setWindowIcon(IconFactory.create_icon("tree_graph"))
        self.manager = ProjectManager()
        self.current_filename = None
        self.init_ui()

    def ajuster_taille_ecran(self):
        ecran = QApplication.primaryScreen()
        geo = ecran.availableGeometry() # Exclut déjà la barre des tâches Windows
        
        # On prend 90% de l'écran
        largeur = int(geo.width() * 0.9)
        # On retire 30 pixels supplémentaires pour la StatusBar
        hauteur = int(geo.height() * 0.9) - 30 
        
        self.resize(largeur, hauteur)
        
        # On centre par rapport à la zone disponible (geo.y() évite le décalage)
        x = geo.x() + (geo.width() - largeur) // 2
        y = geo.y() + (geo.height() - hauteur) // 2
        self.move(x, y)


    def init_ui(self):
        self.setStyleSheet(StyleManager.get_dock_style())

        # 1. Central Widget is ONLY the Canvas now
        # This allows the Canvas to expand into all available space
        self.canvas = PetriNetView(self)
        self.setCentralWidget(self.canvas)

        # 2. Left Sidebar (Explorer)
        self.explorer_dock = QDockWidget("Explore", self)
        self.explorer_sidebar = ExplorerPanel(self.manager)
        self.explorer_dock.setWidget(self.explorer_sidebar)
        self._custom_title(self.explorer_dock, "explore", "Explore")
        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, self.explorer_dock)


        # 3. Right Sidebar (Analysis)
        self.analysis_dock = QDockWidget("Coverability Tree", self)

        # NOTE: We do NOT need a QScrollArea here anymore because
        # AnalysisPanel now has its own internal ScrollArea for the buttons.
        self.analysis_sidebar = AnalysisPanel()

        self.analysis_dock.setWidget(self.analysis_sidebar)
        self._custom_title(self.analysis_dock, "tree_graph", "Coverability Tree")
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.analysis_dock)


        # 4. Setup Toolbar
        self.toolbar = MainToolbar(self)
        self.addToolBar(Qt.ToolBarArea.TopToolBarArea, self.toolbar)
        self.setup_connections()
        self.explorer_sidebar.refresh_file_list()

        status_bar = self.statusBar()
        status_bar.setFixedHeight(25) # Taille standard propre
        status_bar.setSizeGripEnabled(False)
        

    def setup_connections(self):
        # Connecting Explorer to Main Logic
        self.explorer_sidebar.proj_list.itemDoubleClicked.connect(self.load_project)
        self.explorer_sidebar.proj_list.customContextMenuRequested.connect(self.show_context_menu)

        # Connecting Analysis to Main Logic
        self.analysis_sidebar.btn_full.clicked.connect(self.run_full_analysis)
        self.analysis_sidebar.btn_step_init.clicked.connect(self.run_step_init)

        # File Actions
        self.toolbar.new_act.triggered.connect(self.new_project)
        self.toolbar.save_act.triggered.connect(self.save_project)

        # Mode Actions
        self.toolbar.place_act.triggered.connect(lambda: self.set_mode("circle"))
        self.toolbar.trans_act.triggered.connect(lambda: self.set_mode("square"))
        self.toolbar.arc_act.triggered.connect(lambda: self.set_mode("arrow"))
        self.toolbar.erase_act.triggered.connect(lambda: self.set_mode("erase"))
        self.toolbar.select_act.triggered.connect(lambda: self.set_mode(None))
        self.toolbar.help_act.triggered.connect(self.show_help_dialog)


    def _custom_title(self, dock, icon, text):
        title = QWidget()
        lay = QHBoxLayout(title)
        lay.setContentsMargins(8,4,8,4)
        lbl_icon = QLabel(); lbl_icon.setPixmap(IconFactory.create_icon(icon).pixmap(25,25))
        lbl_text = QLabel(text); lbl_text.setStyleSheet("font-weight: bold; font-size: 14px;")
        lay.addWidget(lbl_icon); lay.addWidget(lbl_text); lay.addStretch()
        dock.setTitleBarWidget(title)


    def show_context_menu(self, pos):
        item = self.explorer_sidebar.proj_list.itemAt(pos)
        if item:
            menu = QMenu()
            delete_action = menu.addAction("Delete Project")
            delete_action.triggered.connect(self.delete_selected_project)
            menu.exec(self.explorer_sidebar.proj_list.mapToGlobal(pos))


    def run_full_analysis(self):
        print("[ACTION] Running Full Analysis...")
        """Coordination: Get data from Canvas -> Pass to Analysis Panel."""
        net, m0 = self.canvas.get_snakes_net() # Clean export

        if hasattr(self.analysis_sidebar, 'view') and self.analysis_sidebar.view.scene():
            self.analysis_sidebar.view.scene().clear()

        self.analysis_sidebar.set_net_data(net, m0)
        self.analysis_sidebar.run_full()

    def run_step_init(self):
        print("[ACTION] Initializing Stepper...")
        if hasattr(self.analysis_sidebar, 'view'):
            if self.analysis_sidebar.view.scene():
                self.analysis_sidebar.view.scene().clear()

        net, m0 = self.canvas.get_snakes_net()
        self.analysis_sidebar.set_net_data(net, m0)
        self.analysis_sidebar.run_step_init()

        # ========================== HER LOGIC ==========================

    def set_mode(self, mode):
        self.canvas.set_mode(mode)
        # Tell the toolbar to update its UI state
        self.toolbar.update_mode_checks(mode)


    def update_stats(self):
        """The bridge between the Canvas, the Logic, and the Sidebar."""
        # 1. Scrape the canvas to get a formal Snakes PetriNet
        net, m0 = self.canvas.get_snakes_net()

        # 2. Use the external utility for math
        pre, post = extract_pre_post(net)

        # 3. Get arc count directly from canvas for the badge
        arc_count = len(self.canvas.arrows)

        # 4. Hand everything to the sidebar to handle display
        self.explorer_sidebar.update_content(net, pre, post, arc_count)
    
           
    # Add this to PetriNetApp in mainpanel.py
    def update_arrows(self, label):
        """
        Required by MovableEllipse and MovableRect to update
        arrow positions when shapes are moved.
        """
        if hasattr(self, 'canvas'):
            self.canvas.update_arrows(label)


    def load_project(self, item):
        """Triggered by double-clicking a file in the sidebar."""
        actual_filename = item.data(Qt.ItemDataRole.UserRole)

        # Manager handles the file read, Canvas handles the drawing
        if self.manager.load_file(actual_filename, self.canvas, self):
            self.canvas.center_on_items()
            self.update_stats()

    def new_project(self):
        confirm = QMessageBox.question(self, "New", "Clear Canvas?",
                                       QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)

        if confirm == QMessageBox.StandardButton.Yes:
            # 1. Clear Data
            self.canvas.clear_all()
            self.manager.reset_session()

            # 2. Clear Analysis UI
            if hasattr(self, 'analysis_sidebar'):
                if self.analysis_sidebar.view.scene():
                    self.analysis_sidebar.view.scene().clear()

            # 3. Update Visuals
            self.update_stats()

    def save_project(self):
        # Use the manager's state
        name = self.manager.current_filename

        if not name:
            name, ok = QInputDialog.getText(self, "Save", "Project Name:")
            if not (ok and name): return

        # Manager handles extraction and writing
        self.manager.save_file(name, self.canvas)
        self.explorer_sidebar.refresh_file_list()


    def delete_selected_project(self):
        item = self.explorer_sidebar.proj_list.currentItem()
        if not item: return

        actual_filename = item.data(Qt.ItemDataRole.UserRole)
        display_name = item.text().replace("📄  ", "").strip()

        confirm = QMessageBox.question(self, "Confirm Delete",
                                       f"Delete '{display_name}'?",
                                       QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)

        if confirm == QMessageBox.StandardButton.Yes:
            # 1. Tell manager to delete from disk
            if self.manager.delete_file(actual_filename):
                # 2. Update Sidebar list
                self.explorer_sidebar.refresh_file_list()

                # 3. If it was the open file, clear the canvas
                if self.manager.current_filename == display_name:
                    self.canvas.clear_all()
                    self.manager.reset_session()
                    self.update_stats()


    def create_label_with_icon(self, icon_name, text, icon_size=20):
        """Helper to create a label with an icon"""
        label = QLabel()
        icon = IconFactory.create_icon(icon_name)
        pixmap = icon.pixmap(QSize(icon_size, icon_size))
        label.setPixmap(pixmap)
        label.setText(f"  {text}")
        label.setStyleSheet("font-weight: bold; font-size: 14px;")
        return label

    def show_help_dialog(self):
        from ui.help_dialog import HelpDialog  # Import locally to avoid circular imports if needed
        dialog = HelpDialog(self)
        dialog.exec()
    
    # Inside your PetriNetApp class
    def show_error(self, title, message):
        """Global error handler for the application."""
        from PyQt6.QtWidgets import QMessageBox
        msg = QMessageBox(self)
        msg.setIcon(QMessageBox.Icon.Critical)
        msg.setWindowTitle(title)
        msg.setText(message)
        msg.exec()


if __name__ == "__main__":
    import sys
    if sys.platform == "win32":
        try:
            from ctypes import windll
            myappid = 'mycompany.petrinet.architect.1.0'  # arbitrary string
            windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
        except:
            pass

    app = QApplication(sys.argv)

    app.setWindowIcon(IconFactory.create_icon("app_icon"))
    StyleManager.apply_light_theme(app)
    window = PetriNetApp()
    window.show()
    sys.exit(app.exec())