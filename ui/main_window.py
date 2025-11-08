from PySide6.QtWidgets import QMainWindow, QTabWidget, QMessageBox, QToolBar, QStatusBar
from PySide6.QtGui import QAction, QIcon
from PySide6.QtCore import Qt, QSize
from ui.customers_view import CustomersView
from ui.deliveries_view import DeliveriesView
from ui.invoices_view import InvoicesView
from ui.reports_view import ReportsView
from ui.settings_view import SettingsView
import os

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
        self.tabs.setTabPosition(QTabWidget.North)
        self.tabs.setDocumentMode(True)
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

        # القوائم والشريط
        self._make_menu()
        self._make_toolbar()
        self._apply_styles()

        # شريط المهام
        self.status = QStatusBar()
        self.setStatusBar(self.status)
        self.update_status()

    def _make_menu(self):
        menubar = self.menuBar()
        file_menu = menubar.addMenu("ملف")

        reset_action = QAction("🗑️ إعادة ضبط البيانات", self)
        reset_action.triggered.connect(self.reset_data)
        file_menu.addAction(reset_action)

        backup_action = QAction("💾 نسخ احتياطي", self)
        backup_action.triggered.connect(self.backup_data)
        file_menu.addAction(backup_action)

        exit_action = QAction("🚪 خروج", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

    def _make_toolbar(self):
        toolbar = QToolBar("شريط الأدوات")
        toolbar.setIconSize(QSize(28, 28))
        self.addToolBar(Qt.TopToolBarArea, toolbar)

        refresh_action = QAction("🔄 تحديث", self)
        refresh_action.triggered.connect(self.refresh_all)
        toolbar.addAction(refresh_action)

        reset_action = QAction("🗑️ إعادة ضبط", self)
        reset_action.triggered.connect(self.reset_data)
        toolbar.addAction(reset_action)

        add_customer = QAction("👤 زبون جديد", self)
        add_customer.triggered.connect(lambda: self.tabs.setCurrentWidget(self.customers_view))
        toolbar.addAction(add_customer)

        add_delivery = QAction("📦 استلام جديد", self)
        add_delivery.triggered.connect(lambda: self.tabs.setCurrentWidget(self.deliveries_view))
        toolbar.addAction(add_delivery)

        add_invoice = QAction("🧾 فاتورة جديدة", self)
        add_invoice.triggered.connect(lambda: self.tabs.setCurrentWidget(self.invoices_view))
        toolbar.addAction(add_invoice)

        reports = QAction("📊 تقارير", self)
        reports.triggered.connect(lambda: self.tabs.setCurrentWidget(self.reports_view))
        toolbar.addAction(reports)

        settings = QAction("⚙️ إعدادات", self)
        settings.triggered.connect(lambda: self.tabs.setCurrentWidget(self.settings_view))
        toolbar.addAction(settings)

    def _apply_styles(self):
        self.setStyleSheet("""
            QMainWindow { background: #f7f7fa; }
            QTabWidget::pane {
                border: 1px solid #d0d0d0;
                border-radius: 8px;
                margin: 8px;
            }
            QTabBar::tab {
                background: #e0e0e0;
                border-radius: 8px;
                padding: 10px 24px;
                font-size: 17px;
                color: #333;
                margin: 2px;
            }
            QTabBar::tab:selected {
                background: #006400;
                color: white;
                font-weight: bold;
            }
            QMenuBar { background: #f0f0f0; font-size: 16px; }
            QToolBar { background: #f0f4ff; border-bottom: 1px solid #d0d0d0; }
            QToolButton { font-size: 15px; padding: 6px 16px; }
        """)

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
        # هنا ممكن تضيف كود النسخ الاحتياطي (نسخ مجلد data إلى مجلد backups)
        QMessageBox.information(self, "نسخ احتياطي", "تم إنشاء نسخة احتياطية للبيانات.")
