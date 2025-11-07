import sys, os
from PySide6.QtWidgets import QApplication
from ui.main_window import MainWindow
from services.store import JsonStore
from services.theme import apply_app_style

def ensure_data_files(store: JsonStore):
    # إنشاء الملفات الأساسية
    for name in ["customers", "deliveries", "invoices", "debts", "adjustments", "settings"]:
        store._init(name)
    # إعدادات افتراضية
    settings = store.load("settings")
    if not settings.get("items"):
        settings["items"] = [{
            "brand_name": "معصرة الزيتون",
            "price_per_liter_default": 15.0,
            "bottle_price_default": 5.0,
            "unit_weights": {"دلو": 14.0, "صندوق": 14.5, "كيس": None, "كيلو": 1.0}
        }]
        store.save("settings", settings)

def main():
    app = QApplication(sys.argv)
    app.setApplicationName("إدارة معصرة الزيتون")
    apply_app_style(app)

    # إنشاء مجلدات أساسية
    os.makedirs("data", exist_ok=True)
    os.makedirs("assets", exist_ok=True)
    os.makedirs("backups", exist_ok=True)

    store = JsonStore("data")
    ensure_data_files(store)

    win = MainWindow(store)
    win.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
