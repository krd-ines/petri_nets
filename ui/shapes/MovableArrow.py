from PyQt6.QtWidgets import (
    QGraphicsLineItem, QGraphicsPolygonItem, QGraphicsItem,
    QGraphicsTextItem, QInputDialog
)
from PyQt6.QtGui import QPen, QBrush, QPolygonF
from PyQt6.QtCore import Qt, QPointF

class MovableArrow(QGraphicsLineItem):
    def __init__(self, start_item, end_item, start_label, end_label, parent=None):
        super().__init__(parent)

        self.start_item = start_item
        self.end_item = end_item
        self.start_label = start_label
        self.end_label = end_label

        # Default weight (credential) is 1
        self.weight = 1

        # Thinner Line (Width 1)
        self.setPen(QPen(Qt.GlobalColor.black, 1))
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable, True)

        # Create Arrowhead (Child Item)
        self.head_item = QGraphicsPolygonItem(self)
        self.head_item.setPen(QPen(Qt.GlobalColor.black, 1))
        self.head_item.setBrush(QBrush(Qt.GlobalColor.black))

        # Create Label for Weight (Child Item)
        self.weight_label = QGraphicsTextItem("", self)
        self.weight_label.setDefaultTextColor(Qt.GlobalColor.black)
        self.weight_label.setVisible(False)

        # Initial geometry calculation
        self.update_geometry()

    def mouseDoubleClickEvent(self, event):
        """Handle double-click to set arc weight/credential."""
        if event.button() == Qt.MouseButton.LeftButton:
            new_weight, ok = QInputDialog.getInt(
                None, "Set Arc Weight", "Enter weight (credential):",
                self.weight, 1, 100, 1
            )
            if ok:
                self.set_weight(new_weight)
        super().mouseDoubleClickEvent(event)

    def set_weight(self, value):
        self.weight = value
        if self.weight > 1:
            self.weight_label.setPlainText(str(self.weight))
            self.weight_label.setVisible(True)
            self.update_label_position()
        else:
            self.weight_label.setVisible(False)

    def update_geometry(self):
        # 1. Get centers
        start_center = self.start_item.scenePos()
        end_center = self.end_item.scenePos()

        # 2. Calculate Vector
        direction = end_center - start_center
        length = (direction.x()**2 + direction.y()**2) ** 0.5

        # Avoid division by zero
        if length == 0: return

        # Normalize (Unit Vector)
        unit = QPointF(direction.x()/length, direction.y()/length)

        # --- FIX: Start AND End at Outline ---
        node_radius = 20

        # If nodes are overlapping or too close, don't draw weird inverted lines
        if length <= 2 * node_radius:
            self.setLine(start_center.x(), start_center.y(), start_center.x(), start_center.y())
            self.head_item.setPolygon(QPolygonF()) # Hide head
            return

        # Start Point: Shift 'radius' forward from start center
        start_point = start_center + (unit * node_radius)

        # End Point: Shift 'radius' backward from end center
        end_point = end_center - (unit * node_radius)

        # Set the line connecting these two edge points
        self.setLine(start_point.x(), start_point.y(), end_point.x(), end_point.y())

        # 3. Calculate Arrowhead shape (at end_point)
        perp = QPointF(-unit.y(), unit.x()) # Perpendicular vector
        arrow_size = 10

        p1 = end_point
        p2 = end_point - unit * arrow_size + perp * (arrow_size / 3)
        p3 = end_point - unit * arrow_size - perp * (arrow_size / 3)

        self.head_item.setPolygon(QPolygonF([p1, p2, p3]))

        # 4. Update Label
        self.update_label_position()

    def update_label_position(self):
        if not self.weight_label.isVisible(): return

        line = self.line()
        mid_x = (line.x1() + line.x2()) / 2
        mid_y = (line.y1() + line.y2()) / 2

        self.weight_label.setPos(mid_x + 5, mid_y - 20)

    def delete(self, scene):
        scene.removeItem(self)