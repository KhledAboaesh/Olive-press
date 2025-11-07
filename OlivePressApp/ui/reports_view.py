from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QMessageBox, QInputDialog,
    QComboBox, QProgressBar, QLineEdit, QDateEdit, QFileDialog
)
from PySide6.QtCore import Qt, QDate
from services.table_style import style_table

PRIMARY_COLOR = "#006400"

class ReportsView(QWidget):
    def __init__(self, store):
        super().__init__()
        self.store = store
        self.setLayout(QVBoxLayout())

        # رأس الصفحة
        header = QHBoxLayout()
        title = QLabel("📊 التقارير والديون")
        title.setStyleSheet(f"color:{PRIMARY_COLOR}; font-size:18pt; font-weight:bold;")
        header.addWidget(title)
        header.addStretch()
        self.layout().addLayout(header)

        # ملخص أعلى الصفحة
        self.summary = QLabel("")
        self.summary.setStyleSheet("font-size:14pt; color:#333; margin:8px;")
        self.layout().addWidget(self.summary)

        # أدوات البحث والفلترة
        filter_layout = QHBoxLayout()

        self.filter_box = QComboBox()
        self.filter_box.addItems(["عرض الكل", "غير مدفوع فقط", "مدفوع فقط"])
        filter_layout.addWidget(QLabel("فلترة:"))
        filter_layout.addWidget(self.filter_box)

        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("🔍 بحث باسم الزبون أو رقم الفاتورة...")
        filter_layout.addWidget(self.search_box)

        self.date_from = QDateEdit()
        self.date_from.setCalendarPopup(True)
        self.date_from.setDate(QDate.currentDate().addMonths(-1))  # افتراضي شهر سابق
        filter_layout.addWidget(QLabel("من:"))
        filter_layout.addWidget(self.date_from)

        self.date_to = QDateEdit()
        self.date_to.setCalendarPopup(True)
        self.date_to.setDate(QDate.currentDate())
        filter_layout.addWidget(QLabel("إلى:"))
        filter_layout.addWidget(self.date_to)

        filter_layout.addStretch()
        self.layout().addLayout(filter_layout)

        # جدول الديون
        self.debts_table = QTableWidget(0, 7)
        self.debts_table.setHorizontalHeaderLabels([
            "الزبون", "رقم الفاتورة", "المبلغ المتبقي", "الحالة", "ID", "تاريخ", "نسبة السداد"
        ])
        style_table(self.debts_table)
        self.layout().addWidget(self.debts_table)

        # أزرار التحكم
        btns = QHBoxLayout()
        settle_btn = QPushButton("✅ تسديد كامل")
        settle_btn.clicked.connect(self.settle_selected_debt)
        btns.addWidget(settle_btn)

        partial_btn = QPushButton("💰 تسديد جزئي")
        partial_btn.setProperty("class", "secondary")
        partial_btn.clicked.connect(self.partial_settle_selected_debt)
        btns.addWidget(partial_btn)

        export_btn = QPushButton("📄 تصدير تقرير")
        export_btn.clicked.connect(self.export_report)
        btns.addWidget(export_btn)

        refresh_btn = QPushButton("🔄 تحديث")
        refresh_btn.clicked.connect(self.refresh)
        btns.addWidget(refresh_btn)

        self.layout().addLayout(btns)

        self.refresh()

    def refresh(self):
        debts = self.store.list("debts")
        customers = {c["id"]: c for c in self.store.list("customers")}

        # فلترة بالحالة
        f = self.filter_box.currentText()
        if f == "غير مدفوع فقط":
            debts = [d for d in debts if d["status"] == "غير مدفوع"]
        elif f == "مدفوع فقط":
            debts = [d for d in debts if d["status"] == "مدفوع"]

        # فلترة بالتاريخ
        from_date = self.date_from.date().toString("yyyy-MM-dd")
        to_date = self.date_to.date().toString("yyyy-MM-dd")
        debts = [d for d in debts if from_date <= d.get("date","") <= to_date]

        # بحث نصي
        query = self.search_box.text().strip()
        if query:
            debts = [d for d in debts if query in str(d.get("invoice_id","")) or query in customers.get(d["customer_id"], {"name":""})["name"]]

        # ملخص
        total_debts = sum(float(d.get("remaining_amount", 0)) for d in debts)
        unpaid_count = sum(1 for d in debts if d.get("status") == "غير مدفوع")
        paid_count = sum(1 for d in debts if d.get("status") == "مدفوع")
        max_debt = max((d.get("remaining_amount",0) for d in debts), default=0)
        min_debt = min((d.get("remaining_amount",0) for d in debts), default=0)

        self.summary.setText(
            f"إجمالي الديون: {total_debts:.2f} د.ل | غير مدفوعة: {unpaid_count} | مدفوعة: {paid_count} | أكبر دين: {max_debt:.2f} | أصغر دين: {min_debt:.2f}"
        )

        # عرض النتائج
        self.debts_table.setRowCount(len(debts))
        for r, d in enumerate(debts):
            cname = customers.get(d["customer_id"], {"name": "غير معروف"})["name"]
            self._set_item(r, 0, cname)
            self._set_item(r, 1, str(d["invoice_id"]))
            self._set_item(r, 2, f"{d.get('remaining_amount',0):.2f}", align=Qt.AlignRight)

            status_item = QTableWidgetItem(d["status"])
            status_item.setForeground(Qt.green if d["status"]=="مدفوع" else Qt.red)
            self.debts_table.setItem(r, 3, status_item)

            self._set_item(r, 4, str(d["id"]), align=Qt.AlignCenter)
            self._set_item(r, 5, d.get("date",""))

            # شريط تقدم للسداد
            progress = QProgressBar()
            total = d.get("total", d.get("remaining_amount",0))
            remaining = d.get("remaining_amount",0)
            paid = max(0, total - remaining)
            percent = int((paid / total) * 100) if total > 0 else 0
            progress.setValue(percent)
            self.debts_table.setCellWidget(r, 6, progress)

    def _set_item(self, row, col, value, align=None):
        item = QTableWidgetItem(str(value))
        if align:
            item.setTextAlignment(align | Qt.AlignVCenter)
        self.debts_table.setItem(row, col, item)

    def settle_selected_debt(self):
        row = self.debts_table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "تنبيه", "اختر دين من الجدول أولاً.")
            return
        debt_id = int(self.debts_table.item(row, 4).text())
        self.store.settle_debt(debt_id)
        QMessageBox.information(self, "تم", "تم تسديد الدين بالكامل.")
        self.refresh()

    def partial_settle_selected_debt(self):
        row = self.debts_table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "تنبيه", "اختر دين من الجدول أولاً.")
            return
        debt_id = int(self.debts_table.item(row, 4).text())
        amount, ok = QInputDialog.getDouble(self, "تسديد جزئي", "أدخل المبلغ المدفوع:", 0.0, 0.0, 1e9, 2)
        if not ok or amount <= 0:
            return
        self.store.partial_settle_debt(debt_id, amount)
        QMessageBox.information(self, "تم", f"تم دفع {amount:.2f} د.ل من الدين.")
        self.refresh()

    def export_report(self):
        path, _ = QFileDialog.getSaveFileName(self, "حفظ التقرير", "debts_report.txt", "Text Files (*.txt)")
        if not path:
            return
        debts = self.store.list("debts")
        with open(path, "w", encoding="utf-8") as f:
            f.write("تقرير الديون\n")
            f.write("="*40 + "\n")
            for d in debts:
                f.write(f"فاتورة {d['invoice_id']} | زبون {d['customer_id']} | متبقي {d['remaining_amount']} | حالة {d['status']} | تاريخ {d.get('date','')}\n")
        QMessageBox.information(self, "تم", f"تم حفظ التقرير في:\n{path}")
