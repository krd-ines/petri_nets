import sys
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QPushButton,
    QGraphicsScene, QGraphicsView
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPen
#hello
# Import Refactored Classes
from MovableEllipse import MovableEllipse
from MovableRect import MovableRect
from MovableArrow import MovableArrow

class PetriNetEditor(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Petri Net Drawer")
        self.resize(900, 650)

        layout = QVBoxLayout(self)

        # Buttons
        self.btn_circle = QPushButton("Circle")
        self.btn_square = QPushButton("Square")
        self.btn_arrow = QPushButton("Arrow")
        self.btn_erase = QPushButton("Erase")
        self.btn_stop = QPushButton("Stop Drawing")
        self.btn_print = QPushButton("Print Net")

        layout.addWidget(self.btn_circle)
        layout.addWidget(self.btn_square)
        layout.addWidget(self.btn_arrow)
        layout.addWidget(self.btn_erase)
        layout.addWidget(self.btn_stop)
        layout.addWidget(self.btn_print)

        # Scene + view
        self.scene = QGraphicsScene()
        self.view = QGraphicsView(self.scene)
        layout.addWidget(self.view)

        # Current mode
        self.current_shape = None
        self.start_item = None
        self.start_click_pos = None
        self.temp_line = None

        # Data structures
        self.circles = []
        self.squares = []
        self.arrows = []

        # Counters
        self.circle_count = 0
        self.square_count = 0

        # Connect buttons
        self.btn_circle.clicked.connect(lambda: self.set_shape("circle"))
        self.btn_square.clicked.connect(lambda: self.set_shape("square"))
        self.btn_arrow.clicked.connect(lambda: self.set_shape("arrow"))
        self.btn_erase.clicked.connect(lambda: self.set_shape("erase"))
        self.btn_stop.clicked.connect(lambda: self.set_shape(None))
        self.btn_print.clicked.connect(self.print_net)

        self.view.setMouseTracking(True)
        self.view.viewport().installEventFilter(self)

    def set_shape(self, shape):
        self.current_shape = shape
        self.start_item = None
        self.start_click_pos = None
        if self.temp_line:
            self.scene.removeItem(self.temp_line)
            self.temp_line = None

    def eventFilter(self, source, event):
        if event.type() == event.Type.MouseButtonPress and source is self.view.viewport():
            if self.current_shape is None:
                return False

            pos = self.view.mapToScene(event.pos())

            # --- Circle ---
            if self.current_shape == "circle" and event.button() == Qt.MouseButton.LeftButton:
                label = f"p{self.circle_count}"
                self.circle_count += 1
                circle_item = MovableEllipse(pos, label, self)
                self.scene.addItem(circle_item)
                self.circles.append({"label": label, "item": circle_item})

            # --- Square ---
            elif self.current_shape == "square" and event.button() == Qt.MouseButton.LeftButton:
                label = f"t{self.square_count}"
                self.square_count += 1
                square_item = MovableRect(pos, label, self)
                self.scene.addItem(square_item)
                self.squares.append({"label": label, "item": square_item})

            # --- Arrow ---
            elif self.current_shape == "arrow":
                if event.button() == Qt.MouseButton.RightButton:
                    clicked_items = self.scene.items(pos)
                    valid_items = [i for i in clicked_items if isinstance(i, (MovableEllipse, MovableRect))]

                    if valid_items:
                        item = valid_items[0]
                        if self.start_item is None:
                            self.start_item = item
                            self.start_click_pos = pos
                        else:
                            end_item = item
                            start_label = self.find_label(self.start_item)
                            end_label = self.find_label(end_item)

                            # CREATE ARROW
                            arrow_item = MovableArrow(self.start_item, end_item, start_label, end_label)
                            self.scene.addItem(arrow_item)

                            self.arrows.append({
                                "start_label": start_label,
                                "end_label": end_label,
                                "item": arrow_item
                            })

                            # Reset
                            self.start_item = None
                            self.start_click_pos = None
                            if self.temp_line:
                                self.scene.removeItem(self.temp_line)
                                self.temp_line = None

                elif event.button() == Qt.MouseButton.LeftButton and self.start_item:
                    if self.temp_line:
                        self.scene.removeItem(self.temp_line)
                    self.temp_line = self.scene.addLine(
                        self.start_click_pos.x(), self.start_click_pos.y(),
                        pos.x(), pos.y(),
                        QPen(Qt.GlobalColor.black, 1)
                    )

            # --- Erase ---
            elif self.current_shape == "erase" and event.button() == Qt.MouseButton.LeftButton:
                clicked_items = self.scene.items(pos)
                if clicked_items:
                    item = clicked_items[0]
                    if item.parentItem():
                        item = item.parentItem()
                    label = self.find_label(item)
                    if label:
                        self.erase_shape_by_label(label)

            return True
        return super().eventFilter(source, event)

    # --- THE LINKING FUNCTION ---
    def update_arrows(self, moved_label):
        """Called by Shapes when they move"""
        for a in self.arrows:
            if a["start_label"] == moved_label or a["end_label"] == moved_label:
                a["item"].update_geometry()

    def find_label(self, item):
        if isinstance(item, MovableEllipse): return item.label_text
        if isinstance(item, MovableRect): return item.label_text
        return None

    def erase_shape_by_label(self, label):
        removed = False
        # Remove Circle
        for i, c in enumerate(self.circles):
            if c["label"] == label:
                c["item"].delete(self.scene)
                del self.circles[i]
                removed = True
                break
        # Remove Square
        if not removed:
            for i, s in enumerate(self.squares):
                if s["label"] == label:
                    s["item"].delete(self.scene)
                    del self.squares[i]
                    removed = True
                    break

        if not removed: return

        # Remove connected arrows
        new_arrows = []
        for a in self.arrows:
            if a["start_label"] == label or a["end_label"] == label:
                a["item"].delete(self.scene)
            else:
                new_arrows.append(a)
        self.arrows = new_arrows

    def print_net(self):
        print("\n--- Petri Net Data ---")
        print("Circles:", [
            {k: v for k, v in c.items() if k not in ("item", "label_item")}
            for c in self.circles
        ])
        print("Squares:", [
            {k: v for k, v in s.items() if k not in ("item", "label_item")}
            for s in self.squares
        ])
        print("Arrows:", [
            {k: v for k, v in a.items() if k not in ("line_item", "head_item", "start_item", "end_item")}
            for a in self.arrows
        ])
        print("----------------------\n")

def main():
    app = QApplication(sys.argv)
    editor = PetriNetEditor()
    editor.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()