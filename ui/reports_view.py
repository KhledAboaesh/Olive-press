from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTableWidget, QTableWidgetItem, QComboBox
from datetime import datetime

class ReportsView(QWidget):
    def __init__(self, store):
        super().__init__()
        self.store = store
        self.setLayout(QVBoxLayout())

        # فلاتر التاريخ المبسطة: الشهر والسنة
        filters = QHBoxLayout()
        self.year = QComboBox()
        self.month = QComboBox()
        now = datetime.now()
        years = list({datetime.now().year, now.year - 1, now.year - 2})
        for y in sorted(years, reverse=True):
            self.year.addItem(str(y), y)
        for m in range(1, 13):
            self.month.addItem(str(m), m)
        apply_btn = QPushButton("تطبيق")
        apply_btn.clicked.connect(self.refresh)

        filters.addWidget(QLabel("سنة"))
        filters.addWidget(self.year)
        filters.addWidget(QLabel("شهر"))
        filters.addWidget(self.month)
        filters.addWidget(apply_btn)
        self.layout().addLayout(filters)

        self.summary = QLabel("")
        self.layout().addWidget(self.summary)

        self.debts_table = QTableWidget(0, 4)
        self.debts_table.setHorizontalHeaderLabels(["الزبون", "رقم الفاتورة", "المبلغ المتبقي", "الحالة"])
        self.layout().addWidget(self.debts_table)

        self.refresh()

    def refresh(self):
        y = self.year.currentData()
        m = self.month.currentData()
        invoices = self.store.list("invoices")
        deliveries = self.store.list("deliveries")

        # تصفية حسب الشهر والسنة
        inv_f = [i for i in invoices if self._match_month(i.get("date",""), y, m)]
        delv_f = [d for d in deliveries if self._match_month(d.get("date",""), y, m)]

        total_oil = sum(i.get("oil_quantity", 0.0) for i in inv_f)
        total_money = sum(i.get("total", 0.0) for i in inv_f)
        total_olives = sum(d.get("total_weight", 0.0) for d in delv_f)

        self.summary.setText(f"إجمالي الزيتون: {total_olives} كغ | إجمالي الزيت: {total_oil} لتر | إجمالي المبالغ: {total_money} د.ل")

        # ديون
        debts = self.store.list("debts")
        customers = {c["id"]: c for c in self.store.list("customers")}
        self.debts_table.setRowCount(len(debts))
        for r, d in enumerate(debts):
            cname = customers.get(d["customer_id"], {"name": "غير معروف"})["name"]
            self.debts_table.setItem(r, 0, QTableWidgetItem(cname))
            self.debts_table.setItem(r, 1, QTableWidgetItem(str(d["invoice_id"])))
            self.debts_table.setItem(r, 2, QTableWidgetItem(str(d["remaining_amount"])))
            self.debts_table.setItem(r, 3, QTableWidgetItem(d["status"]))

    def _match_month(self, date_str, year, month):
        try:
            dt = datetime.strptime(date_str, "%Y-%m-%d")
            return dt.year == year and dt.month == month
        except:
            return False
