import io

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet

from app.models.order import Order


def generate_invoice_pdf(order: Order) -> bytes:
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=20 * mm, bottomMargin=20 * mm)
    styles = getSampleStyleSheet()
    elements = []

    elements.append(Paragraph("Campus Eats — Invoice", styles["Title"]))
    elements.append(Spacer(1, 6))
    elements.append(Paragraph(f"Order Number: {order.order_number}", styles["Normal"]))
    elements.append(Paragraph(f"Status: {order.status.value}", styles["Normal"]))
    if order.placed_at:
        elements.append(Paragraph(f"Placed At: {order.placed_at.strftime('%Y-%m-%d %H:%M')}", styles["Normal"]))
    elements.append(Spacer(1, 12))

    table_data = [["Item", "Qty", "Unit Price", "Subtotal"]]
    for item in order.items:
        table_data.append(
            [item.food_name_snapshot, str(item.quantity), f"Rs. {item.unit_price_snapshot:.2f}", f"Rs. {item.subtotal:.2f}"]
        )

    item_table = Table(table_data, colWidths=[70 * mm, 20 * mm, 35 * mm, 35 * mm])
    item_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#f97316")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                ("ALIGN", (1, 0), (-1, -1), "RIGHT"),
            ]
        )
    )
    elements.append(item_table)
    elements.append(Spacer(1, 12))

    totals_data = [
        ["Item Total", f"Rs. {order.item_total:.2f}"],
        ["Discount", f"- Rs. {order.discount_amount:.2f}"],
        ["Delivery Charge", f"Rs. {order.delivery_charge:.2f}"],
        ["Packing Charge", f"Rs. {order.packing_charge:.2f}"],
        ["GST", f"Rs. {order.gst_amount:.2f}"],
        ["Grand Total", f"Rs. {order.grand_total:.2f}"],
    ]
    totals_table = Table(totals_data, colWidths=[100 * mm, 40 * mm])
    totals_table.setStyle(
        TableStyle(
            [
                ("ALIGN", (1, 0), (-1, -1), "RIGHT"),
                ("FONTNAME", (0, -1), (-1, -1), "Helvetica-Bold"),
                ("LINEABOVE", (0, -1), (-1, -1), 1, colors.black),
            ]
        )
    )
    elements.append(totals_table)

    doc.build(elements)
    return buffer.getvalue()
