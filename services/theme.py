# services/theme.py
from PySide6.QtGui import QPalette, QColor
from PySide6.QtWidgets import QApplication

PRIMARY = "#006400"
DANGER = "#b22222"
GRAY_LIGHT = "#e0e0e0"
GRAY_TEXT = "#555555"
WHITE = "#ffffff"

APP_QSS = f"""
* {{
  font-family: Tahoma;
}}
QMainWindow, QWidget {{
  background: {WHITE};
  color: {GRAY_TEXT};
}}
QLabel {{
  color: {GRAY_TEXT};
  font-size: 12pt;
}}
QPushButton {{
  background-color: {PRIMARY};
  color: white;
  border: none;
  border-radius: 6px;
  padding: 8px 14px;
  font-weight: bold;
}}
QPushButton:hover {{
  background-color: #0a7a0a;
}}
QPushButton.danger {{
  background-color: {DANGER};
}}
QPushButton.secondary {{
  background-color: {GRAY_LIGHT};
  color: #000;
}}
QTableWidget, QTableView {{
  gridline-color: #000000;
  background: {WHITE};
  alternate-background-color: {GRAY_LIGHT};
  selection-background-color: #cde8cd;
  selection-color: #000;
}}
QHeaderView::section {{
  background-color: {PRIMARY};
  color: white;
  padding: 8px;
  border: 1px solid #000;
  font-weight: bold;
}}
"""

def apply_palette(app: QApplication):
    pal = app.palette()
    pal.setColor(QPalette.Window, QColor(WHITE))
    pal.setColor(QPalette.WindowText, QColor(GRAY_TEXT))
    pal.setColor(QPalette.Base, QColor(WHITE))
    pal.setColor(QPalette.AlternateBase, QColor(GRAY_LIGHT))
    pal.setColor(QPalette.Button, QColor(PRIMARY))
    pal.setColor(QPalette.ButtonText, QColor("#ffffff"))
    pal.setColor(QPalette.Text, QColor("#000000"))
    pal.setColor(QPalette.Highlight, QColor("#cde8cd"))
    pal.setColor(QPalette.HighlightedText, QColor("#000000"))
    app.setPalette(pal)

def apply_app_style(app: QApplication):
    apply_palette(app)
    app.setStyleSheet(APP_QSS)
