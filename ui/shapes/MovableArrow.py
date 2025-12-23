from PyQt6.QtWidgets import (
    QGraphicsPolygonItem, QGraphicsItem, QGraphicsTextItem, 
    QInputDialog, QGraphicsPathItem
)
from PyQt6.QtGui import QPen, QBrush, QPolygonF, QPainterPath
import math
from PyQt6.QtCore import Qt, QPointF

class MovableArrow(QGraphicsPathItem):
    def __init__(self, start_item, end_item, start_label, end_label, parent=None):
        super().__init__(parent)
        self.start_item = start_item
        self.end_item = end_item
        self.start_label = start_label
        self.end_label = end_label

        self.weight = 1
        self.bend_factor = 0  # 0=straight, 35=curved
        
        # NEW: Use absolute direction based on arrow type
        # This creates a consistent reference frame regardless of node positions
        from ui.shapes.MovableEllipse import MovableEllipse
        if isinstance(self.start_item, MovableEllipse):
            self.bend_direction = 1  # Place -> Transition: offset upward in screen space
        else:
            self.bend_direction = -1  # Transition -> Place: offset downward in screen space

        self.setPen(QPen(Qt.GlobalColor.black, 1))
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable, True)
        
        self.head_item = QGraphicsPolygonItem(self)
        self.head_item.setBrush(QBrush(Qt.GlobalColor.black))

        self.weight_label = QGraphicsTextItem("", self)
        self.weight_label.setDefaultTextColor(Qt.GlobalColor.black)
        self.weight_label.setVisible(False)

        self.update_geometry()

    def set_weight(self, value):
        self.weight = value
        if self.weight > 1:
            self.weight_label.setPlainText(str(self.weight))
            self.weight_label.setVisible(True)
        else:
            self.weight_label.setVisible(False)
        
        self.update_geometry()
        
        # Notify the scene/view that the data changed
        if self.scene():
            # This triggers a redraw and allows the view to catch the change
            self.scene().update()

    def update_geometry(self):
        p1 = self.start_item.scenePos()
        p2 = self.end_item.scenePos()

        dx = p2.x() - p1.x()
        dy = p2.y() - p1.y()
        dist = math.sqrt(dx**2 + dy**2)

        if dist < 10: 
            self.setPath(QPainterPath())
            self.head_item.setPolygon(QPolygonF())
            return

        ux, uy = dx/dist, dy/dist
        node_radius = 20

        start_pt = QPointF(p1.x() + ux * node_radius, p1.y() + uy * node_radius)
        end_pt = QPointF(p2.x() - ux * node_radius, p2.y() - uy * node_radius)

        path = QPainterPath()
        path.moveTo(start_pt)

        if self.bend_factor == 0:
            # Straight arrow
            path.lineTo(end_pt)
            mid_pt = (start_pt + end_pt) / 2
            angle = math.atan2(dy, dx)
        else:
            # Curved arrow - offset perpendicular to the line
            mid_x = (start_pt.x() + end_pt.x()) / 2
            mid_y = (start_pt.y() + end_pt.y()) / 2
            
            # Calculate perpendicular vector (rotated 90 degrees)
            perp_x = -dy
            perp_y = dx
            perp_len = math.sqrt(perp_x**2 + perp_y**2)
            
            if perp_len > 0:
                perp_x /= perp_len
                perp_y /= perp_len
            
            # Key fix: Determine which side based on the sign of the cross product
            # This ensures Place->Trans always curves opposite to Trans->Place
            # Use a consistent method: check the determinant sign
            cross = perp_x * 1 + perp_y * 0  # dot with reference vector (1,0)
            
            # Force opposite directions for bidirectional arrows
            if self.bend_direction > 0:
                # Place -> Transition: always curve in positive perpendicular direction
                if cross < 0:
                    perp_x, perp_y = -perp_x, -perp_y
            else:
                # Transition -> Place: always curve in negative perpendicular direction
                if cross > 0:
                    perp_x, perp_y = -perp_x, -perp_y
            
            offset = abs(self.bend_factor)
            ctrl_pt = QPointF(mid_x + perp_x * offset, mid_y + perp_y * offset)
            
            path.quadTo(ctrl_pt, end_pt)
            mid_pt = ctrl_pt
            angle = math.atan2(end_pt.y() - ctrl_pt.y(), end_pt.x() - ctrl_pt.x())

        self.setPath(path)

        # Update Arrowhead
        arrow_size = 10
        p_head = QPolygonF([
            QPointF(0, 0),
            QPointF(-arrow_size, arrow_size/3),
            QPointF(-arrow_size, -arrow_size/3)
        ])
        self.head_item.setPolygon(p_head)
        self.head_item.setPos(end_pt)
        self.head_item.setRotation(math.degrees(angle))

        if self.weight_label.isVisible():
            self.weight_label.setPos(mid_pt.x() + 5, mid_pt.y() - 10)
    
    def delete(self, scene):
        scene.removeItem(self)