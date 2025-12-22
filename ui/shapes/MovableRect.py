from PyQt6.QtWidgets import QGraphicsRectItem, QGraphicsTextItem, QGraphicsItem
from PyQt6.QtGui import QPen, QBrush
from PyQt6.QtCore import Qt, QRectF

class MovableRect(QGraphicsRectItem):
    def __init__(self, position, label_text, editor):
        size = 40
        half = size / 2
        rect = QRectF(-half, -half, size, size)
        super().__init__(rect)

        self.editor = editor
        self.label_text = label_text

        # Visuals
        self.setBrush(QBrush(Qt.GlobalColor.lightGray))
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
        self.label_item.setPos(-lb_rect.width() / 2, -half - lb_rect.height() - 2)

    def itemChange(self, change, value):
        # DETECT MOVEMENT
        if change == QGraphicsItem.GraphicsItemChange.ItemPositionHasChanged:
            # Tell the editor to update arrows connected to this node
            self.editor.update_arrows(self.label_text)

        return super().itemChange(change, value)

    def delete(self, scene):
        scene.removeItem(self)