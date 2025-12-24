from PyQt6.QtWidgets import QGraphicsScene, QGraphicsView, QFrame, QInputDialog
from PyQt6.QtCore import Qt, QPointF
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

        # --- ADD THESE TWO LINES FOR SELECTION ---
        # Allows you to click and drag a box to select multiple items
        self.setDragMode(QGraphicsView.DragMode.RubberBandDrag)
        # Keeps the scene rectangle growing as you move items
        self.scene.setSceneRect(-2000, -2000, 4000, 4000)

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
        # --- NEW LOGIC ---
        # If we are in "Select Mode" (None), let the default QGraphicsView 
        # rubber-band selection handle the event.
        if self.current_mode is None:
            super().mousePressEvent(event)
            return
        
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
        # Inside PetriNetView.mouseDoubleClickEvent
        elif isinstance(item, MovableArrow):
            val, ok = QInputDialog.getInt(self, "Edit", "Weight:", item.weight, 1, 100)
            if ok:
                item.set_weight(val)
                # --- ADD THIS LINE ---
                if self.editor:
                    self.editor.update_stats() 
            event.accept()
            return

        # If we didn't handle it, let the default behavior happen
        super().mouseDoubleClickEvent(event)

    def is_connection_duplicate(self, start_label, end_label):
        for arrow_dict in self.arrows:
            # Check if the labels match the keys in your dictionary
            if arrow_dict["start_label"] == start_label and arrow_dict["end_label"] == end_label:
                return True
        return False

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
        item = self.scene.itemAt(pos, self.transform())
        if item and item.parentItem(): item = item.parentItem()
        if not isinstance(item, (MovableEllipse, MovableRect)): return

        if button == Qt.MouseButton.LeftButton:
            self.start_item = item
            self.editor.statusBar().showMessage(f"Selected {item.label_text}. Right Click destination.")

        elif button == Qt.MouseButton.RightButton and self.start_item:
            if type(self.start_item) == type(item): return

            s_lbl = self.start_item.label_text
            e_lbl = item.label_text

            if self.is_connection_duplicate(s_lbl, e_lbl):
                if self.editor:
                    self.editor.show_error(
                        "Duplicate Arc", 
                        f"A connection already exists from {s_lbl} to {e_lbl}."
                    )
                self.start_item = None # Reset selection
                return
            
            bend = 0
            # Check for reverse arrow
            for a_entry in self.arrows:
                if a_entry["start_label"] == e_lbl and a_entry["end_label"] == s_lbl:
                    # Partner found! 
                    # Set BOTH to use the bend logic (Magnitude 30)
                    a_entry["item"].bend_factor = 35
                    
                    bend = 35
                    a_entry["item"].update_geometry()
                    break
            
            arrow = MovableArrow(self.start_item, item, s_lbl, e_lbl)
            arrow.bend_factor = bend
            self.scene.addItem(arrow)
            self.arrows.append({"start_label": s_lbl, "end_label": e_lbl, "item": arrow})

            self.start_item = None
            self.editor.statusBar().showMessage("Arc created.")

    def _handle_erasing(self, pos):
        # Helper to remove from list by comparing item references
        def remove_from_list(lst, item_ref):
            for entry in lst:
                if entry["item"] == item_ref:
                    lst.remove(entry)
                    return entry.get("label", None)
            return None

        item = self.scene.itemAt(pos, self.transform())
        
        if isinstance(item, MovableArrow):
            # Check for partner before deleting
            for a_entry in self.arrows:
                if (a_entry["start_label"] == item.end_label and 
                    a_entry["end_label"] == item.start_label):
                    a_entry["item"].bend_factor = 0
                    a_entry["item"].update_geometry()
            
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
        """Re-calculates geometry for all arcs connected to the moving node."""
        for a_entry in self.arrows:
            if a_entry["start_label"] == label or a_entry["end_label"] == label:
                # This triggers the update_geometry() we fixed earlier
                a_entry["item"].update_geometry()

    def center_on_items(self):
        """Finds all items in the scene and centers the view on them."""
        # Get the bounding rectangle of all items currently in the scene
        rect = self.scene.itemsBoundingRect()
        
        if not rect.isNull():
            # Add some padding so the nodes aren't touching the edge of the view
            padding = 50
            rect.adjust(-padding, -padding, padding, padding)
            
            # This tells the view to look at this specific rectangle
            self.setSceneRect(rect) # Adjust scene size to fit content
            self.centerOn(rect.center())

    def get_snakes_net(self):
        """Converts the visual canvas items into a formal Snakes PetriNet object."""
        from snakes.nets import PetriNet, Place, Transition, Value
        
        net = PetriNet("CanvasNet")
        m0 = {}
        
        # 1. Places
        for c in self.circles:
            name = str(c.get('label', f"p{id(c)}"))
            tokens = c['item'].tokens
            net.add_place(Place(name, tokens))
            m0[name] = tokens

        # 2. Transitions
        for s in self.squares:
            name = str(s.get('label', f"t{id(s)}"))
            net.add_transition(Transition(name))

        # 3. Arcs
        for a in self.arrows:
            src, tgt = a.get('start_label'), a.get('end_label')
            weight_val = a['item'].weight 
            if src and tgt:
                if src in m0: # Place -> Transition
                    net.add_input(src, tgt, Value(weight_val))
                else:         # Transition -> Place
                    net.add_output(tgt, src, Value(weight_val))
                    
        return net, m0
    
    def get_serialization_data(self):
        """Converts current canvas state into a serializable dictionary."""
        return {
            "places": [
                {
                    "label": c['label'], 
                    "x": c['item'].scenePos().x(), 
                    "y": c['item'].scenePos().y(), 
                    "tokens": c['item'].tokens
                } for c in self.circles
            ],
            "transitions": [
                {
                    "label": s['label'], 
                    "x": s['item'].scenePos().x(), 
                    "y": s['item'].scenePos().y()
                } for s in self.squares
            ],
            "arcs": [
                {
                    "start": a['start_label'], 
                    "end": a['end_label'], 
                    "weight": a['item'].weight, 
                    "bend_factor": a['item'].bend_factor
                } for a in self.arrows
            ]
        }
    
    def load_from_data(self, data, editor):
        """Rebuilds the visual canvas from raw dictionary data."""
        self.clear_all()
        label_map = {}

        # 1. Load Places
        for p in data.get("places", []):
            pos = QPointF(p["x"], p["y"])
            item = MovableEllipse(pos, p["label"], editor)
            item.set_tokens(p["tokens"])
            self.scene.addItem(item)
            self.circles.append({"label": p["label"], "item": item})
            label_map[p["label"]] = item
            
            # Keep internal counters in sync
            try:
                idx = int(p["label"][1:])
                if idx >= self.circle_count: self.circle_count = idx + 1
            except ValueError: pass

        # 2. Load Transitions
        for t in data.get("transitions", []):
            pos = QPointF(t["x"], t["y"])
            item = MovableRect(pos, t["label"], editor)
            self.scene.addItem(item)
            self.squares.append({"label": t["label"], "item": item})
            label_map[t["label"]] = item
            
            try:
                idx = int(t["label"][1:])
                if idx >= self.square_count: self.square_count = idx + 1
            except ValueError: pass

        # 3. Load Arcs
        for arc in data.get("arcs", []):
            s_item = label_map.get(arc["start"])
            e_item = label_map.get(arc["end"])
            
            if s_item and e_item:
                arrow = MovableArrow(s_item, e_item, arc["start"], arc["end"])
                arrow.set_weight(arc["weight"])
                # Restore the curve/bend
                arrow.bend_factor = arc.get("bend_factor", 0)
                arrow.update_geometry()
                
                self.scene.addItem(arrow)
                self.arrows.append({
                    "start_label": arc["start"], 
                    "end_label": arc["end"], 
                    "item": arrow
                })