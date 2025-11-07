from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTableWidget, QTableWidgetItem, QComboBox, QMessageBox, QDialog, QDialogButtonBox
from ui.widgets.forms import LabeledForm
from services.logic import compute_total_weight
from datetime import datetime

class DeliveriesView(QWidget):
    def __init__(self, store):
        super().__init__()
        self.store = store
        self.setLayout(QVBoxLayout())

        top = QHBoxLayout()
        add_btn = QPushButton("إضافة استلام")
        add_btn.clicked.connect(self.add_delivery)
        top.addWidget(add_btn)
        self.layout().addLayout(top)

        self.table = QTableWidget(0, 6)
        self.table.setHorizontalHeaderLabels(["الزبون", "نوع التعبئة", "العدد", "الوزن الإجمالي", "التاريخ", "ID"])
        self.layout().addWidget(self.table)

        self.refresh()

    def refresh(self):
        deliveries = self.store.list("deliveries")
        customers = {c["id"]: c for c in self.store.list("customers")}
        self.table.setRowCount(len(deliveries))
        for r, it in enumerate(deliveries):
            cname = customers.get(it["customer_id"], {"name": "غير معروف"})["name"]
            self.table.setItem(r, 0, QTableWidgetItem(cname))
            self.table.setItem(r, 1, QTableWidgetItem(it["package_type"]))
            self.table.setItem(r, 2, QTableWidgetItem(str(it["quantity"])))
            self.table.setItem(r, 3, QTableWidgetItem(str(it["total_weight"])))
            self.table.setItem(r, 4, QTableWidgetItem(it["date"]))
            self.table.setItem(r, 5, QTableWidgetItem(str(it["id"])))

    def add_delivery(self):
        dlg = DeliveryDialog(self.store)
        if dlg.exec():
            self.refresh()

class DeliveryDialog(QDialog):
    def __init__(self, store):
        super().__init__()
        self.store = store
        self.setWindowTitle("استلام زيتون")

        form = LabeledForm()
        self.customer = QComboBox()
        self.customers = self.store.list("customers")
        for c in self.customers:
            self.customer.addItem(c["name"], c["id"])
        form.form.addRow("الزبون", self.customer)

        self.package = form.add_combo("package_type", "نوع التعبئة", ["كيس", "دلو", "صندوق", "كيلو"])
        self.quantity = form.add_int("quantity", "العدد/الكمية")
        self.manual_weight = form.add_double("manual_weight", "وزن يدوي (للأكياس فقط)", 0.0, 1e9, 2)

        buttons = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.save)
        buttons.rejected.connect(self.reject)

        lay = QVBoxLayout()
        lay.addWidget(form)
        lay.addWidget(buttons)
        self.setLayout(lay)

    def save(self):
        if self.customer.currentIndex() < 0:
            QMessageBox.warning(self, "تنبيه", "يرجى اختيار زبون.")
            return
        cid = self.customer.currentData()
        ptype = self.package.currentText()
        qty = self.quantity.value()
        mw = self.manual_weight.value() or None

        try:
            total_w = compute_total_weight(ptype, qty, manual_weight=mw)
        except Exception as e:
            QMessageBox.warning(self, "خطأ", str(e))
            return

        item = {
            "customer_id": cid,
            "package_type": ptype,
            "quantity": qty,
            "total_weight": total_w,
            "date": datetime.now().strftime("%Y-%m-%d")
        }
        self.store.insert("deliveries", item)
        self.accept()
