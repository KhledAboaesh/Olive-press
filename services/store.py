import os, json

class JsonStore:
    def __init__(self, folder="data"):
        self.folder = folder
        os.makedirs(folder, exist_ok=True)

    def _path(self, name):
        return os.path.join(self.folder, f"{name}.json")

    def _init(self, name):
        """إنشاء الملف إذا لم يكن موجود أو إصلاحه إذا ناقص"""
        path = self._path(name)
        if not os.path.exists(path):
            with open(path, "w", encoding="utf-8") as f:
                json.dump({"items": [], "last_id": 0}, f, ensure_ascii=False, indent=2)
        else:
            # إصلاح الملفات الناقصة
            with open(path, "r", encoding="utf-8") as f:
                try:
                    data = json.load(f)
                except Exception:
                    data = {}
            if "items" not in data:
                data["items"] = []
            if "last_id" not in data:
                data["last_id"] = 0
            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)

    def load(self, name):
        self._init(name)
        with open(self._path(name), "r", encoding="utf-8") as f:
            return json.load(f)

    def save(self, name, data):
        with open(self._path(name), "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def list(self, name):
        return self.load(name).get("items", [])

    def insert(self, name, item):
        data = self.load(name)
        if "last_id" not in data:
            data["last_id"] = 0
        data["last_id"] += 1
        item["id"] = data["last_id"]
        data["items"].append(item)
        self.save(name, data)
        return item

    def update(self, name, item_id, updates):
        data = self.load(name)
        for item in data["items"]:
            if item["id"] == item_id:
                item.update(updates)
                break
        self.save(name, data)

    def delete(self, name, item_id):
        data = self.load(name)
        data["items"] = [i for i in data["items"] if i["id"] != item_id]
        self.save(name, data)

    def reset_all(self, fill_demo=False):
        for fname in os.listdir(self.folder):
            if fname.endswith(".json"):
                os.remove(os.path.join(self.folder, fname))
        for name in ["customers", "deliveries", "invoices", "debts", "adjustments", "settings"]:
            self._init(name)
        if fill_demo:
            cust = self.insert("customers", {"name": "زبون تجريبي"})
            inv = self.insert("invoices", {
                "customer_id": cust["id"],
                "total": 100,
                "remaining_amount": 100,
                "status": "غير مدفوع",
                "date": "2025-11-07"
            })
            self.insert("debts", {
                "customer_id": cust["id"],
                "invoice_id": inv["id"],
                "remaining_amount": 100,
                "status": "غير مدفوع",
                "date": "2025-11-07"
            })

    # دوال خاصة بالديون
    def settle_debt(self, debt_id):
        data = self.load("debts")
        for d in data["items"]:
            if d["id"] == debt_id:
                d["remaining_amount"] = 0
                d["status"] = "مدفوع"
                break
        self.save("debts", data)

    def partial_settle_debt(self, debt_id, amount):
        data = self.load("debts")
        for d in data["items"]:
            if d["id"] == debt_id and d["status"] != "مدفوع":
                remaining = d.get("remaining_amount", 0)
                new_remaining = max(0, remaining - amount)
                d["remaining_amount"] = new_remaining
                d["status"] = "مدفوع" if new_remaining == 0 else "غير مدفوع"
                break
        self.save("debts", data)
