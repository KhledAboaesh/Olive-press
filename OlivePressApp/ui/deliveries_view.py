from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QLineEdit, QDateEdit, QMessageBox
)
from PySide6.QtCore import Qt, QDate
from datetime import datetime
from services.table_style import style_table

class DeliveriesView(QWidget):
    def __init__(self, store):
        super().__init__()
        self.store = store
        self.setLayout(QVBoxLayout())

        # رأس الصفحة
        header = QHBoxLayout()
        title = QLabel("📦 الاستلام")
        title.setStyleSheet("color:#006400; font-size:18pt; font-weight:bold;")
        header.addWidget(title)
        header.addStretch()
        self.layout().addLayout(header)

        # ملخص
        self.summary = QLabel("")
        self.summary.setStyleSheet("font-size:14pt; margin:8px;")
        self.layout().addWidget(self.summary)

        # أدوات البحث والفلترة
        filter_layout = QHBoxLayout()
        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("🔍 بحث باسم الزبون أو رقم الاستلام...")
        filter_layout.addWidget(self.search_box)

        self.date_from = QDateEdit()
        self.date_from.setCalendarPopup(True)
        self.date_from.setDate(QDate.currentDate().addMonths(-1))
        filter_layout.addWidget(QLabel("من:"))
        filter_layout.addWidget(self.date_from)

        self.date_to = QDateEdit()
        self.date_to.setCalendarPopup(True)
        self.date_to.setDate(QDate.currentDate())
        filter_layout.addWidget(QLabel("إلى:"))
        filter_layout.addWidget(self.date_to)

        refresh_btn = QPushButton("🔄 تحديث")
        refresh_btn.clicked.connect(self.refresh)
        filter_layout.addWidget(refresh_btn)

        self.layout().addLayout(filter_layout)

        # جدول الاستلامات
        self.table = QTableWidget(0, 6)
        self.table.setHorizontalHeaderLabels([
            "الزبون", "الوزن (كجم)", "المبلغ المدفوع", "التاريخ", "ID", "فاتورة مرتبطة"
        ])
        style_table(self.table)
        self.layout().addWidget(self.table)

        self.refresh()

    def refresh(self):
        deliveries = self.store.list("deliveries")
        customers = {c["id"]: c for c in self.store.list("customers")}
        invoices = {i["delivery_id"]: i for i in self.store.list("invoices") if i.get("delivery_id")}

        # فلترة بالتاريخ
        from_date = self.date_from.date().toString("yyyy-MM-dd")
        to_date = self.date_to.date().toString("yyyy-MM-dd")
        deliveries = [d for d in deliveries if from_date <= d.get("date","") <= to_date]

        # بحث نصي
        query = self.search_box.text().strip()
        if query:
            deliveries = [d for d in deliveries if query in str(d.get("id","")) or query in customers.get(d["customer_id"], {"name":""})["name"]]

        # ملخص
        total_weight = sum(d.get("total_weight",0) for d in deliveries)
        total_paid = sum(d.get("paid_amount",0) for d in deliveries)
        self.summary.setText(f"إجمالي الوزن: {total_weight:.2f} كجم | إجمالي المدفوع: {total_paid:.2f} د.ل | عدد الاستلامات: {len(deliveries)}")

        # عرض النتائج
        self.table.setRowCount(len(deliveries))
        for r, d in enumerate(deliveries):
            cname = customers.get(d["customer_id"], {"name":"غير معروف"})["name"]
            self._set_item(r, 0, cname)
            self._set_item(r, 1, f"{d.get('total_weight',0):.2f}")
            self._set_item(r, 2, f"{d.get('paid_amount',0):.2f}")
            self._set_item(r, 3, d.get("date",""))
            self._set_item(r, 4, str(d["id"]))

            inv = invoices.get(d["id"])
            self._set_item(r, 5, f"فاتورة {inv['id']}" if inv else "—")

    def _set_item(self, row, col, value):
        item = QTableWidgetItem(str(value))
        item.setTextAlignment(Qt.AlignCenter)
        self.table.setItem(row, col, item)

    # دالة لإضافة استلام جديد مع تحديث الفاتورة والدين
    def add_delivery(self, customer_id, weight, paid_amount):
        delivery = {
            "customer_id": customer_id,
            "total_weight": weight,
            "date": datetime.now().strftime("%Y-%m-%d"),
            "paid_amount": paid_amount
        }
        inserted = self.store.insert("deliveries", delivery)

        # حساب إجمالي الفاتورة (مثال: 1 لتر زيت لكل 5 كجم زيتون × سعر افتراضي)
        settings = self.store.list("settings")[0]
        price_per_liter = settings.get("price_per_liter_default", 15.0)
        oil_qty = weight / 5.0
        total = oil_qty * price_per_liter

        invoice = {
            "customer_id": customer_id,
            "delivery_id": inserted["id"],
            "oil_quantity": oil_qty,
            "price_per_liter": price_per_liter,
            "total": total,
            "paid_amount": paid_amount,
            "remaining_amount": max(0, total - paid_amount),
            "status": "مدفوع" if paid_amount >= total else "غير مدفوع",
            "date": delivery["date"]
        }
        inv = self.store.insert("invoices", invoice)

        # إنشاء دين إذا هناك فرق
        if invoice["remaining_amount"] > 0:
            debt = {
                "customer_id": customer_id,
                "invoice_id": inv["id"],
                "remaining_amount": invoice["remaining_amount"],
                "status": "غير مدفوع",
                "date": invoice["date"]
            }
            self.store.insert("debts", debt)

        QMessageBox.information(self, "تم", "تم تسجيل الاستلام وإنشاء الفاتورة تلقائياً.")
        self.refresh()
