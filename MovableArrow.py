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

        # Visual Setup
        self.setPen(QPen(Qt.GlobalColor.black, 2))
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable, True)

        # Create Arrowhead (Child Item)
        self.head_item = QGraphicsPolygonItem(self)
        self.head_item.setPen(QPen(Qt.GlobalColor.black))
        self.head_item.setBrush(QBrush(Qt.GlobalColor.black))

        # Create Label for Weight (Child Item)
        self.weight_label = QGraphicsTextItem("", self)
        self.weight_label.setDefaultTextColor(Qt.GlobalColor.black)
        self.weight_label.setVisible(False)  # Hidden by default (for weight 1)

        # Initial geometry calculation
        self.update_geometry()

    def mouseDoubleClickEvent(self, event):
        """Handle double-click to set arc weight/credential."""
        if event.button() == Qt.MouseButton.LeftButton:
            # Ask user for an integer
            new_weight, ok = QInputDialog.getInt(
                None,
                "Set Arc Weight",
                "Enter weight (credential):",
                self.weight,
                1, 100, 1
            )

            if ok:
                self.set_weight(new_weight)

        super().mouseDoubleClickEvent(event)

    def set_weight(self, value):
        self.weight = value
        # Only show the label if weight > 1 (Standard Petri Net convention)
        if self.weight > 1:
            self.weight_label.setPlainText(str(self.weight))
            self.weight_label.setVisible(True)
            self.update_label_position()
        else:
            self.weight_label.setVisible(False)

    def update_geometry(self):
        # 1. Get the current dynamic position of the start and end nodes
        start_center = self.start_item.scenePos()
        end_center = self.end_item.scenePos()

        # 2. Update the straight line connecting them
        self.setLine(start_center.x(), start_center.y(), end_center.x(), end_center.y())

        # 3. Calculate the direction vector for the arrowhead
        direction = end_center - start_center
        length = (direction.x()**2 + direction.y()**2) ** 0.5

        if length == 0:
            return

        # Normalize the vector (unit vector)
        unit = QPointF(direction.x()/length, direction.y()/length)
        # Calculate perpendicular vector for the base of the arrow triangle
        perp = QPointF(-unit.y(), unit.x())

        arrow_size = 10

        # 4. Calculate triangle points
        # Tip of the arrow (at the center of the end node)
        p1 = end_center
        # Base corners
        p2 = end_center - unit * arrow_size + perp * arrow_size / 2
        p3 = end_center - unit * arrow_size - perp * arrow_size / 2

        # 5. Set the polygon
        arrow_head = QPolygonF([p1, p2, p3])
        self.head_item.setPolygon(arrow_head)

        # 6. Update label position
        self.update_label_position()

    def update_label_position(self):
        if not self.weight_label.isVisible():
            return

        line = self.line()
        # Calculate midpoint of the line
        mid_x = (line.x1() + line.x2()) / 2
        mid_y = (line.y1() + line.y2()) / 2

        # Position label slightly offset from the midpoint so it doesn't cover the line
        # Adjust (-10, -20) as needed to look good
        self.weight_label.setPos(mid_x + 5, mid_y - 20)

    def delete(self, scene):
        scene.removeItem(self)