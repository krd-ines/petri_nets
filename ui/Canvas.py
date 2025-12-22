from PyQt6.QtWidgets import QGraphicsScene, QGraphicsView, QFrame, QInputDialog
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPainter

from ui.shapes.MovableEllipse import MovableEllipse
from ui.shapes.MovableArrow import MovableArrow
from ui.shapes.MovableRect import MovableRect


class PetriNetView(QGraphicsView):
    def __init__(self, parent_editor):
        super().__init__()
        self.editor = parent_editor  # Reference to Main Window (for updating stats)
        self.scene = QGraphicsScene()
        self.setScene(self.scene)

        # visual settings
        self.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.setFrameShape(QFrame.Shape.NoFrame)
        self.setMouseTracking(True)

        # --- Data Storage ---
        self.circles = []
        self.squares = []
        self.arrows = []
        self.circle_count = 0
        self.square_count = 0

        # --- State ---
        self.current_mode = None  # "circle", "square", "arrow", "erase", or None
        self.start_item = None    # Used when drawing arrows

    def set_mode(self, mode):
        self.current_mode = mode
        self.start_item = None # Reset arrow drawing if mode changes

    def clear_all(self):
        self.scene.clear()
        self.circles = []
        self.squares = []
        self.arrows = []
        self.circle_count = 0
        self.square_count = 0

    def mousePressEvent(self, event):
        pos = self.mapToScene(event.pos())

        # 1. Handle Drawing Logic
        if self.current_mode == "circle" and event.button() == Qt.MouseButton.LeftButton:
            self._add_place(pos)
        elif self.current_mode == "square" and event.button() == Qt.MouseButton.LeftButton:
            self._add_transition(pos)
        elif self.current_mode == "arrow":
            self._handle_arrow_creation(pos, event.button())
        elif self.current_mode == "erase" and event.button() == Qt.MouseButton.LeftButton:
            self._handle_erasing(pos)

        # 2. Update the Editor's Stats Panel
        if self.editor:
            self.editor.update_stats()

        super().mousePressEvent(event)

    def mouseDoubleClickEvent(self, event):
        pos = self.mapToScene(event.pos())
        item = self.scene.itemAt(pos, self.transform())

        # FIX: If we clicked the text label inside the shape, switch to the parent shape
        if item and item.parentItem():
            item = item.parentItem()

        # 1. Handle Place (Tokens)
        if isinstance(item, MovableEllipse):
            val, ok = QInputDialog.getInt(self, "Edit", "Tokens:", item.tokens, 0, 100)
            if ok:
                item.set_tokens(val)
                self.editor.update_stats()

            event.accept() # STOP the event here (prevents double popup)
            return

            # 2. Handle Arrow (Weight)
        elif isinstance(item, MovableArrow):
            val, ok = QInputDialog.getInt(self, "Edit", "Weight:", item.weight, 1, 100)
            if ok:
                item.set_weight(val)

            event.accept() # STOP the event here
            return

        # If we didn't handle it, let the default behavior happen
        super().mouseDoubleClickEvent(event)

    # --- Internal Helpers ---
    def _add_place(self, pos):
        lbl = f"p{self.circle_count}"
        self.circle_count += 1
        item = MovableEllipse(pos, lbl, self.editor)
        self.scene.addItem(item)
        self.circles.append({"label": lbl, "item": item})

    def _add_transition(self, pos):
        lbl = f"t{self.square_count}"
        self.square_count += 1
        item = MovableRect(pos, lbl, self.editor)
        self.scene.addItem(item)
        self.squares.append({"label": lbl, "item": item})

    def _handle_arrow_creation(self, pos, button):
        # We need to find if there is a valid item under the mouse
        item = self.scene.itemAt(pos, self.transform())

        # If clicked text label, get parent
        if item and item.parentItem():
            item = item.parentItem()

        if not isinstance(item, (MovableEllipse, MovableRect)): return

        if button == Qt.MouseButton.LeftButton:
            # Step 1: Click start node
            self.start_item = item
            self.editor.statusBar().showMessage(f"Selected {item.label_text}. Right Click destination.")

        elif button == Qt.MouseButton.RightButton and self.start_item:
            # Step 2: Right click end node
            if type(self.start_item) == type(item):
                self.editor.statusBar().showMessage("Cannot connect same types (Place-Place or Trans-Trans)!", 2000)
                return

            s_lbl = self.start_item.label_text
            e_lbl = item.label_text
            arrow = MovableArrow(self.start_item, item, s_lbl, e_lbl)
            self.scene.addItem(arrow)
            self.arrows.append({"start_label": s_lbl, "end_label": e_lbl, "item": arrow})

            self.start_item = None # Reset
            self.editor.statusBar().showMessage("Arc created.")

    def _handle_erasing(self, pos):
        item = self.scene.itemAt(pos, self.transform())
        if not item: return

        # If clicked text label, get parent
        if item.parentItem():
            item = item.parentItem()

        # Helper to remove from list by comparing item references
        def remove_from_list(lst, item_ref):
            for entry in lst:
                if entry["item"] == item_ref:
                    lst.remove(entry)
                    return entry["label"]
            return None

        if isinstance(item, MovableArrow):
            item.delete(self.scene)
            remove_from_list(self.arrows, item)

        elif isinstance(item, (MovableEllipse, MovableRect)):
            lbl = item.label_text

            # Remove the item from specific list
            if isinstance(item, MovableEllipse):
                remove_from_list(self.circles, item)
            else:
                remove_from_list(self.squares, item)

            item.delete(self.scene)

            # Also remove any arrows connected to this node
            to_remove = [a for a in self.arrows if a["start_label"] == lbl or a["end_label"] == lbl]
            for a in to_remove:
                a["item"].delete(self.scene)
                self.arrows.remove(a)

    def update_arrows(self, label):
        """Called by shapes (MovableEllipse/Rect) when they move"""
        for a in self.arrows:
            if a["start_label"] == label or a["end_label"] == label:
                a["item"].update_geometry()