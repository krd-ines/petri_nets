import base64
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QTextBrowser, QPushButton
from PyQt6.QtGui import QPixmap, QPainter, QColor, QPen
from PyQt6.QtCore import QBuffer, QIODevice, QByteArray, Qt, QSize
from ui.IconFactory import IconFactory

class HelpDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Petri Net Architect - User Guide")

        # Compact window size
        self.resize(600, 520)

        # 1. WINDOW STYLE
        self.setStyleSheet("""
            QDialog {
                background-color: #f0f0f0; 
            }
            QTextBrowser {
                background-color: transparent;
                border: none;
            }
            QPushButton {
                background-color: #5DADE2; 
                color: white; 
                border-radius: 20px; 
                padding: 10px 30px;
                font-family: 'Segoe UI', sans-serif;
                font-weight: bold;
                font-size: 14px;
                margin: 10px;
            }
            QPushButton:hover {
                background-color: #3498DB;
            }
            QPushButton:pressed {
                background-color: #2980B9;
            }
            QScrollBar:vertical {
                border: none;
                background: #e0e0e0;
                width: 8px;
                margin: 0px;
            }
            QScrollBar::handle:vertical {
                background: #bdc3c7;
                border-radius: 4px;
            }
        """)

        try:
            self.setWindowIcon(IconFactory.create_icon("help"))
        except:
            pass

        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 10, 15, 10)

        # 2. GENERATE CRISP ICONS
        # We generate them at 2x size (32px) but display at 1x size (16px) for sharpness.

        # Tool Icons
        icon_place = self.get_icon_tag("circle")
        icon_trans = self.get_icon_tag("square")
        icon_arc   = self.get_icon_tag("arrow")
        icon_stop  = self.get_icon_tag("stop")
        icon_erase = self.get_icon_tag("erase")
        icon_tree  = self.get_icon_tag("tree_graph")

        # Legend Color Boxes (Lavender, Green, Red)
        img_new  = self.get_color_box_tag("#CCCCFF")
        img_done = self.get_color_box_tag("#CCFFCC")
        img_dead = self.get_color_box_tag("#FFCCCC")

        # 3. CONTENT
        guide_content = f"""
        <style>
            body {{
                font-family: 'Segoe UI', sans-serif;
                color: #333;
                background-color: transparent;
                margin: 0; padding: 5px;
            }}
            
            h1 {{
                color: #2c3e50;
                font-size: 24px;
                margin-bottom: 5px;
                text-align: center;
                border-bottom: 2px solid #5DADE2;
                padding-bottom: 10px;
            }}

            h3 {{
                color: #2980b9; 
                font-size: 16px; 
                margin-top: 20px; 
                margin-bottom: 10px;
                text-transform: uppercase;
                letter-spacing: 1px;
            }}

            p, li, td {{ font-size: 13px; line-height: 1.6; color: #444; }}
            ul {{ padding-left: 20px; }}
            li {{ margin-bottom: 6px; }}
            
            table {{ width: 100%; border-collapse: separate; border-spacing: 2px; }}
            td {{ vertical-align: middle; padding: 3px; }}
            
            .key {{
                background-color: #ffffff;
                border: 1px solid #bdc3c7;
                border-bottom: 2px solid #95a5a6;
                border-radius: 4px;
                padding: 1px 6px;
                font-weight: bold;
                color: #555;
            }}
            
            .prop-name {{ font-weight: bold; color: #E67E22; }}
        </style>

        <h1>📘 User Manual</h1>
        <p align="center" style="color:#7f8c8d; font-style:italic;">Petri Net Architect Guide</p>

        <h3>1. Drawing Tools</h3>
        <table border="0">
            <tr>
                <td width="24" align="center">{icon_place}</td>
                <td><b>Place:</b> Click canvas to add a state.</td>
            </tr>
            <tr>
                <td align="center">{icon_trans}</td>
                <td><b>Transition:</b> Click canvas to add an event.</td>
            </tr>
            <tr>
                <td align="center">{icon_arc}</td>
                <td><b>Arc:</b> Connect nodes. 
                    <br><span style="color:#7f8c8d; font-size:12px;">(Click Source &rarr; Right click Destination)</span>
                </td>
            </tr>
            <tr>
                <td align="center">{icon_stop}</td>
                <td><b>Stop:</b> <span style="color:#e74c3c; font-weight:bold;">Exit Drawing.</span> Select & move items.</td>
            </tr>
             <tr>
                <td align="center">{icon_erase}</td>
                <td><b>Erase:</b> Click items to delete.</td>
            </tr>
        </table>

        <h3>2. Shortcuts & Editing</h3>
        <ul>
            <li><b>Edit Tokens:</b> Double-click a <span class="key">Place</span> to set number of tokens.</li>
            <li><b>Edit Weight:</b> Double-click an <span class="key">Arc</span> to set weight.</li>
            <li><b>Move Nodes:</b> Select {icon_stop} <b>Stop</b>, then drag.</li>
            <li><b>Zoom:</b> Use <span class="key">Mouse Wheel</span>.</li>
        </ul>

        <h3>3. Analysis Results</h3>
        <p>"Full Build" and "Step Build" buttons generate a coverability tree graph that follows this legend:</p>
        
        <table border="0" cellspacing="4">
            <tr>
                <td width="20" align="center">{img_new}</td>
                <td><b>New Marking:</b> A newly discovered marking that still needs to be explored.</td>
            </tr>
            <tr>
                <td align="center">{img_done}</td>
                <td><b>Done Marking:</b> A marking already fully explored.</td>
            </tr>
            <tr>
                <td align="center">{img_dead}</td>
                <td><b>Dead-End:</b> A marking where no more exploring is possible.</td>
            </tr>
        </table>

        <h3>4. Properties Defined</h3>
        
        <p><span class="prop-name">Bounded:</span> Is the graph finite?
        <br>&nbsp;• <b style="color:#27ae60">YES:</b> Tokens never reach infinity.
        <br>&nbsp;• <b style="color:#c0392b">NO:</b> Infinite growth.</p>

        <p><span class="prop-name">Quasi-Live:</span> Is the graph quasi-live?
        <br>&nbsp;• <b style="color:#27ae60">YES:</b> All transitions can fire eventually from at least one marking.
        <br>&nbsp;• <b style="color:#c0392b">NO:</b> Some transitions are not fired at all.</p>

        <p><span class="prop-name">Live:</span> Is the graph live?
        <br>&nbsp;• <b style="color:#27ae60">YES:</b> Transitions can always fire from any marking.
        <br>&nbsp;• <b style="color:#c0392b">NO:</b> It can get stuck/dead-end.</p>

        <p><span class="prop-name">Reversible:</span> Can the graph be reset?
        <br>&nbsp;• <b style="color:#27ae60">YES:</b> It can always return to start marking.</p>
        <br>&nbsp;• <b style="color:#c0392b">NO:</b> It cannot always return to start marking.</p>
        """

        self.browser = QTextBrowser()
        self.browser.setHtml(guide_content)
        self.browser.setOpenExternalLinks(True)
        self.browser.setFrameShape(QTextBrowser.Shape.NoFrame)
        layout.addWidget(self.browser)

        # 3. Floating Button at Bottom
        btn_close = QPushButton("Got it!")
        btn_close.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_close.clicked.connect(self.accept)
        layout.addWidget(btn_close, alignment=Qt.AlignmentFlag.AlignCenter)

    def get_icon_tag(self, icon_name):
        """Gets icon at 2x resolution (36px) and scales down in HTML to 18px for sharpness."""
        try:
            icon = IconFactory.create_icon(icon_name)
            # Fetch high-res pixmap (36x36)
            pixmap = icon.pixmap(36, 36)
            # Display smaller (18x18)
            return self._pixmap_to_html(pixmap, display_size=18)
        except:
            return ""

    def get_color_box_tag(self, color_hex):
        """Creates a high-res (32px) square image, displays as 14px."""
        # 1. Create a larger canvas (32x32) for high DPI clarity
        size = 32
        pixmap = QPixmap(size, size)
        pixmap.fill(QColor("transparent"))

        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # 2. Draw Box
        painter.setBrush(QColor(color_hex))
        # Thicker pen (2px) so it looks like 1px when scaled down by half
        pen = QPen(QColor("#555555"), 2)
        painter.setPen(pen)

        # Draw slightly inside so border doesn't get clipped
        painter.drawRect(1, 1, size-2, size-2)
        painter.end()

        # 3. Display at small size (14px)
        return self._pixmap_to_html(pixmap, display_size=14)

    def _pixmap_to_html(self, pixmap, display_size):
        """Encodes pixmap to Base64 and forces HTML width/height."""
        byte_array = QByteArray()
        buffer = QBuffer(byte_array)
        buffer.open(QIODevice.OpenModeFlag.WriteOnly)
        pixmap.save(buffer, "PNG")
        base64_data = byte_array.toBase64().data().decode()
        return f'<img src="data:image/png;base64,{base64_data}" width="{display_size}" height="{display_size}" style="vertical-align: middle;">'