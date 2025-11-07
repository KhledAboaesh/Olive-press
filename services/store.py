import json
import os

class DataManager:
    def __init__(self, data_dir):
        self.data_dir = data_dir
        self.data_files = {
            "customers": os.path.join(data_dir, "customers.json"),
            "deliveries": os.path.join(data_dir, "deliveries.json"),
            "invoices": os.path.join(data_dir, "invoices.json"),
            "debts": os.path.join(data_dir, "debts.json"),
            "adjustments": os.path.join(data_dir, "adjustments.json"),
            "settings": os.path.join(data_dir, "settings.json")
        }

    def load(self, name):
        with open(self.data_files[name], "r", encoding="utf-8") as f:
            return json.load(f)

    def save(self, name, data):
        with open(self.data_files[name], "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

    def list(self, name, where=None):
        """
        إرجاع قائمة العناصر من ملف البيانات المحدد، مع دعم فلترة اختيارية.
        where: دالة فلترة (lambda) أو None
        """
        data = self.load(name)
        items = data.get("items", [])
        if where:
            items = [item for item in items if where(item)]
        return items

    def reset_all(self, fill_demo=False):
        demo = {
            "customers": {
                "seq": 2,
                "items": [
                    {"id": 1, "name": "أحمد علي", "phone": "0912345678", "notes": "زبون دائم"},
                    {"id": 2, "name": "سالم محمد", "phone": "0923456789", "notes": "زبون قديم"}
                ]
            },
            "deliveries": {
                "seq": 2,
                "items": [
                    {"id": 1, "customer_id": 1, "package_type": "دلو", "quantity": 3, "total_weight": 42.0, "date": "2025-11-07"},
                    {"id": 2, "customer_id": 2, "package_type": "كيس", "quantity": 2, "total_weight": 30.0, "date": "2025-11-07"}
                ]
            },
            "invoices": {
                "seq": 2,
                "items": [
                    {"id": 1, "customer_id": 1, "delivery_id": 1, "operation_type": "عصر", "oil_quantity": 20.0, "price_per_liter": 15.0, "bottle_count_customer": 2, "bottle_count_shop": 1, "bottle_price": 5.0, "payment_type": "نقدي", "total": 310.0, "date": "2025-11-07", "swap": None},
                    {"id": 2, "customer_id": 2, "delivery_id": 2, "operation_type": "بديل", "oil_quantity": 16.0, "price_per_liter": 15.0, "bottle_count_customer": 1, "bottle_count_shop": 2, "bottle_price": 5.0, "payment_type": "دين", "total": 255.0, "date": "2025-11-07", "swap": {"olive_weight": 30.0, "oil_received": 16.0, "difference_liters": 2.0, "difference_price": 30.0}}
                ]
            },
            "debts": {
                "seq": 1,
                "items": [
                    {"id": 1, "customer_id": 2, "invoice_id": 2, "remaining_amount": 255.0, "status": "غير مدفوع"}
                ]
            },
            "adjustments": {
                "seq": 1,
                "items": [
                    {"id": 1, "ref_type": "invoice", "ref_id": 2, "action": "تصحيح وزن", "details": "وزن الكيس كان 15 كغ بدل 14 كغ", "timestamp": "2025-11-07T14:20:00"}
                ]
            },
            "settings": {
                "prices": {"oil_per_liter": 15.0, "bottle": 5.0},
                "unit_weights": {"دلو": 14.0, "صندوق": 14.5, "كيس": None, "كيلو": 1.0},
                "options": {"payment_types": ["نقدي", "دين", "إلكتروني"]}
            }
        }
        for name in ["customers", "deliveries", "invoices", "debts", "adjustments", "settings"]:
            if fill_demo:
                self.save(name, demo[name])
            else:
                self.save(name, {"seq": 0, "items": []} if name != "settings" else {"prices": {"oil_per_liter": 15.0, "bottle": 5.0}, "unit_weights": {"دلو": 14.0, "صندوق": 14.5, "كيس": None, "كيلو": 1.0}, "options": {"payment_types": ["نقدي", "دين", "إلكتروني"]}})