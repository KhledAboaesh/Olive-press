UNIT_WEIGHTS = {
    "دلو": 14.0,
    "صندوق": 14.5,  # متوسط بين 14–15
    "كيس": None,    # يحتاج وزن يدوي بعد الميزان
    "كيلو": 1.0
}

def compute_total_weight(package_type, quantity, manual_weight=None):
    if package_type == "كيس":
        if manual_weight is None or manual_weight <= 0:
            raise ValueError("أدخل الوزن الحقيقي للأكياس بعد الميزان.")
        return manual_weight
    if package_type == "كيلو":
        return float(quantity)
    unit = UNIT_WEIGHTS.get(package_type)
    if unit is None:
        raise ValueError(f"نوع تعبئة غير معروف: {package_type}")
    return float(quantity) * unit

def compute_invoice_total(oil_quantity, price_per_liter,
                          bottle_count_shop, bottle_price,
                          extra_costs=0.0, discounts=0.0):
    base = float(oil_quantity) * float(price_per_liter)
    bottles = int(bottle_count_shop) * float(bottle_price)
    return round(base + bottles + float(extra_costs) - float(discounts), 2)
