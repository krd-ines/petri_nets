from PyQt6.QtWidgets import QGraphicsLineItem, QGraphicsPolygonItem, QGraphicsItem
from PyQt6.QtGui import QPen, QBrush, QPolygonF
from PyQt6.QtCore import Qt, QPointF

class MovableArrow(QGraphicsLineItem):
    def __init__(self, start_item, end_item, start_label, end_label):
        super().__init__()

        self.start_item = start_item
        self.end_item = end_item
        self.start_label = start_label
        self.end_label = end_label

        # Visual Setup
        self.setPen(QPen(Qt.GlobalColor.black, 2))
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable, True)

        # Create Arrowhead (Child Item)
        self.head_item = QGraphicsPolygonItem(self)
        self.head_item.setPen(QPen(Qt.GlobalColor.black))
        self.head_item.setBrush(QBrush(Qt.GlobalColor.black))

        # Initial geometry calculation
        self.update_geometry()

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
        # Since MovableArrow is at (0,0) in scene coords (we only changed setLine),
        # we can use scene coordinates for the child polygon.
        arrow_head = QPolygonF([p1, p2, p3])
        self.head_item.setPolygon(arrow_head)

    def delete(self, scene):
        scene.removeItem(self)