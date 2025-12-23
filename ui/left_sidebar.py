import os
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QTabWidget, QListWidget, QListWidgetItem, 
                             QScrollArea, QFrame, QGroupBox)
from PyQt6.QtCore import Qt, QSize
from ui.IconFactory import IconFactory

# 1. STYLE CONSTANTS (Modular CSS)
TAB_STYLE = """
    QTabBar::tab {
        background: #e9ecef; border: 1px solid #dee2e6;
        padding: 8px 12px; font-size: 13px; font-weight: bold; color: #495057;
        border-top-left-radius: 4px; border-top-right-radius: 4px;
    }
    QTabBar::tab:selected { background: white; border-bottom-color: white; color: #3498db; }
"""

LIST_STYLE = """
    QListWidget { border: none; background-color: white; outline: none; padding: 4px; }
    QListWidget::item { padding: 4px; border-radius: 6px; font-size: 20px; color: #2c3e50; border-bottom: 1px solid #f1f3f5; }
    QListWidget::item:hover { background-color: #f8f9fa; }
    QListWidget::item:selected { background-color: #e3f2fd; color: #1976d2; font-weight: bold; border-left: 4px solid #1976d2; }
"""

class ExplorerPanel(QWidget):
    def __init__(self, manager, parent=None):
        super().__init__(parent)
        self.manager = manager
        self.stat_widgets = {}
        self.init_ui()

    def init_ui(self):
        """Main entry point for UI assembly."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.tabs = QTabWidget()
        self.tabs.setIconSize(QSize(20, 20))
        self.tabs.setStyleSheet(TAB_STYLE)
        
        # Assemble Tabs via sub-methods
        self._setup_projects_tab()
        self._setup_stats_tab()

        layout.addWidget(self.tabs)

    # --- UI COMPONENTS (Modularity) ---

    def _setup_projects_tab(self):
        """Creates the Project List component."""
        self.proj_list = QListWidget()
        self.proj_list.setSpacing(2) 
        self.proj_list.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.proj_list.setStyleSheet(LIST_STYLE)
        self.tabs.addTab(self.proj_list, IconFactory.create_icon("projects"), "Projects")

    def _setup_stats_tab(self):
        """Creates the Net Info (Stats) component."""
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        
        content = QWidget()
        self.stats_layout = QVBoxLayout(content)
        self.stats_layout.setSpacing(10)
        self.stats_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        
        # Add sub-widgets
        self._add_stat_badge("Places")
        self._add_stat_badge("Transitions")
        self._add_stat_badge("Arcs")
        self._add_matrix_box("Pre-Matrix")
        self._add_matrix_box("Post-Matrix")

        scroll.setWidget(content)
        self.tabs.addTab(scroll, IconFactory.create_icon("net_info"), "Net Info")

    def _add_stat_badge(self, name):
        """Factory for a single stat row."""
        f = QFrame()
        f.setStyleSheet("background: #ffffff; border: 1px solid #e9ecef; border-radius: 6px; padding: 6px;")
        l = QHBoxLayout(f)
        
        title = QLabel(f"<b>{name}:</b>")
        title.setStyleSheet("font-size: 14px; color: #2c3e50; border: none;")
        
        val = QLabel("-")
        val.setStyleSheet("font-size: 14px; font-weight: bold; color: #3498db; border: none;")
        
        l.addWidget(title)
        l.addStretch()
        l.addWidget(val)
        
        self.stats_layout.addWidget(f)
        self.stat_widgets[name] = val

    def _add_matrix_box(self, name):
        """Factory for a matrix display box."""
        group = QGroupBox(name)
        group.setStyleSheet("QGroupBox { font-weight: bold; font-size: 14px; color: #34495e; padding-top: 20px; border: 1px solid #dee2e6; margin-top: 10px; }")
        
        layout = QVBoxLayout(group)
        display = QLabel("No Data")
        display.setStyleSheet("font-family: 'Courier New'; font-size: 13px; background: #f8f9fa; padding: 10px; border-radius: 4px;")
        display.setWordWrap(True)
        
        layout.addWidget(display)
        self.stats_layout.addWidget(group)
        self.stat_widgets[name] = display

    # --- LOGIC (Modularity) ---

    def refresh_file_list(self):
        """Encapsulated logic for file scanning."""
        self.proj_list.clear()
        if not os.path.exists(self.manager.projects_dir):
            return

        for file_name in self._get_project_files():
            display_name = file_name.replace(".json", "")
            item = QListWidgetItem(f"📄   {display_name}")
            item.setData(Qt.ItemDataRole.UserRole, file_name)
            self.proj_list.addItem(item)

    def _get_project_files(self):
        """Helper to return sorted list of JSON files."""
        return sorted([f for f in os.listdir(self.manager.projects_dir) if f.endswith(".json")])
    

    def update_content(self, net, pre_dict, post_dict, arc_count):
        """Updates all labels and matrices in the Net Info tab."""
        # 1. Update basic counts
        self.stat_widgets["Places"].setText(str(len(net.place())))
        self.stat_widgets["Transitions"].setText(str(len(net.transition())))
        self.stat_widgets["Arcs"].setText(str(arc_count))

        # 2. Generate list of names for matrix alignment
        places = [p.name for p in net.place()]
        transitions = [t.name for t in net.transition()]

        # 3. Format and set matrix text
        self.stat_widgets["Pre-Matrix"].setText(self._format_matrix(pre_dict, places, transitions))
        self.stat_widgets["Post-Matrix"].setText(self._format_matrix(post_dict, places, transitions))

    def _format_matrix(self, data_dict, places, transitions):
        if not transitions or not places:
            return "No Data"

        col_w, row_w = 5, 6
        # Header: Transitions
        header = " " * row_w + "".join([f"{t:>{col_w}}" for t in transitions])
        separator = "-" * (row_w + col_w * len(transitions) + 2)
        
        rows = []
        for p in places:
            row_str = f"{p:<{row_w}}"
            # Note: data_dict is structured as [transition][place]
            vals = "".join([f"{data_dict.get(t, {}).get(p, 0):>{col_w}}" for t in transitions])
            rows.append(f"{row_str}[{vals} ]")
            
        return f"{header}\n{separator}\n" + "\n".join(rows)