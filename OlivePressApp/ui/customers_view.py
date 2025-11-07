from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTableWidget, QTableWidgetItem, QLineEdit, QMessageBox, QDialog, QDialogButtonBox
from ui.widgets.forms import LabeledForm

class CustomersView(QWidget):
    def __init__(self, store):
        super().__init__()
        self.store = store
        self.setLayout(QVBoxLayout())
        top = QHBoxLayout()

        self.search = QLineEdit()
        self.search.setPlaceholderText("ابحث بالاسم أو الهاتف...")
        self.search.textChanged.connect(self.refresh)
        top.addWidget(self.search)

        add_btn = QPushButton("إضافة زبون")
        add_btn.clicked.connect(self.add_customer)
        top.addWidget(add_btn)

        self.layout().addLayout(top)

        self.table = QTableWidget(0, 4)
        self.table.setHorizontalHeaderLabels(["الاسم", "الهاتف", "ملاحظات", "ID"])
        self.table.cellDoubleClicked.connect(self.edit_customer)
        self.layout().addWidget(self.table)

        self.refresh()

    def refresh(self):
        term = self.search.text().strip()
        items = self.store.list("customers", where=(lambda i: (term in i["name"] or term in i.get("phone","")))) if term else self.store.list("customers")
        self.table.setRowCount(len(items))
        for r, it in enumerate(items):
            self.table.setItem(r, 0, QTableWidgetItem(it["name"]))
            self.table.setItem(r, 1, QTableWidgetItem(it.get("phone","")))
            self.table.setItem(r, 2, QTableWidgetItem(it.get("notes","")))
            self.table.setItem(r, 3, QTableWidgetItem(str(it["id"])))

    def add_customer(self):
        dlg = CustomerDialog(self.store)
        if dlg.exec():
            self.refresh()

    def edit_customer(self, row, col):
        id_item = self.table.item(row, 3)
        if not id_item: return
        cid = int(id_item.text())
        dlg = CustomerDialog(self.store, cid)
        if dlg.exec():
            self.refresh()

class CustomerDialog(QDialog):
    def __init__(self, store, customer_id=None):
        super().__init__()
        self.store = store
        self.customer_id = customer_id
        self.setWindowTitle("بيانات الزبون")
        form = LabeledForm()
        self.name = form.add_line("name", "الاسم")
        self.phone = form.add_line("phone", "الهاتف")
        self.notes = form.add_line("notes", "ملاحظات")
        buttons = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.save)
        buttons.rejected.connect(self.reject)

        lay = QVBoxLayout()
        lay.addWidget(form)
        lay.addWidget(buttons)
        self.setLayout(lay)

        if customer_id:
            data = self.store.load("customers")
            for it in data["items"]:
                if it["id"] == customer_id:
                    self.name.setText(it["name"])
                    self.phone.setText(it.get("phone",""))
                    self.notes.setText(it.get("notes",""))
                    break

    def save(self):
        name = self.name.text().strip()
        if not name:
            QMessageBox.warning(self, "تنبيه", "يرجى إدخال الاسم.")
            return
        payload = {"name": name, "phone": self.phone.text().strip(), "notes": self.notes.text().strip()}
        if self.customer_id:
            self.store.update("customers", self.customer_id, payload)
        else:
            self.store.insert("customers", payload)
        self.accept()
