import sys
import os
from PySide6.QtWidgets import QApplication
from ui.main_window import MainWindow
from services.store import DataManager

def ensure_data_files(store):
    for name in ["customers", "deliveries", "invoices", "debts", "adjustments", "settings"]:
        if not os.path.exists(store.data_files[name]):
            if name != "settings":
                store.save(name, {"seq": 0, "items": []})
            else:
                store.save(name, {"prices": {"oil_per_liter": 15.0, "bottle": 5.0}, "unit_weights": {"دلو": 14.0, "صندوق": 14.5, "كيس": None, "كيلو": 1.0}, "options": {"payment_types": ["نقدي", "دين", "إلكتروني"]}})

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setApplicationName("إدارة معصرة الزيتون")
    os.makedirs("data", exist_ok=True)
    os.makedirs("assets", exist_ok=True)
    os.makedirs("backups", exist_ok=True)
    store = DataManager("data")
    ensure_data_files(store)
    win = MainWindow(store)
    win.show()
    sys.exit(app.exec())
