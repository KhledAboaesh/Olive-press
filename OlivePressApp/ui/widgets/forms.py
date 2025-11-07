from PySide6.QtWidgets import QWidget, QFormLayout, QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox

class LabeledForm(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.form = QFormLayout(self)
        self.fields = {}

    def add_line(self, key, label, placeholder=""):
        w = QLineEdit()
        w.setPlaceholderText(placeholder)
        self.form.addRow(label, w)
        self.fields[key] = w
        return w

    def add_combo(self, key, label, items):
        w = QComboBox()
        w.addItems(items)
        self.form.addRow(label, w)
        self.fields[key] = w
        return w

    def add_int(self, key, label, minimum=0, maximum=10**9):
        w = QSpinBox()
        w.setRange(minimum, maximum)
        self.form.addRow(label, w)
        self.fields[key] = w
        return w

    def add_double(self, key, label, minimum=0.0, maximum=10**9, decimals=2):
        w = QDoubleSpinBox()
        w.setDecimals(decimals)
        w.setRange(minimum, maximum)
        self.form.addRow(label, w)
        self.fields[key] = w
        return w

    def values(self):
        out = {}
        for k, w in self.fields.items():
            if hasattr(w, "text") and not isinstance(w, (QSpinBox, QDoubleSpinBox)):
                out[k] = w.text()
            elif hasattr(w, "value"):
                out[k] = w.value()
            elif hasattr(w, "currentText"):
                out[k] = w.currentText()
        return out
