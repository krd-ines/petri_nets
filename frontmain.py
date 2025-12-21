import sys
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QPushButton,
    QGraphicsScene, QGraphicsView, QInputDialog
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPen
from snakes.nets import PetriNet, Place, Transition, Value, MultiArc
# Import custom classes
from MovableEllipse import MovableEllipse
from MovableRect import MovableRect
from MovableArrow import MovableArrow

# Import snakes + tree modules
from snakes.nets import PetriNet, Place, Transition, Value
from tree.algo import build_coverability_tree
from tree.print import print_graph
from tree.export import save_graph_image

class PetriNetEditor(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Petri Net Drawer")
        self.resize(900, 650)

        layout = QVBoxLayout(self)

        # --- Buttons ---
        self.btn_circle = QPushButton("Circle (Place)")
        self.btn_square = QPushButton("Square (Transition)")
        self.btn_arrow = QPushButton("Arrow (Arc)")
        self.btn_erase = QPushButton("Erase")
        self.btn_stop = QPushButton("Stop Drawing")
        self.btn_print = QPushButton("Print Net Data")
        self.btn_draw_graph = QPushButton("Draw Final Graph")

        layout.addWidget(self.btn_circle)
        layout.addWidget(self.btn_square)
        layout.addWidget(self.btn_arrow)
        layout.addWidget(self.btn_erase)
        layout.addWidget(self.btn_stop)
        layout.addWidget(self.btn_print)
        layout.addWidget(self.btn_draw_graph)

        # --- Scene + View ---
        self.scene = QGraphicsScene()
        self.view = QGraphicsView(self.scene)
        layout.addWidget(self.view)

        # --- State Variables ---
        self.current_shape = None
        self.start_item = None
        self.start_click_pos = None
        self.temp_line = None

        # --- Data Storage ---
        self.circles = []
        self.squares = []
        self.arrows = []

        # Counters for automatic labeling
        self.circle_count = 0
        self.square_count = 0

        # --- Connections ---
        self.btn_circle.clicked.connect(lambda: self.set_shape("circle"))
        self.btn_square.clicked.connect(lambda: self.set_shape("square"))
        self.btn_arrow.clicked.connect(lambda: self.set_shape("arrow"))
        self.btn_erase.clicked.connect(lambda: self.set_shape("erase"))
        self.btn_stop.clicked.connect(lambda: self.set_shape(None))
        self.btn_print.clicked.connect(self.print_net)
        self.btn_draw_graph.clicked.connect(self.draw_final_graph)

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
        if source is not self.view.viewport():
            return super().eventFilter(source, event)

        # =======================================================
        # 1. HANDLE DOUBLE CLICK (Tokens & Arc Weights)
        # =======================================================
        if event.type() == event.Type.MouseButtonDblClick and event.button() == Qt.MouseButton.LeftButton:
            pos = self.view.mapToScene(event.pos())

            # We look for items at the clicked position
            items_at_pos = self.scene.items(pos)

            for item in items_at_pos:
                # -- Case A: Double Click on Place (Circle) --
                if isinstance(item, MovableEllipse):
                    num, ok = QInputDialog.getInt(
                        self, "Set Tokens",
                        f"Tokens for {item.label_text}:",
                        item.tokens, 0, 100, 1
                    )
                    if ok:
                        item.set_tokens(num)
                    return True

                    # -- Case B: Double Click on Arc (Arrow) --
                elif isinstance(item, MovableArrow):
                    num, ok = QInputDialog.getInt(
                        self, "Set Arc Weight",
                        "Enter weight (credential):",
                        item.weight, 1, 100, 1
                    )
                    if ok:
                        item.set_weight(num)
                    return True

                    # =======================================================
        # 2. HANDLE SINGLE CLICK (Drawing Logic)
        # =======================================================
        if event.type() == event.Type.MouseButtonPress:
            if self.current_shape is None:
                return False

            pos = self.view.mapToScene(event.pos())

            # --- Draw Circle ---
            if self.current_shape == "circle" and event.button() == Qt.MouseButton.LeftButton:
                label = f"p{self.circle_count}"
                self.circle_count += 1
                circle_item = MovableEllipse(pos, label, self)
                self.scene.addItem(circle_item)
                self.circles.append({"label": label, "item": circle_item})

            # --- Draw Square ---
            elif self.current_shape == "square" and event.button() == Qt.MouseButton.LeftButton:
                label = f"t{self.square_count}"
                self.square_count += 1
                square_item = MovableRect(pos, label, self)
                self.scene.addItem(square_item)
                self.squares.append({"label": label, "item": square_item})

            # --- Draw Arrow (Right click select, Left click finish) ---
            elif self.current_shape == "arrow":
                if event.button() == Qt.MouseButton.RightButton:
                    # Select Start/End item
                    clicked_items = self.scene.items(pos)
                    valid_items = [i for i in clicked_items if isinstance(i, (MovableEllipse, MovableRect))]

                    if valid_items:
                        item = valid_items[0]

                        if self.start_item is None:
                            # 1. First click (Start)
                            self.start_item = item
                            self.start_click_pos = pos
                        else:
                            # 2. Second click (End)
                            end_item = item
                            start_label = self.find_label(self.start_item)
                            end_label = self.find_label(end_item)

                            # Validation: Don't connect same types (p->p or t->t)
                            if type(self.start_item) == type(end_item):
                                print("Error: Cannot connect two items of the same type.")
                                self.reset_arrow_tool()
                                return True

                            # Create Arrow
                            arrow_item = MovableArrow(self.start_item, end_item, start_label, end_label)
                            self.scene.addItem(arrow_item)
                            self.arrows.append({
                                "start_label": start_label,
                                "end_label": end_label,
                                "item": arrow_item
                            })

                            self.reset_arrow_tool()

                # Visual temp line logic
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
                    elif isinstance(item, MovableArrow):
                        self.erase_arrow(item)

            return True
        return super().eventFilter(source, event)

    # --- Helper Methods ---
    def reset_arrow_tool(self):
        self.start_item = None
        self.start_click_pos = None
        if self.temp_line:
            self.scene.removeItem(self.temp_line)
            self.temp_line = None

    def update_arrows(self, moved_label):
        for a in self.arrows:
            if a["start_label"] == moved_label or a["end_label"] == moved_label:
                a["item"].update_geometry()

    def find_label(self, item):
        if isinstance(item, MovableEllipse): return item.label_text
        if isinstance(item, MovableRect): return item.label_text
        return None

    def erase_arrow(self, arrow_item):
        """Removes an arrow from scene and list."""
        arrow_item.delete(self.scene)
        self.arrows = [a for a in self.arrows if a["item"] != arrow_item]

    def erase_shape_by_label(self, label):
        removed = False
        for i, c in enumerate(self.circles):
            if c["label"] == label:
                c["item"].delete(self.scene)
                del self.circles[i]
                removed = True
                break
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
        print("\n--- Current Net Configuration ---")
        for c in self.circles:
            print(f"Place: {c['label']} | Tokens: {c['item'].tokens}")
        for s in self.squares:
            print(f"Transition: {s['label']}")
        for a in self.arrows:
            print(f"Arc: {a['start_label']} -> {a['end_label']} | Weight: {a['item'].weight}")
        print("---------------------------------\n")

    # =======================================================
    # 3. DRAW FINAL GRAPH (Corrected Logic)
    # =======================================================
    def draw_final_graph(self):
        """Exports the Petri net graph image using SNAKES."""
        print("Building graph...")
        net = PetriNet("frontend_net")

        # 1. Add Places
        for c in self.circles:
            count = c["item"].tokens
            tokens_list = [Value(1) for _ in range(count)]
            net.add_place(Place(c["label"], tokens=tokens_list))

        # 2. Add Transitions
        for s in self.squares:
            net.add_transition(Transition(s["label"]))

        # 3. Add Arcs
        for a in self.arrows:
            start, end = a["start_label"], a["end_label"]
            weight = a["item"].weight

            # --- FIX: Use MultiArc ---
            if weight == 1:
                arc_val = Value(1)
            else:
                arc_val = MultiArc([Value(1) for _ in range(weight)])
            # -------------------------

            if start.startswith("p") and end.startswith("t"):
                net.add_input(start, end, arc_val)
            elif start.startswith("t") and end.startswith("p"):
                net.add_output(end, start, arc_val)

        # 4. Generate Tree
        try:
            initial_marking = {p.name: len(p.tokens) for p in net.place()}
            print(f"Initial Marking: {initial_marking}")

            tree = build_coverability_tree(net, initial_marking)
            print_graph(tree)
            save_graph_image(tree, "graph")
            print("Graph exported successfully.")

        except Exception as e:
            print(f"Error building graph: {e}")
            import traceback
            traceback.print_exc()

def main():
    app = QApplication(sys.argv)
    editor = PetriNetEditor()
    editor.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()