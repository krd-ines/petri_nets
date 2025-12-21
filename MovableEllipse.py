from PyQt6.QtWidgets import QGraphicsEllipseItem, QGraphicsTextItem, QGraphicsItem
from PyQt6.QtGui import QPen, QBrush
from PyQt6.QtCore import Qt, QRectF

class MovableEllipse(QGraphicsEllipseItem):
    def __init__(self, position, label_text, editor):
        radius = 20
        rect = QRectF(-radius, -radius, 2 * radius, 2 * radius)
        super().__init__(rect)

        self.editor = editor
        self.label_text = label_text

        # Visuals
        self.setBrush(QBrush(Qt.GlobalColor.white))
        self.setPen(QPen(Qt.GlobalColor.black))
        self.setPos(position)

        # Interaction Flags
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable, True)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable, True)
        # Crucial: this ensures itemChange is called when position changes
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemSendsGeometryChanges, True)

        # Label
        self.label_item = QGraphicsTextItem(label_text, self)
        lb_rect = self.label_item.boundingRect()
        self.label_item.setPos(-lb_rect.width() / 2, -radius - lb_rect.height() - 2)

    def itemChange(self, change, value):
        # DETECT MOVEMENT
        if change == QGraphicsItem.GraphicsItemChange.ItemPositionHasChanged:
            # Tell the editor to update arrows connected to this node
            self.editor.update_arrows(self.label_text)

        return super().itemChange(change, value)

    def delete(self, scene):
        scene.removeItem(self)