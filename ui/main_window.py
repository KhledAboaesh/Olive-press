from PySide6.QtWidgets import QMainWindow, QTabWidget, QMessageBox, QStatusBar, QPushButton
from PySide6.QtGui import QIcon
import os, shutil
from datetime import datetime
from ui.customers_view import CustomersView
from ui.deliveries_view import DeliveriesView
from ui.invoices_view import InvoicesView
from ui.reports_view import ReportsView
from ui.settings_view import SettingsView

class MainWindow(QMainWindow):
    def __init__(self, store):
        super().__init__()
        self.store = store
        self.setWindowTitle("إدارة معصرة الزيتون")
        self.resize(1200, 800)

        # أيقونة النافذة
        icon_path = os.path.join(os.path.dirname(__file__), "..", "assets", "logo.png")
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))

        # التبويبات
        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)

        # إضافة الواجهات
        self.customers_view = CustomersView(store)
        self.deliveries_view = DeliveriesView(store)
        self.invoices_view = InvoicesView(store)
        self.reports_view = ReportsView(store)
        self.settings_view = SettingsView(store)

        self.tabs.addTab(self.customers_view, "👥 الزبائن")
        self.tabs.addTab(self.deliveries_view, "📦 الاستلام")
        self.tabs.addTab(self.invoices_view, "🧾 الفواتير")
        self.tabs.addTab(self.reports_view, "📊 التقارير والديون")
        self.tabs.addTab(self.settings_view, "⚙️ الإعدادات")

        # شريط المهام
        self.status = QStatusBar()
        self.setStatusBar(self.status)

        # أزرار في شريط المهام
        self._add_status_buttons()
        self.update_status()

    def _add_status_buttons(self):
        # زر تحديث
        btn_refresh = QPushButton("🔄 تحديث")
        btn_refresh.clicked.connect(self.refresh_all)
        self.status.addPermanentWidget(btn_refresh)

        # زر إعادة ضبط
        btn_reset = QPushButton("🗑️ إعادة الضبط")
        btn_reset.clicked.connect(self.reset_data)
        btn_reset.setStyleSheet("background-color:#ff0000;")  # لون مميز للتحذير
        self.status.addPermanentWidget(btn_reset)

        # زر نسخ احتياطي
        btn_backup = QPushButton("💾 نسخ احتياطي")
        btn_backup.clicked.connect(self.backup_data)
        self.status.addPermanentWidget(btn_backup)

        # زر خروج
        btn_exit = QPushButton("🚪 خروج")
        btn_exit.clicked.connect(self.close)
        btn_exit.setStyleSheet("background-color:#ff0000;")  # لون مميز للخروج
        self.status.addPermanentWidget(btn_exit)

        # أزرار التنقل
        btn_customer = QPushButton("👤 زبون جديد")
        btn_customer.clicked.connect(lambda: self.tabs.setCurrentWidget(self.customers_view))
        self.status.addPermanentWidget(btn_customer)

        btn_delivery = QPushButton("📦 استلام جديد")
        btn_delivery.clicked.connect(lambda: self.tabs.setCurrentWidget(self.deliveries_view))
        self.status.addPermanentWidget(btn_delivery)

        btn_invoice = QPushButton("🧾 فاتورة")
        btn_invoice.clicked.connect(lambda: self.tabs.setCurrentWidget(self.invoices_view))
        self.status.addPermanentWidget(btn_invoice)

        btn_reports = QPushButton("📊 تقارير")
        btn_reports.clicked.connect(lambda: self.tabs.setCurrentWidget(self.reports_view))
        self.status.addPermanentWidget(btn_reports)

        btn_settings = QPushButton("⚙️ إعدادات")
        btn_settings.clicked.connect(lambda: self.tabs.setCurrentWidget(self.settings_view))
        self.status.addPermanentWidget(btn_settings)

    def reset_data(self):
        reply = QMessageBox.question(
            self,
            "إعادة ضبط البيانات",
            "هل تريد تفريغ جميع البيانات؟\nنعم: تفريغ كامل\nلا: تعبئة بيانات تجريبية",
            QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel
        )
        if reply == QMessageBox.Cancel:
            return
        fill_demo = (reply == QMessageBox.No)
        self.store.reset_all(fill_demo=fill_demo)
        QMessageBox.information(self, "تمت العملية", "تمت إعادة ضبط جميع البيانات.")
        self.refresh_all()

    def refresh_all(self):
        self.customers_view.refresh()
        self.deliveries_view.refresh()
        self.invoices_view.refresh()
        self.reports_view.refresh()
        self.update_status()

    def update_status(self):
        customers_count = len(self.store.list("customers"))
        invoices_count = len(self.store.list("invoices"))
        debts_count = sum(1 for d in self.store.list("debts") if d["status"] != "مدفوع")
        self.status.showMessage(
            f"👥 الزبائن: {customers_count} | 🧾 الفواتير: {invoices_count} | 💰 الديون غير المدفوعة: {debts_count}"
        )

    def backup_data(self):
        """نسخ مجلد data إلى مجلد backups مع اسم حسب التاريخ"""
        src = "data"
        dst = "backups"
        os.makedirs(dst, exist_ok=True)
        backup_name = datetime.now().strftime("backup_%Y%m%d_%H%M%S")
        dst_path = os.path.join(dst, backup_name)
        shutil.copytree(src, dst_path)
        QMessageBox.information(self, "نسخ احتياطي", f"✅ تم إنشاء نسخة احتياطية في {dst_path}")
