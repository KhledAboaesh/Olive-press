# services/table_style.py
from PySide6.QtWidgets import QTableWidget
from PySide6.QtCore import Qt

def style_table(tbl: QTableWidget):
    """تطبيق تنسيق موحّد على الجداول"""
    tbl.setAlternatingRowColors(True)
    tbl.setSelectionBehavior(QTableWidget.SelectRows)
    tbl.setSelectionMode(QTableWidget.SingleSelection)
    tbl.verticalHeader().setVisible(False)
    tbl.horizontalHeader().setStretchLastSection(True)
    tbl.horizontalHeader().setDefaultAlignment(Qt.AlignRight | Qt.AlignVCenter)
    tbl.setSortingEnabled(True)
    tbl.setWordWrap(False)
    tbl.setShowGrid(True)
