import json
import os
from PyQt6.QtCore import QPointF

# Shapes


# Logic
from snakes.nets import PetriNet, Place, Transition, Value, MultiArc

from ui.shapes.MovableEllipse import MovableEllipse
from ui.shapes.MovableArrow import MovableArrow
from ui.shapes.MovableRect import MovableRect

from tree.algo import build_coverability_tree
from tree.export import save_graph_image

class ProjectManager:
    def __init__(self, projects_dir="saved_projects"):
        self.projects_dir = projects_dir
        if not os.path.exists(self.projects_dir):
            os.makedirs(self.projects_dir)

    def save_file(self, filename, canvas):
        """Extracts data from canvas and saves to JSON"""
        if not filename.endswith(".json"): filename += ".json"

        data = {
            "places": [{"label": c['label'], "x": c['item'].scenePos().x(), "y": c['item'].scenePos().y(), "tokens": c['item'].tokens} for c in canvas.circles],
            "transitions": [{"label": s['label'], "x": s['item'].scenePos().x(), "y": s['item'].scenePos().y()} for s in canvas.squares],
            "arcs": [{"start": a['start_label'], "end": a['end_label'], "weight": a['item'].weight} for a in canvas.arrows]
        }

        path = os.path.join(self.projects_dir, filename)
        with open(path, 'w') as f:
            json.dump(data, f, indent=4)
        return filename

    def load_file(self, filename, canvas, editor):
        """Reads JSON and repopulates the canvas"""
        path = os.path.join(self.projects_dir, filename)
        if not os.path.exists(path): return False

        canvas.clear_all()

        with open(path, 'r') as f:
            data = json.load(f)

        label_map = {}

        # Load Places
        for p in data["places"]:
            pos = QPointF(p["x"], p["y"])
            item = MovableEllipse(pos, p["label"], editor)
            item.set_tokens(p["tokens"])
            canvas.scene.addItem(item)
            canvas.circles.append({"label": p["label"], "item": item})
            label_map[p["label"]] = item
            # Update counter to avoid duplicates
            idx = int(p["label"][1:])
            if idx >= canvas.circle_count: canvas.circle_count = idx + 1

        # Load Transitions
        for t in data["transitions"]:
            pos = QPointF(t["x"], t["y"])
            item = MovableRect(pos, t["label"], editor)
            canvas.scene.addItem(item)
            canvas.squares.append({"label": t["label"], "item": item})
            label_map[t["label"]] = item
            idx = int(t["label"][1:])
            if idx >= canvas.square_count: canvas.square_count = idx + 1

        # Load Arcs
        for arc in data["arcs"]:
            s_item = label_map.get(arc["start"])
            e_item = label_map.get(arc["end"])
            if s_item and e_item:
                arrow = MovableArrow(s_item, e_item, arc["start"], arc["end"])
                arrow.set_weight(arc["weight"])
                canvas.scene.addItem(arrow)
                canvas.arrows.append({"start_label": arc["start"], "end_label": arc["end"], "item": arrow})

        return True

    def build_graph(self, canvas):
        """Generates the Coverability Tree image"""
        net = PetriNet("net")
        for c in canvas.circles:
            net.add_place(Place(c["label"], [Value(1) for _ in range(c["item"].tokens)]))
        for s in canvas.squares:
            net.add_transition(Transition(s["label"]))
        for a in canvas.arrows:
            w = a["item"].weight
            val = Value(1) if w == 1 else MultiArc([Value(1)]*w)
            if a["start_label"].startswith("p"): net.add_input(a["start_label"], a["end_label"], val)
            else: net.add_output(a["end_label"], a["start_label"], val)

        tree = build_coverability_tree(net, {p.name: len(p.tokens) for p in net.place()})
        output_name = "graph"
        save_graph_image(tree, output_name)
        return output_name + ".png"