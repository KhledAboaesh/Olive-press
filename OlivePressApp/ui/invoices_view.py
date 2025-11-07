from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTableWidget, QTableWidgetItem, QComboBox, QMessageBox, QFileDialog, QDialog, QDialogButtonBox
from ui.widgets.forms import LabeledForm
from services.logic import compute_invoice_total, UNIT_WEIGHTS
from services.printing import render_invoice_template, save_invoice_pdf
from datetime import datetime

class InvoicesView(QWidget):
    def __init__(self, store):
        super().__init__()
        self.store = store
        self.setLayout(QVBoxLayout())

        top = QHBoxLayout()
        add_btn = QPushButton("إصدار فاتورة")
        add_btn.clicked.connect(self.add_invoice)
        top.addWidget(add_btn)

        export_btn = QPushButton("تصدير الفاتورة المحددة PDF")
        export_btn.clicked.connect(self.export_selected_invoice_pdf)
        top.addWidget(export_btn)

        self.layout().addLayout(top)

        self.table = QTableWidget(0, 9)
        self.table.setHorizontalHeaderLabels([
            "الزبون", "نوع العملية", "كمية الزيت (لتر)", "سعر/لتر",
            "عبوات الزبون", "عبوات المعصرة", "طريقة الدفع", "الإجمالي", "ID"
        ])
        self.layout().addWidget(self.table)

        self.refresh()

    def refresh(self):
        invoices = self.store.list("invoices")
        customers = {c["id"]: c for c in self.store.list("customers")}
        self.table.setRowCount(len(invoices))
        for r, inv in enumerate(invoices):
            cname = customers.get(inv["customer_id"], {"name": "غير معروف"})["name"]
            self.table.setItem(r, 0, QTableWidgetItem(cname))
            self.table.setItem(r, 1, QTableWidgetItem(inv.get("operation_type","")))
            self.table.setItem(r, 2, QTableWidgetItem(str(inv.get("oil_quantity",0.0))))
            self.table.setItem(r, 3, QTableWidgetItem(str(inv.get("price_per_liter",0.0))))
            self.table.setItem(r, 4, QTableWidgetItem(str(inv.get("bottle_count_customer",0))))
            self.table.setItem(r, 5, QTableWidgetItem(str(inv.get("bottle_count_shop",0))))
            self.table.setItem(r, 6, QTableWidgetItem(inv.get("payment_type","")))
            self.table.setItem(r, 7, QTableWidgetItem(str(inv.get("total",0.0))))
            self.table.setItem(r, 8, QTableWidgetItem(str(inv["id"])))

    def add_invoice(self):
        dlg = InvoiceDialog(self.store)
        if dlg.exec():
            self.refresh()

    def export_selected_invoice_pdf(self):
        row = self.table.currentRow()
        if row < 0:
            QMessageBox.information(self, "تصدير", "اختر فاتورة من الجدول أولاً.")
            return
        id_item = self.table.item(row, 8)
        if not id_item:
            QMessageBox.warning(self, "خطأ", "تعذر قراءة رقم الفاتورة.")
            return
        inv_id = int(id_item.text())
        data = self.store.load("invoices")
        inv = next((i for i in data["items"] if i["id"] == inv_id), None)
        if not inv:
            QMessageBox.warning(self, "خطأ", "الفتورة غير موجودة.")
            return
        cust = next((c for c in self.store.list("customers") if c["id"] == inv["customer_id"]), None)

        html = render_invoice_template(inv, cust or {"name": "غير معروف"})
        path, _ = QFileDialog.getSaveFileName(self, "حفظ PDF", f"invoice_{inv_id}.pdf", "PDF Files (*.pdf)")
        if not path:
            return
        try:
            save_invoice_pdf(html, path)
            QMessageBox.information(self, "تم", f"تم حفظ الفاتورة إلى:\n{path}")
        except Exception as e:
            QMessageBox.warning(self, "خطأ", str(e))

class InvoiceDialog(QDialog):
    def __init__(self, store):
        super().__init__()
        self.store = store
        self.setWindowTitle("إنشاء فاتورة")
        form = LabeledForm()

        # الزبون والتسليم
        self.customer = QComboBox()
        self.customers = self.store.list("customers")
        for c in self.customers:
            self.customer.addItem(c["name"], c["id"])
        form.form.addRow("الزبون", self.customer)

        self.delivery = QComboBox()
        for d in self.store.list("deliveries"):
            cname = next((c["name"] for c in self.customers if c["id"] == d["customer_id"]), "غير معروف")
            self.delivery.addItem(f"#{d['id']} - {cname} - {d['total_weight']} كغ", d["id"])
        form.form.addRow("استلام مرتبط", self.delivery)

        # نوع العملية
        self.operation = form.add_combo("operation_type", "نوع العملية", ["عصر", "تبديل", "بيع"])

        # بيانات الزيت
        self.oil_qty = form.add_double("oil_quantity", "كمية الزيت (لتر)", 0.0, 1e6, 2)
        self.price_per_liter = form.add_double("price_per_liter", "سعر/لتر", 0.0, 1e6, 2)

        # العبوات
        self.bottle_count_customer = form.add_int("bottle_count_customer", "عبوات الزبون", 0, 1e6)
        self.bottle_count_shop = form.add_int("bottle_count_shop", "عبوات المعصرة", 0, 1e6)
        self.bottle_price = form.add_double("bottle_price", "سعر العبوة", 0.0, 1e6, 2)

        # الدفع
        self.payment = form.add_combo("payment_type", "طريقة الدفع", ["نقدي", "دين", "تبديل", "إلكتروني"])

        # حقول التبديل
        self.swap_olive = form.add_double("swap_olive", "كمية الزيتون (كغ) عند التبديل", 0.0, 1e9, 2)
        self.swap_oil = form.add_double("swap_oil", "كمية الزيت المستلم (لتر)", 0.0, 1e9, 2)
        self.swap_diff_l = form.add_double("swap_diff_l", "فرق اللترات", 0.0, 1e9, 2)
        self.swap_diff_price = form.add_double("swap_diff_price", "فرق السعر (دينار)", 0.0, 1e9, 2)

        buttons = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.save)
        buttons.rejected.connect(self.reject)

        lay = QVBoxLayout()
        lay.addWidget(form)
        lay.addWidget(buttons)
        self.setLayout(lay)

        # إعدادات افتراضية
        settings = self.store.load("settings").get("items", [{}])[0]
        self.price_per_liter.setValue(float(settings.get("price_per_liter_default", 15.0)))
        self.bottle_price.setValue(float(settings.get("bottle_price_default", 5.0)))

    def save(self):
        if self.customer.currentIndex() < 0:
            QMessageBox.warning(self, "تنبيه", "اختر الزبون.")
            return
        cid = self.customer.currentData()
        delv_id = self.delivery.currentData() if self.delivery.currentIndex() >= 0 else None
        op = self.operation.currentText()

        oil_q = self.oil_qty.value()
        ppl = self.price_per_liter.value()
        bc_cust = self.bottle_count_customer.value()
        bc_shop = self.bottle_count_shop.value()
        bprice = self.bottle_price.value()
        pay = self.payment.currentText()

        total = compute_invoice_total(oil_q, ppl, bc_shop, bprice)

        inv = {
            "customer_id": cid,
            "delivery_id": delv_id,
            "operation_type": op,
            "oil_quantity": oil_q,
            "price_per_liter": ppl,
            "bottle_count_customer": bc_cust,
            "bottle_count_shop": bc_shop,
            "bottle_price": bprice,
            "payment_type": pay,
            "total": total,
            "date": datetime.now().strftime("%Y-%m-%d")
        }

        if op == "تبديل":
            inv["swap"] = {
                "olive_weight": self.swap_olive.value(),
                "oil_received": self.swap_oil.value(),
                "difference_liters": self.swap_diff_l.value(),
                "difference_price": self.swap_diff_price.value()
            }

        inserted = self.store.insert("invoices", inv)

        # إنشاء دين تلقائي عند الدفع "دين"
        if pay == "دين":
            debt = {
                "customer_id": cid,
                "invoice_id": inserted["id"],
                "remaining_amount": total,
                "status": "غير مدفوع"
            }
            self.store.insert("debts", debt)

        self.accept()
