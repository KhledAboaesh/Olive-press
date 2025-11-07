from PySide6.QtWidgets import QMainWindow, QTabWidget, QMessageBox, QToolBar
from PySide6.QtGui import QAction, QIcon
from PySide6.QtCore import Qt, QSize
from ui.customers_view import CustomersView
from ui.deliveries_view import DeliveriesView
from ui.invoices_view import InvoicesView
from ui.reports_view import ReportsView
import os

class MainWindow(QMainWindow):
    def __init__(self, store):
        super().__init__()
        self.store = store
        self.setWindowTitle("إدارة معصرة الزيتون")
        self.resize(1200, 800)

        # إضافة أيقونة للنافذة إذا وجدت
        icon_path = os.path.join(os.path.dirname(__file__), "..", "assets", "logo.png")
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))

        # التبويبات
        self.tabs = QTabWidget()
        self.tabs.setTabPosition(QTabWidget.North)
        self.tabs.setDocumentMode(True)  # مظهر حديث للتبويبات
        self.setCentralWidget(self.tabs)

        # إضافة الواجهات
        self.customers_view = CustomersView(store)
        self.deliveries_view = DeliveriesView(store)
        self.invoices_view = InvoicesView(store)
        self.reports_view = ReportsView(store)

        self.tabs.addTab(self.customers_view, "👥 الزبائن")
        self.tabs.addTab(self.deliveries_view, "📦 الاستلام")
        self.tabs.addTab(self.invoices_view, "🧾 الفواتير")
        self.tabs.addTab(self.reports_view, "📊 التقارير والديون")

        # إنشاء القوائم والشريط
        self._make_menu()
        self._make_toolbar()
        self._apply_styles()

    def _make_menu(self):
        menubar = self.menuBar()
        file_menu = menubar.addMenu("ملف")

        reset_action = QAction(QIcon(), "إعادة ضبط البيانات", self)
        reset_action.triggered.connect(self.reset_data)
        file_menu.addAction(reset_action)

    def _make_toolbar(self):
        toolbar = QToolBar("شريط الأدوات")
        toolbar.setIconSize(QSize(28, 28))
        self.addToolBar(Qt.TopToolBarArea, toolbar)

        # زر تحديث
        refresh_action = QAction(QIcon(), "🔄 تحديث", self)
        refresh_action.triggered.connect(self.refresh_all)
        toolbar.addAction(refresh_action)

        # زر إعادة ضبط
        reset_action = QAction(QIcon(), "🗑️ إعادة ضبط", self)
        reset_action.triggered.connect(self.reset_data)
        toolbar.addAction(reset_action)

    def _apply_styles(self):
        # QSS حديث للألوان والخطوط
        self.setStyleSheet("""
            QMainWindow {
                background: #f7f7fa;
            }
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
            QMenuBar {
                background: #f0f0f0;
                font-size: 16px;
            }
            QToolBar {
                background: #f0f4ff;
                border-bottom: 1px solid #d0d0d0;
            }
            QToolButton {
                font-size: 15px;
                padding: 6px 16px;
            }
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
