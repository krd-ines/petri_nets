from PyQt6.QtWidgets import QToolBar, QWidget, QSizePolicy
from PyQt6.QtGui import QAction
from PyQt6.QtCore import Qt, QSize
from ui.IconFactory import IconFactory

class MainToolbar(QToolBar):
    def __init__(self, parent=None):
        super().__init__("Main", parent)
        self.setIconSize(QSize(32, 32))
        self.setMovable(False)
        self.act_grp = [] # To keep track of checkable buttons (tools)
        self.init_actions()

    def init_actions(self):
        # 1. File operations
        self.new_act = self._add_act("new", "New Project")
        self.new_act.setToolTip("Create a new Petri net")

        self.save_act = self._add_act("save", "Save Project")
        self.save_act.setToolTip("Save the current Petri net")

        self.addSeparator()

        # 2. Drawing tools (Checkable)
        self.place_act = self._add_act("circle", "Place", True)
        self.place_act.setToolTip("Add Place - Click on canvas to create a place")

        self.trans_act = self._add_act("square", "Transition", True)
        self.trans_act.setToolTip("Add Transition - Click on canvas to create a transition")

        self.arc_act = self._add_act("arrow", "Arc", True)
        self.arc_act.setToolTip("Add Arc - Left click source, right click destination")

        self.erase_act = self._add_act("erase", "Erase", True)
        self.erase_act.setToolTip("Erase - Click on any element to delete it")

        # Add these to a group for easy toggling
        self.act_grp = [self.place_act, self.trans_act, self.arc_act, self.erase_act]

        self.addSeparator()

        # 3. Stop tool
        self.select_act = self._add_act("stop", "Stop Drawing")
        self.select_act.setToolTip("Click to stop drawing mode.")

        # 4. Spacer (Push Help to the right) - Optional, looks nice
        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        self.addWidget(spacer)

        # 5. Help Action
        self.help_act = self._add_act("help", "User Guide") # Make sure you have a 'help.png' in icons
        self.help_act.setToolTip("Open the User Guide and Legend")

    def _add_act(self, icon, tip, checkable=False):
        act = QAction(IconFactory.create_icon(icon), tip, self)
        act.setCheckable(checkable)
        self.addAction(act)
        return act

    def update_mode_checks(self, current_mode):
        """Updates which button looks 'pressed' based on the current mode."""
        modes = ["circle", "square", "arrow", "erase"]
        for i, act in enumerate(self.act_grp):
            act.setChecked(current_mode == modes[i])