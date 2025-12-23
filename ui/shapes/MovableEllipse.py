from PyQt6.QtWidgets import QGraphicsEllipseItem, QGraphicsTextItem, QGraphicsItem, QInputDialog
from PyQt6.QtGui import QPen, QBrush, QFont
from PyQt6.QtCore import Qt, QPointF
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
        # Use ItemPositionChange for smoother, real-time arrow updates
        if change == QGraphicsItem.GraphicsItemChange.ItemPositionChange:
            # We must use the 'value' (the new position) or call update_arrows
            # to ensure the geometry re-calculates using the upcoming position.
            if self.editor:
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
        """Update token count and trigger a redraw"""
        # If you still have old child items, remove them one last time
        if hasattr(self, 'token_items'):
            for dot in self.token_items:
                if dot.scene():
                    dot.scene().removeItem(dot)
            self.token_items.clear()
        
        self.tokens = num
        self.update()  # This tells Qt to call the paint() method again

    def paint(self, painter, option, widget):
        # 1. Draw the Ellipse itself (the Place)
        super().paint(painter, option, widget)

        # 2. Draw the Content (Dots or Number)
        painter.setRenderHint(painter.RenderHint.Antialiasing)
        
        if 0 < self.tokens <= 5:
            # NEAT DICE PATTERNS
            painter.setBrush(QBrush(Qt.GlobalColor.black))
            dot_r = 3
            # Coordinates relative to the center (0,0) of the ellipse
            patterns = {
                1: [(0, 0)],
                2: [(-6, 0), (6, 0)],
                3: [(-6, 5), (6, 5), (0, -5)],
                4: [(-6, -6), (6, -6), (-6, 6), (6, 6)],
                5: [(-7, -7), (7, -7), (7, 7), (-7, 7), (0, 0)]
            }
            for px, py in patterns[self.tokens]:
                painter.drawEllipse(QPointF(px, py), dot_r, dot_r)
        
        elif self.tokens > 5:
            # DRAW NUMBER
            painter.setPen(QPen(Qt.GlobalColor.black))
            font = QFont("Segoe UI", 11, QFont.Weight.Bold)
            painter.setFont(font)
            # Center the number inside the circle
            painter.drawText(self.boundingRect(), Qt.AlignmentFlag.AlignCenter, str(self.tokens))