from PyQt6.QtWidgets import (QGraphicsEllipseItem, QGraphicsTextItem, 
                             QGraphicsPathItem, QGraphicsScene, QGraphicsItem, QGraphicsPolygonItem)
from PyQt6.QtGui import QBrush, QPen, QPolygonF, QPainterPath, QFont, QColor
from PyQt6.QtCore import Qt, QLineF, QPointF
from tree.algo import KMGraph
import math

from PyQt6.QtGui import QFont, QPen, QBrush, QColor
from PyQt6.QtCore import Qt

# -------------------------------------------------------------
# Graph items

# ---------------------------------------------
# Node Item

class GraphNode(QGraphicsEllipseItem):
    def __init__(self, node):
        super().__init__()
        self.node = node
        self.edges = [] 

        # Color Logic based on Tag
        if hasattr(self.node, 'tag'):
            if self.node.tag == "dead-end":
                bg_color = QColor(255, 200, 200) 
            elif self.node.tag == "done":
                bg_color = QColor(200, 255, 200)
            elif self.node.tag == "old":
                bg_color = QColor(240, 240, 240)
            elif self.node.tag == "new":
                bg_color = QColor(200, 200, 255)
        else:
            bg_color = QColor(240, 240, 240)

        # node appearance
        self.setBrush(QBrush(bg_color))
        self.setPen(QPen(Qt.GlobalColor.black, 3))

        # node content (marking)
        marking_text = self.format_marking()
        self.label = QGraphicsTextItem(marking_text, self)
        
        # Style the Font
        node_font = QFont("Arial", 12, QFont.Weight.Bold)
        self.label.setFont(node_font)
        
        # allow user to move nodes
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemSendsGeometryChanges)

        self.update_geometry()

    def update_geometry(self):
        # Get the size of the text we just styled
        text_rect = self.label.boundingRect()
        
        # Ovals need more width than height to look good
        padding_x = 40 
        padding_y = 20
        
        w = text_rect.width() + padding_x
        h = text_rect.height() + padding_y
        
        # Set the oval shape
        self.setRect(-w/2, -h/2, w, h)
        
        # Center the text exactly in the middle of the oval
        self.label.setPos(-text_rect.width()/2, -text_rect.height()/2)

    def format_marking(self):
        from tree.markings import OMEGA
        # Using the Unicode for omega: \u03c9
        vals = ["\u03c9" if v == OMEGA else str(v) for v in self.node.marking.values()]
        return "(" + ",".join(vals) + ")"

    def itemChange(self, change, value):
        if change == QGraphicsItem.GraphicsItemChange.ItemPositionChange:
            for edge in self.edges:
                edge.update_position()
        return super().itemChange(change, value)


class GraphEdge(QGraphicsPathItem):
    def __init__(self, src_item, dst_item, transition):
        super().__init__()
        self.src = src_item
        self.dst = dst_item
        self.transition = transition
        
        self.setPen(QPen(Qt.GlobalColor.black, 1.5))
        
        # Label for the transition
        self.label = QGraphicsTextItem(transition, self)
        self.label.setDefaultTextColor(QColor("darkred"))

        edge_font = QFont("Consolas", 12) # Monospace font looks good for transitions
        edge_font.setItalic(True)
        edge_font.setBold(True)
        self.label.setFont(edge_font)

        # Arrowhead item
        self.arrow_head = QGraphicsPolygonItem(self)
        self.arrow_head.setBrush(QBrush(Qt.GlobalColor.black))

    def update_position(self):
        s_pos = self.src.scenePos()
        d_pos = self.dst.scenePos()
        
        # --- SELF-LOOP LOGIC ---
        # --- SELF-LOOP LOGIC (SIDE LOOP WITH IMPROVED ARROW) ---
        if self.src == self.dst:
            rect = self.src.rect()
            w, h = rect.width(), rect.height()
            
            path = QPainterPath()
            
            # 1. Start/End on the RIGHT side of the oval boundary
            start_p = QPointF(w/2, -h/4) 
            end_p = QPointF(w/2, h/4)
            
            # 2. Control points pushed Right (w*1.2) to create a clean handle
            ctrl1 = QPointF(w * 1.2, -h)
            ctrl2 = QPointF(w * 1.2, h)
            
            path.moveTo(start_p)
            path.cubicTo(ctrl1, ctrl2, end_p)
            self.setPath(path)
            
            # 3. Position Label centered to the right of the loop
            l_rect = self.label.boundingRect()
            self.label.setPos(w * 1.1, -l_rect.height() / 2)
            
            # 4. DYNAMIC ARROWHEAD (Calculates entry angle)
            tip = end_p
            # Calculate angle based on the curve's entry direction (from ctrl2 to tip)
            angle = math.atan2(tip.y() - ctrl2.y(), tip.x() - ctrl2.x())
            
            arrow_size = 12
            wing_angle = 0.5 # Radians (sharper point)
            
            # Calculate the two wing points relative to the calculated tangent
            p2 = tip - QPointF(math.cos(angle - wing_angle) * arrow_size, 
                               math.sin(angle - wing_angle) * arrow_size)
            p3 = tip - QPointF(math.cos(angle + wing_angle) * arrow_size, 
                               math.sin(angle + wing_angle) * arrow_size)
            
            self.arrow_head.setPolygon(QPolygonF([tip, p2, p3]))
            
            # Ensure edge follows the node's scene position
            self.setPos(s_pos)
            return

        # --- EXISTING STRAIGHT/BENT LINE LOGIC ---
        self.setPos(0, 0) # Reset position for standard lines
        center_line = QLineF(s_pos, d_pos)
        full_len = center_line.length()
        if full_len < 1: return

        # --- 1. DYNAMIC OVAL BOUNDARY ---
        def get_node_radius_at_angle(node, line):
            r = node.rect()
            w, h = r.width() / 2, r.height() / 2
            # line.angle() is in degrees, math.radians converts it for cos/sin
            angle = math.radians(line.angle())
            denom = math.sqrt((h * math.cos(angle))**2 + (w * math.sin(angle))**2)
            return (w * h) / denom if denom != 0 else w

        dist_src = get_node_radius_at_angle(self.src, center_line)
        dist_dst = get_node_radius_at_angle(self.dst, QLineF(d_pos, s_pos))

        # FIX: Use pointAt(percentage) instead of at(pixels)
        # Percentage = desired_distance / total_length
        start_outline = center_line.pointAt(dist_src / full_len)
        end_outline = QLineF(d_pos, s_pos).pointAt(dist_dst / full_len)

        # --- 2. BENDING LOGIC ---
        is_back_edge = d_pos.y() < s_pos.y()
        path = QPainterPath()
        path.moveTo(start_outline)
        
        if is_back_edge:
            mid = QLineF(start_outline, end_outline).center()
            offset = 60
            dx, dy = d_pos.x() - s_pos.x(), d_pos.y() - s_pos.y()
            ctrl_p = QPointF(mid.x() - dy * offset / full_len, mid.y() + dx * offset / full_len)
            path.quadTo(ctrl_p, end_outline)
            
            # Tangent for arrow
            t = 0.95
            pos_near_end = (1-t)**2 * start_outline + 2*(1-t)*t * ctrl_p + t**2 * end_outline
            tangent_line = QLineF(pos_near_end, end_outline)
        else:
            path.lineTo(end_outline)
            tangent_line = QLineF(start_outline, end_outline)

        self.setPath(path)

        # --- 3. LABEL POSITIONING ---
        mid_p = path.pointAtPercent(0.5)
        
        # path.angleAtPercent(0.5) returns the angle of the curve at midpoint
        # We subtract 90 to push it "outward" perpendicular to the line
        angle_rad = math.radians(path.angleAtPercent(0.5) - 90)
        
        padding = 20 
        # Calculate offset using polar coordinates
        label_x = mid_p.x() + math.cos(angle_rad) * padding
        label_y = mid_p.y() - math.sin(angle_rad) * padding
        
        text_rect = self.label.boundingRect()
        self.label.setPos(label_x - text_rect.width() / 2, 
                         label_y - text_rect.height() / 2)

        # --- 4. ARROWHEAD ---
        tip = end_outline 
        angle = math.atan2(-tangent_line.dy(), tangent_line.dx())
        arrow_size = 12
        p2 = tip + QPointF(math.sin(angle - math.pi/3) * arrow_size, math.cos(angle - math.pi/3) * arrow_size)
        p3 = tip + QPointF(math.sin(angle - math.pi + math.pi/3) * arrow_size, math.cos(angle - math.pi + math.pi/3) * arrow_size)
        self.arrow_head.setPolygon(QPolygonF([tip, p2, p3]))

# --- LAYOUT ALGORITHM ---

def calculate_tree_layout(graph: KMGraph):
    if not graph.nodes:
        return {}

    levels = {graph.nodes[0].id: 0}
    queue = [graph.nodes[0].id]
    while queue:
        u = queue.pop(0)
        for edge in graph.edges:
            if edge.src == u and edge.dst not in levels:
                levels[edge.dst] = levels[u] + 1
                queue.append(edge.dst)

    nodes_by_level = {}
    for node_id, lv in levels.items():
        nodes_by_level.setdefault(lv, []).append(node_id)

    pos = {}
    X_GAP = 200
    Y_GAP = 200
    
    for lv, ids in nodes_by_level.items():
        level_width = (len(ids) - 1) * X_GAP
        start_x = -level_width / 2
        for i, node_id in enumerate(ids):
            pos[node_id] = (start_x + (i * X_GAP), lv * Y_GAP)
            
    return pos

# --- SCENE BUILDER ---

def build_scene_from_graph(graph: KMGraph) -> QGraphicsScene:
    scene = QGraphicsScene()
    node_items = {}

    positions = calculate_tree_layout(graph)

    for node in graph.nodes:
        item = GraphNode(node)
        x, y = positions.get(node.id, (0, 0))
        item.setPos(x, y)
        scene.addItem(item)
        node_items[node.id] = item

    for edge in graph.edges:
        if edge.src in node_items and edge.dst in node_items:
            src_item = node_items[edge.src]
            dst_item = node_items[edge.dst]
            
            edge_item = GraphEdge(src_item, dst_item, edge.transition)
            scene.addItem(edge_item)
            scene.addItem(edge_item.label) 
            
            src_item.edges.append(edge_item)
            dst_item.edges.append(edge_item)
            
            edge_item.update_position()

    return scene


