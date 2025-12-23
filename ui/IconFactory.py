from PyQt6.QtGui import QPixmap, QPainter, QPen, QColor, QFont, QIcon, QBrush, QLinearGradient
from PyQt6.QtCore import Qt, QRectF, QPointF

class IconFactory:
    @staticmethod
    def create_icon(name):
        pixmap = QPixmap(64, 64)
        pixmap.fill(Qt.GlobalColor.transparent)
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        if name == "circle":
            # Simple circle like original
            painter.setBrush(QColor("white"))
            painter.setPen(QPen(Qt.GlobalColor.black, 3))
            painter.drawEllipse(12, 12, 40, 40)
            
        elif name == "square":
            # Simple square like original
            painter.setBrush(QColor("lightgray"))
            painter.setPen(QPen(Qt.GlobalColor.black, 3))
            painter.drawRect(12, 12, 40, 40)
            
        elif name == "arrow":
            # Simple arrow like original
            painter.setPen(QPen(Qt.GlobalColor.black, 3))
            painter.drawLine(12, 52, 52, 12)
            painter.drawLine(52, 12, 34, 12)
            painter.drawLine(52, 12, 52, 30)
            
        elif name == "erase":
            # Eraser with dark outline for visibility
            painter.translate(32, 32)
            painter.rotate(45)
            # Dark outline
            painter.setPen(QPen(QColor("#424242"), 2))
            painter.setBrush(QColor("#FF6B6B"))
            painter.drawRoundedRect(-13, -19, 24, 24, 3, 3)
            # Metal band
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QColor("#757575"))
            painter.drawRect(-13, 5, 24, 4)
            # Rubber tip with darker border
            painter.setPen(QPen(QColor("#9E9E9E"), 1.5))
            painter.setBrush(QColor("#FFD54F"))
            painter.drawRoundedRect(-13, 9, 24, 8, 2, 2)
            
        elif name == "stop":
            # Modern stop/select button
            painter.setPen(Qt.PenStyle.NoPen)
            # Outer circle shadow
            painter.setBrush(QColor(0, 0, 0, 20))
            painter.drawEllipse(11, 11, 44, 44)
            # Main circle
            gradient = QLinearGradient(0, 10, 0, 54)
            gradient.setColorAt(0, QColor("#E53935"))
            gradient.setColorAt(1, QColor("#C62828"))
            painter.setBrush(gradient)
            painter.drawEllipse(10, 10, 44, 44)
            # Inner square (hand symbol)
            painter.setBrush(QColor("white"))
            painter.drawRoundedRect(22, 22, 20, 20, 2, 2)
            
        elif name == "info":
            # Modern info button
            painter.setPen(Qt.PenStyle.NoPen)
            # Shadow
            painter.setBrush(QColor(0, 0, 0, 20))
            painter.drawEllipse(11, 11, 44, 44)
            # Circle gradient
            gradient = QLinearGradient(0, 10, 0, 54)
            gradient.setColorAt(0, QColor("#42A5F5"))
            gradient.setColorAt(1, QColor("#1976D2"))
            painter.setBrush(gradient)
            painter.drawEllipse(10, 10, 44, 44)
            # Info icon
            painter.setPen(QPen(Qt.GlobalColor.white, 5, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
            painter.drawLine(32, 28, 32, 44)
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QColor("white"))
            painter.drawEllipse(29, 18, 6, 6)
            
        elif name == "graph":
            # Modern tree/graph visualization icon
            painter.setPen(QPen(QColor("#9E9E9E"), 2.5))
            # Connections
            painter.drawLine(32, 18, 20, 35)
            painter.drawLine(32, 18, 44, 35)
            painter.drawLine(20, 35, 32, 50)
            # Nodes with gradients
            nodes = [(32, 18, "#4CAF50"), (20, 35, "#2196F3"), (44, 35, "#FF9800"), (32, 50, "#E91E63")]
            for x, y, color in nodes:
                gradient = QLinearGradient(x-6, y-6, x+6, y+6)
                gradient.setColorAt(0, QColor(color).lighter(120))
                gradient.setColorAt(1, QColor(color))
                painter.setBrush(gradient)
                painter.setPen(QPen(QColor(color).darker(140), 2))
                painter.drawEllipse(x-6, y-6, 12, 12)
            
        elif name == "save":
            # Modern floppy disk icon
            painter.setPen(Qt.PenStyle.NoPen)
            # Shadow
            painter.setBrush(QColor(0, 0, 0, 20))
            painter.drawRoundedRect(11, 11, 44, 44, 4, 4)
            # Main body gradient
            gradient = QLinearGradient(0, 10, 0, 54)
            gradient.setColorAt(0, QColor("#66BB6A"))
            gradient.setColorAt(1, QColor("#43A047"))
            painter.setBrush(gradient)
            painter.drawRoundedRect(10, 10, 44, 44, 4, 4)
            # Label area (white)
            painter.setBrush(QColor("white"))
            painter.drawRoundedRect(16, 16, 32, 20, 2, 2)
            # Bottom metal flap
            painter.setBrush(QColor("#2E7D32"))
            painter.drawRect(10, 42, 44, 12)
            # Save notch
            painter.setBrush(QColor("#1B5E20"))
            painter.drawRect(38, 10, 10, 12)
            
        elif name == "save_as":
            # Save As variant with accent
            painter.setPen(Qt.PenStyle.NoPen)
            # Shadow
            painter.setBrush(QColor(0, 0, 0, 20))
            painter.drawRoundedRect(11, 11, 44, 44, 4, 4)
            # Main body gradient (orange)
            gradient = QLinearGradient(0, 10, 0, 54)
            gradient.setColorAt(0, QColor("#FFA726"))
            gradient.setColorAt(1, QColor("#FB8C00"))
            painter.setBrush(gradient)
            painter.drawRoundedRect(10, 10, 44, 44, 4, 4)
            # Label area
            painter.setBrush(QColor("white"))
            painter.drawRoundedRect(16, 16, 32, 20, 2, 2)
            # Bottom metal
            painter.setBrush(QColor("#E65100"))
            painter.drawRect(10, 42, 44, 12)
            # Notch
            painter.setBrush(QColor("#BF360C"))
            painter.drawRect(38, 10, 10, 12)
            # Plus badge
            painter.setBrush(QColor("#4CAF50"))
            painter.drawEllipse(40, 40, 18, 18)
            painter.setPen(QPen(QColor("white"), 2.5, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
            painter.drawLine(49, 45, 49, 53)
            painter.drawLine(45, 49, 53, 49)
            
        elif name == "new":
            # New document with dark borders
            painter.setPen(QPen(QColor("#424242"), 2.5))
            # Main document
            gradient = QLinearGradient(0, 10, 0, 54)
            gradient.setColorAt(0, QColor("#FFFFFF"))
            gradient.setColorAt(1, QColor("#F5F5F5"))
            painter.setBrush(gradient)
            painter.drawRoundedRect(12, 10, 32, 44, 3, 3)
            # Folded corner
            painter.setPen(QPen(QColor("#424242"), 2))
            painter.setBrush(QColor("#E0E0E0"))
            from PyQt6.QtGui import QPolygonF
            corner = QPolygonF([QPointF(44, 10), QPointF(44, 22), QPointF(32, 10)])
            painter.drawPolygon(corner)
            # Plus badge with shadow
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QColor(0, 0, 0, 25))
            painter.drawEllipse(39, 39, 20, 20)
            painter.setBrush(QColor("#4CAF50"))
            painter.drawEllipse(38, 38, 20, 20)
            painter.setPen(QPen(QColor("white"), 3, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
            painter.drawLine(48, 43, 48, 53)
            painter.drawLine(43, 48, 53, 48)

        elif name == "zoom_in":
            # Magnifying glass with plus
            painter.setPen(Qt.PenStyle.NoPen)
            # Handle shadow
            painter.setBrush(QColor(0, 0, 0, 25))
            painter.drawRoundedRect(36, 36, 22, 8, 3, 3)
            painter.rotate(45)
            painter.drawRoundedRect(24, -6, 20, 8, 3, 3)
            painter.rotate(-45)
            # Glass circle
            painter.setPen(QPen(QColor("#424242"), 3))
            gradient = QLinearGradient(14, 14, 36, 36)
            gradient.setColorAt(0, QColor("#E3F2FD"))
            gradient.setColorAt(1, QColor("#BBDEFB"))
            painter.setBrush(gradient)
            painter.drawEllipse(14, 14, 28, 28)
            # Handle
            painter.setPen(QPen(QColor("#424242"), 4, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
            painter.drawLine(36, 36, 50, 50)
            # Plus sign
            painter.setPen(QPen(QColor("#1976D2"), 3, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
            painter.drawLine(28, 22, 28, 34)
            painter.drawLine(22, 28, 34, 28)
            
        elif name == "zoom_out":
            # Magnifying glass with minus
            painter.setPen(Qt.PenStyle.NoPen)
            # Handle shadow
            painter.setBrush(QColor(0, 0, 0, 25))
            painter.drawRoundedRect(36, 36, 22, 8, 3, 3)
            painter.rotate(45)
            painter.drawRoundedRect(24, -6, 20, 8, 3, 3)
            painter.rotate(-45)
            # Glass circle
            painter.setPen(QPen(QColor("#424242"), 3))
            gradient = QLinearGradient(14, 14, 36, 36)
            gradient.setColorAt(0, QColor("#E3F2FD"))
            gradient.setColorAt(1, QColor("#BBDEFB"))
            painter.setBrush(gradient)
            painter.drawEllipse(14, 14, 28, 28)
            # Handle
            painter.setPen(QPen(QColor("#424242"), 4, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
            painter.drawLine(36, 36, 50, 50)
            # Minus sign
            painter.setPen(QPen(QColor("#1976D2"), 3, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
            painter.drawLine(22, 28, 34, 28)
            
        elif name == "save_image":
            # Image/photo icon with download arrow
            painter.setPen(Qt.PenStyle.NoPen)
            # Shadow
            painter.setBrush(QColor(0, 0, 0, 20))
            painter.drawRoundedRect(11, 11, 44, 44, 4, 4)
            # Photo frame
            gradient = QLinearGradient(0, 10, 0, 54)
            gradient.setColorAt(0, QColor("#42A5F5"))
            gradient.setColorAt(1, QColor("#1976D2"))
            painter.setBrush(gradient)
            painter.drawRoundedRect(10, 10, 44, 44, 4, 4)
            # Inner white area (like a photo)
            painter.setBrush(QColor("#E3F2FD"))
            painter.drawRoundedRect(15, 15, 34, 28, 2, 2)
            # Mountain silhouette in photo
            painter.setBrush(QColor("#90CAF9"))
            from PyQt6.QtGui import QPolygonF
            mountain = QPolygonF([QPointF(15, 43), QPointF(25, 28), QPointF(35, 35), QPointF(49, 20), QPointF(49, 43)])
            painter.drawPolygon(mountain)
            # Sun in photo
            painter.setBrush(QColor("#FFD54F"))
            painter.drawEllipse(37, 19, 8, 8)
            # Bottom download bar
            painter.setBrush(QColor("#0D47A1"))
            painter.drawRect(10, 44, 44, 10)
            # Download arrow
            painter.setPen(QPen(QColor("white"), 2, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
            painter.drawLine(32, 47, 32, 52)
            # Arrow head
            painter.setBrush(QColor("white"))
            painter.setPen(Qt.PenStyle.NoPen)
            arrow_head = QPolygonF([QPointF(32, 53), QPointF(28, 49), QPointF(36, 49)])
            painter.drawPolygon(arrow_head)
            
        elif name == "explore":
            # Simple search/magnifying glass icon
            painter.setPen(QPen(QColor("#424242"), 3))
            painter.setBrush(Qt.BrushStyle.NoBrush)
            # Glass circle
            painter.drawEllipse(16, 16, 24, 24)
            # Handle
            painter.setPen(QPen(QColor("#424242"), 4, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
            painter.drawLine(36, 36, 48, 48)
            
        elif name == "projects":
            # Folder icon
            painter.setPen(Qt.PenStyle.NoPen)
            # Folder tab
            painter.setBrush(QColor("#FFA726"))
            painter.drawRoundedRect(12, 18, 20, 8, 2, 2)
            # Main folder body
            gradient = QLinearGradient(0, 26, 0, 50)
            gradient.setColorAt(0, QColor("#FFB74D"))
            gradient.setColorAt(1, QColor("#FF9800"))
            painter.setBrush(gradient)
            painter.drawRoundedRect(12, 26, 40, 24, 3, 3)
            # Folder highlight
            painter.setBrush(QColor(255, 255, 255, 50))
            painter.drawRoundedRect(15, 29, 34, 8, 2, 2)
            
        elif name == "net_info":
            # Info document icon
            painter.setPen(Qt.PenStyle.NoPen)
            # Document
            gradient = QLinearGradient(0, 12, 0, 52)
            gradient.setColorAt(0, QColor("#FFFFFF"))
            gradient.setColorAt(1, QColor("#F5F5F5"))
            painter.setBrush(gradient)
            painter.setPen(QPen(QColor("#1976D2"), 2))
            painter.drawRoundedRect(16, 12, 32, 40, 3, 3)
            # Info "i" icon
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QColor("#1976D2"))
            painter.drawEllipse(29, 20, 6, 6)
            painter.drawRoundedRect(29, 30, 6, 16, 2, 2)
            
        elif name == "tree_graph":
            # Light, clean tree graph structure with subtle colors
            painter.setPen(QPen(QColor("#9E9E9E"), 2))
            
            # Connections (thin lines)
            painter.drawLine(32, 20, 20, 32)
            painter.drawLine(32, 20, 32, 32)
            painter.drawLine(32, 20, 44, 32)
            painter.drawLine(20, 32, 16, 44)
            painter.drawLine(20, 32, 24, 44)
            painter.drawLine(44, 32, 40, 44)
            painter.drawLine(44, 32, 48, 44)
            
            # Root node (top) - Green
            painter.setPen(QPen(QColor("#43A047"), 2))
            painter.setBrush(QColor("#81C784"))
            painter.drawEllipse(28, 16, 8, 8)
            
            # Second level nodes - Blue
            painter.setPen(QPen(QColor("#1976D2"), 2))
            painter.setBrush(QColor("#64B5F6"))
            for x in [20, 32, 44]:
                painter.drawEllipse(x-4, 28, 8, 8)
            
            # Third level nodes (leaf nodes) - Orange
            painter.setPen(QPen(QColor("#F57C00"), 2))
            painter.setBrush(QColor("#FFB74D"))
            for x in [16, 24, 40, 48]:
                painter.drawEllipse(x-3, 40, 6, 6)
        
        elif name == "reset_zoom":
            # Arrows pointing outward (expand/fit view)
            painter.setPen(Qt.PenStyle.NoPen)
            # Background circle
            painter.setBrush(QColor("#F5F5F5"))
            painter.drawEllipse(10, 10, 44, 44)
            # Border
            painter.setPen(QPen(QColor("#757575"), 2))
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.drawEllipse(10, 10, 44, 44)
            
            # Four arrows pointing outward (like expand to fit)
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QColor("#424242"))
            
            from PyQt6.QtGui import QPolygonF
            # Top arrow
            top_arrow = QPolygonF([QPointF(32, 18), QPointF(28, 24), QPointF(36, 24)])
            painter.drawPolygon(top_arrow)
            
            # Bottom arrow
            bottom_arrow = QPolygonF([QPointF(32, 46), QPointF(28, 40), QPointF(36, 40)])
            painter.drawPolygon(bottom_arrow)
            
            # Left arrow
            left_arrow = QPolygonF([QPointF(18, 32), QPointF(24, 28), QPointF(24, 36)])
            painter.drawPolygon(left_arrow)
            
            # Right arrow
            right_arrow = QPolygonF([QPointF(46, 32), QPointF(40, 28), QPointF(40, 36)])
            painter.drawPolygon(right_arrow)
            
            # Center dot
            painter.drawEllipse(29, 29, 6, 6)
        
        elif name == "app_icon":
            # Petri Net app icon - Shows a simple place and transition
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)
            
            # Background (optional rounded square)
            painter.setPen(Qt.PenStyle.NoPen)
            gradient = QLinearGradient(0, 0, 64, 64)
            gradient.setColorAt(0, QColor("#7E57C2"))
            gradient.setColorAt(1, QColor("#5E35B1"))
            painter.setBrush(gradient)
            painter.drawRoundedRect(4, 4, 56, 56, 8, 8)
            
            # Place (circle) with token
            painter.setPen(QPen(QColor("#FFFFFF"), 3))
            painter.setBrush(QColor("#FFFFFF"))
            painter.drawEllipse(10, 18, 16, 16)
            # Token dot
            painter.setBrush(QColor("#7E57C2"))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawEllipse(15, 23, 6, 6)
            
            # Arrow
            painter.setPen(QPen(QColor("#FFFFFF"), 3, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
            painter.drawLine(26, 26, 38, 26)
            # Arrowhead
            painter.setBrush(QColor("#FFFFFF"))
            painter.setPen(Qt.PenStyle.NoPen)
            from PyQt6.QtGui import QPolygonF
            arrow_head = QPolygonF([QPointF(38, 26), QPointF(33, 23), QPointF(33, 29)])
            painter.drawPolygon(arrow_head)
            
            # Transition (rectangle)
            painter.setPen(QPen(QColor("#FFFFFF"), 3))
            painter.setBrush(QColor("#9E9E9E"))
            painter.drawRect(38, 18, 16, 16)

        painter.end()
        return QIcon(pixmap)