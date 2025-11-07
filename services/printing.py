def render_invoice_template(invoice_data, customer_data):
    # دالة وهمية: ترجع نص HTML بسيط للفاتورة مع اسم العميل
    return f"<html><body><h1>فاتورة رقم {invoice_data.get('id', '')}</h1><p>العميل: {customer_data.get('name', '')}</p></body></html>"


def save_invoice_pdf(invoice_data, file_path):
    # دالة وهمية: تحفظ نص الفاتورة في ملف PDF (هنا تحفظ كـ HTML فقط)
    html = render_invoice_template(invoice_data, {"name": "غير معروف"})
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(html)
    return file_path
