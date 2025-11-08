import os
from datetime import datetime
from PySide6.QtPrintSupport import QPrinter, QPrintDialog
from PySide6.QtGui import QTextDocument

def render_invoice_template(invoice, customer):
    """إنشاء HTML للفواتير مع هوية المعصرة"""
    brand_name = invoice.get("brand_name", "معصرة الزيتون")
    logo_path = os.path.join("assets", "logo.png")

    html = f"""
    <html>
    <head>
        <meta charset="utf-8">
        <style>
            body {{ font-family: Tahoma; margin: 40px; }}
            h1 {{ color: #006400; text-align: center; }}
            table {{
                border-collapse: collapse;
                width: 100%;
                margin-top: 20px;
            }}
            th, td {{
                border: 1px solid #000;
                padding: 8px;
                text-align: center;
            }}
            th {{
                background-color: #006400;
                color: white;
            }}
            tr:nth-child(even) {{ background-color: #f2f2f2; }}
            .footer {{
                margin-top: 30px;
                font-size: 12pt;
                text-align: right;
                color: #555;
            }}
        </style>
    </head>
    <body>
        <div style="text-align:center;">
            <img src="{logo_path}" alt="Logo" style="width:60px;"><br>
            <h1>{brand_name}</h1>
        </div>
        <p><b>رقم الفاتورة:</b> {invoice.get("id","---")}</p>
        <p><b>الزبون:</b> {customer.get("name","غير معروف")}</p>
        <p><b>التاريخ:</b> {invoice.get("date","")}</p>

        <table>
            <tr>
                <th>نوع العملية</th>
                <th>كمية الزيت (لتر)</th>
                <th>سعر/لتر</th>
                <th>عبوات الزبون</th>
                <th>عبوات المعصرة</th>
                <th>طريقة الدفع</th>
                <th>الإجمالي</th>
                <th>المدفوع</th>
                <th>المتبقي</th>
            </tr>
            <tr>
                <td>{invoice.get("operation_type","")}</td>
                <td>{invoice.get("oil_quantity",0)}</td>
                <td>{invoice.get("price_per_liter",0)}</td>
                <td>{invoice.get("bottle_count_customer",0)}</td>
                <td>{invoice.get("bottle_count_shop",0)}</td>
                <td>{invoice.get("payment_type","")}</td>
                <td>{invoice.get("total",0)}</td>
                <td>{invoice.get("paid_amount",0)}</td>
                <td>{invoice.get("remaining_amount",0)}</td>
            </tr>
        </table>
        <br>
        <br>
        <br>
        <br>
        <br>
        <br>
        <br>
        <br>
        <br>
        <br>
        <br>
        <br>
        <br>
        <br>
        <br>
        <br>
        <br>
        <br>
        <br>
        <br>
        <br>
        <br>
        <br>
        <br>
        <br>
        <br>
        <br>
        <div class="footer">
            تم الطباعة بتاريخ: {datetime.now().strftime("%Y-%m-%d %H:%M")}
        </div>
    </body>
    </html>
    """
    return html

def print_invoice(html, parent=None):
    """طباعة الفاتورة مباشرة"""
    doc = QTextDocument()
    doc.setHtml(html)
    printer = QPrinter(QPrinter.HighResolution)
    dialog = QPrintDialog(printer, parent)
    if dialog.exec() == QPrintDialog.Accepted:
        doc.print_(printer)

def save_invoice_pdf(html, path):
    """حفظ الفاتورة كملف PDF"""
    doc = QTextDocument()
    doc.setHtml(html)
    printer = QPrinter(QPrinter.HighResolution)
    printer.setOutputFormat(QPrinter.PdfFormat)
    printer.setOutputFileName(path)
    doc.print_(printer)
