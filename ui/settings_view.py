from PySide6.QtWidgets import QWidget, QFormLayout, QLineEdit, QPushButton, QMessageBox, QSpinBox, QDoubleSpinBox

class SettingsView(QWidget):
    def __init__(self, store):
        super().__init__()
        self.store = store
        layout = QFormLayout(self)

        # حقول الإعدادات
        self.name_input = QLineEdit()
        self.price_input = QDoubleSpinBox()
        self.price_input.setRange(0, 1000)
        self.price_input.setSuffix(" دينار/لتر")

        self.package_price_input = QDoubleSpinBox()
        self.package_price_input.setRange(0, 1000)
        self.package_price_input.setSuffix(" دينار/عبوة")

        self.weight_input = QSpinBox()
        self.weight_input.setRange(1, 100)
        self.weight_input.setSuffix(" كجم")

        # إضافة الحقول للنموذج
        layout.addRow("🏷️ اسم المعصرة:", self.name_input)
        layout.addRow("💰 سعر الزيت الافتراضي:", self.price_input)
        layout.addRow("📦 سعر العبوة:", self.package_price_input)
        layout.addRow("⚖️ وزن الوحدة:", self.weight_input)

        # زر الحفظ
        save_btn = QPushButton("💾 حفظ الإعدادات")
        save_btn.clicked.connect(self.save_settings)
        layout.addRow(save_btn)

        # تحميل الإعدادات الحالية
        self.load_settings()

    def load_settings(self):
        settings = self.store.load("settings")
        items = settings.get("items", [])
        if items:
            s = items[0]
            self.name_input.setText(s.get("name", ""))
            self.price_input.setValue(float(s.get("price", 0)))
            self.package_price_input.setValue(float(s.get("package_price", 0)))
            self.weight_input.setValue(int(s.get("weight", 1)))

    def save_settings(self):
        name = self.name_input.text()
        price = float(self.price_input.value())
        package_price = float(self.package_price_input.value())
        weight = int(self.weight_input.value())

        # إعادة كتابة ملف الإعدادات
        self.store.save("settings", {
            "items": [{
                "name": name,
                "price": price,
                "package_price": package_price,
                "weight": weight
            }],
            "last_id": 1
        })

        QMessageBox.information(self, "تم الحفظ", "✅ تم حفظ الإعدادات بنجاح")
