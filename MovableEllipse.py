from PyQt6.QtWidgets import QGraphicsEllipseItem, QGraphicsTextItem, QGraphicsItem, QInputDialog
from PyQt6.QtGui import QPen, QBrush
from PyQt6.QtCore import Qt, QRectF

class MovableEllipse(QGraphicsEllipseItem):
    def __init__(self, position, label_text, editor):
        self.radius = 20
        rect = QRectF(-self.radius, -self.radius, 2 * self.radius, 2 * self.radius)
        super().__init__(rect)

        self.editor = editor
        self.label_text = label_text
        self.tokens = 0   # default tokens
        self.token_items = []  # graphics for dots

        # Visuals
        self.setBrush(QBrush(Qt.GlobalColor.white))
        self.setPen(QPen(Qt.GlobalColor.black))
        self.setPos(position)

        # Interaction Flags
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable, True)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable, True)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemSendsGeometryChanges, True)

        # Label
        self.label_item = QGraphicsTextItem(label_text, self)
        lb_rect = self.label_item.boundingRect()
        self.label_item.setPos(-lb_rect.width() / 2, -self.radius - lb_rect.height() - 2)

    def itemChange(self, change, value):
        if change == QGraphicsItem.GraphicsItemChange.ItemPositionHasChanged:
            self.editor.update_arrows(self.label_text)
        return super().itemChange(change, value)

    def delete(self, scene):
        scene.removeItem(self)

    # --- CHANGED: Replaced contextMenuEvent with mouseDoubleClickEvent ---
    def mouseDoubleClickEvent(self, event):
        """Double-click (Left) -> ask for number of tokens"""
        if event.button() == Qt.MouseButton.LeftButton:
            num, ok = QInputDialog.getInt(
                None,
                "Set Tokens",
                f"Tokens for {self.label_text}:",
                self.tokens,
                0, 20, 1
            )
            if ok:
                self.set_tokens(num)

        # Call parent to keep standard selection behavior
        super().mouseDoubleClickEvent(event)

    def set_tokens(self, num):
        """Update token count and redraw dots"""
        self.tokens = num

        # remove old dots
        # Check if items are in a scene before trying to remove them from it
        if self.scene():
            for dot in self.token_items:
                self.scene().removeItem(dot)

        self.token_items.clear()

        # draw new dots
        spacing = 8
        start_x = -((num-1) * spacing) / 2
        for i in range(num):
            dot = QGraphicsEllipseItem(-3, -3, 6, 6, self)
            dot.setBrush(QBrush(Qt.GlobalColor.black))
            dot.setPos(start_x + i*spacing, 0)
            self.token_items.append(dot)