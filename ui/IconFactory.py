from PyQt6.QtGui import QPixmap, QPainter, QPen, QColor, QFont, QIcon
from PyQt6.QtCore import Qt, QRectF

class IconFactory:
    @staticmethod
    def create_icon(name):
        pixmap = QPixmap(50, 50)
        pixmap.fill(Qt.GlobalColor.transparent)
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        pen_black = QPen(Qt.GlobalColor.black, 2)
        painter.setPen(pen_black)

        if name == "circle":
            painter.setBrush(QColor("white"))
            painter.drawEllipse(10, 10, 30, 30)
        elif name == "square":
            painter.setBrush(QColor("white"))
            painter.drawRect(10, 10, 30, 30)
        elif name == "arrow":
            painter.drawLine(10, 40, 40, 10)
            painter.drawLine(40, 10, 25, 10)
            painter.drawLine(40, 10, 40, 25)
        elif name == "erase":
            painter.translate(25, 25)
            painter.rotate(45)
            painter.translate(-25, -25)
            painter.setBrush(QColor("#ff99cc"))
            painter.drawRect(15, 12, 20, 15)
            painter.setBrush(QColor("#66b3ff"))
            painter.drawRect(15, 27, 20, 10)
        elif name == "stop":
            painter.setBrush(QColor("#d32f2f"))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawRoundedRect(8, 8, 34, 34, 4, 4)
            painter.setBrush(QColor("white"))
            painter.drawRect(18, 18, 14, 14)
        elif name == "info":
            painter.setBrush(QColor("#1976D2"))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawEllipse(8, 8, 34, 34)
            painter.setPen(QPen(Qt.GlobalColor.white, 4))
            font = QFont("Arial", 20, QFont.Weight.Bold)
            painter.setFont(font)
            painter.drawText(QRectF(8, 8, 34, 34), Qt.AlignmentFlag.AlignCenter, "i")
        elif name == "graph":
            painter.setPen(QPen(QColor("#555"), 2))
            painter.drawLine(10, 40, 25, 10)
            painter.drawLine(25, 10, 40, 40)
            painter.drawLine(40, 40, 10, 40)
            painter.setPen(Qt.GlobalColor.black)
            colors = ["#FFCDD2", "#C8E6C9", "#BBDEFB"]
            coords = [(10, 40), (25, 10), (40, 40)]
            for i, (x, y) in enumerate(coords):
                painter.setBrush(QColor(colors[i]))
                painter.drawEllipse(x-4, y-4, 8, 8)
        elif name == "save":
            painter.setBrush(QColor("#4CAF50"))
            painter.drawRect(10, 10, 30, 30)
            painter.setBrush(QColor("white"))
            painter.drawRect(15, 15, 20, 12)
        elif name == "save_as":
            painter.setBrush(QColor("#FFC107"))
            painter.drawRect(10, 10, 30, 30)
            painter.setBrush(QColor("white"))
            painter.drawRect(15, 15, 20, 12)
            painter.setPen(QPen(Qt.GlobalColor.black, 1))
            painter.drawText(22, 45, "As")
        elif name == "new":
            painter.setBrush(QColor("white"))
            painter.drawRect(10, 8, 24, 34)
            painter.drawLine(34, 8, 34, 42)
            painter.drawLine(10, 42, 34, 42)
            painter.setPen(QPen(QColor("#4CAF50"), 3))
            painter.drawLine(34, 25, 46, 25)
            painter.drawLine(40, 19, 40, 31)

        painter.end()
        return QIcon(pixmap)