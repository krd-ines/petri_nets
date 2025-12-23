from PyQt6.QtGui import QPalette, QColor
from PyQt6.QtCore import Qt

class StyleManager:
    @staticmethod
    def apply_light_theme(app):
        palette = QPalette()
        palette.setColor(QPalette.ColorRole.Window, QColor(240, 240, 240))
        palette.setColor(QPalette.ColorRole.WindowText, Qt.GlobalColor.black)
        palette.setColor(QPalette.ColorRole.Base, Qt.GlobalColor.white)
        palette.setColor(QPalette.ColorRole.Text, Qt.GlobalColor.black)
        palette.setColor(QPalette.ColorRole.Button, QColor(225, 225, 225))
        palette.setColor(QPalette.ColorRole.ButtonText, Qt.GlobalColor.black)
        app.setPalette(palette)
        app.setStyle("Fusion")

    @staticmethod
    def get_main_stylesheet():
        return """
            QDockWidget { font-size: 18px; font-weight: bold; }
            QDockWidget::title { 
                background-color: #f8f9fa; 
                qproperty-alignment: 'AlignLeft | AlignVCenter'; 
            }
        """
    @staticmethod
    def get_dock_style():
        return """
            QDockWidget {
                font-size: 18px;
                font-weight: bold;
            }
            QDockWidget::title {
                background-color: #f8f9fa;
                qproperty-alignment: 'AlignLeft | AlignVCenter';
                /* This forces the font property specifically */
                qproperty-font: 'Segoe UI, 16pt, bold'; 
            }
        """