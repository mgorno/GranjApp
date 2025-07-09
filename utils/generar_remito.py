from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.platypus import Table, TableStyle
from decimal import Decimal
from datetime import datetime

def generar_pdf_remito(nombre_cliente, direccion, fecha_entrega, detalles, total_remito, saldo_anterior, id_remito):
    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=A4)
    ancho, alto = A4
    margen_x = 40
    y = alto - 40

    def formato_cantidad(n):
        return str(int(n)) if n == int(n) else f"{n:.3f}".rstrip("0").replace(".", ",")

    def formato_con_signo(n):
        n = float(n)
        return f"${int(n)}" if n == int(n) else f"${n:.2f}".rstrip("0").rstrip(".")

    # === Encabezado del vendedor ===
    p.setFont("Helvetica-Bold", 16)
    p.drawString(margen_x, y, "Pollería Do Pollo")
    p.setFont("Helvetica", 10)
    y -= 15
    p.drawString(margen_x, y, "CUIT: 30-12345678-9  |  Tel: 11-2345-6789")
    y -= 15
    p.drawString(margen_x, y, "Dirección: Av. de los Cruz 1234, CABA")
    y -= 25

    # === Título del remito ===
    p.setFont("Helvetica-Bold", 18)
    p.drawCentredString(ancho / 2, y, "REMITO")
    y -= 25
    p.setFont("Helvetica", 11)
    p.drawRightString(ancho - margen_x, y, f"Fecha: {fecha_entrega.strftime('%d/%m/%Y')}")
    y -= 15
    p.drawRightString(ancho - margen_x, y, f"N.º Remito: {id_remito}")
    y -= 25

    # === Datos del cliente ===
    p.setFont("Helvetica-Bold", 11)
    p.drawString(margen_x, y, "Cliente:")
    p.setFont("Helvetica", 10)
    p.drawString(margen_x + 50, y, nombre_cliente)
    y -= 15
    p.drawString(margen_x, y, "Dirección:")
    p.drawString(margen_x + 50, y, direccion)
    y -= 30

    # === Tabla de productos ===
    data = [["Producto", "Cantidad", "Precio Unit.", "Subtotal"]]
    for item in detalles:
        desc = item["descripcion"]
        cantidad = formato_cantidad(item["cantidad_real"])
        precio = formato_con_signo(item["precio"])
        subtotal = formato_con_signo(item["cantidad_real"] * item["precio"])
        data.append([desc, cantidad, precio, subtotal])

    table = Table(data, colWidths=[220, 80, 80, 80])
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.black),
        ("ALIGN", (1, 1), (-1, -1), "RIGHT"),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
        ("FONTSIZE", (0, 0), (-1, -1), 10),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("BOTTOMPADDING", (0, 0), (-1, 0), 8),
    ]))
    table.wrapOn(p, ancho, alto)
    table_height = table._height
    table.drawOn(p, margen_x, y - table_height)

    y = y - table_height - 30

    # === Totales ===
    p.setFont("Helvetica-Bold", 11)
    p.line(margen_x, y, ancho - margen_x, y)
    y -= 20
    p.drawRightString(ancho - margen_x, y, f"Total del remito: {formato_con_signo(total_remito)}")
    y -= 15
    p.drawRightString(ancho - margen_x, y, f"Saldo anterior: {formato_con_signo(saldo_anterior)}")
    y -= 15
    total = Decimal(str(total_remito)) + Decimal(str(saldo_anterior))
    p.drawRightString(ancho - margen_x, y, f"Saldo total: {formato_con_signo(total)}")

    # === Firma ===
    y -= 60
    p.setFont("Helvetica", 10)
    p.drawString(margen_x, y, "__________________________")
    p.drawString(margen_x, y - 12, "Firma del Cliente")
    p.drawRightString(ancho - margen_x, y, "__________________________")
    p.drawRightString(ancho - margen_x, y - 12, "Firma del Vendedor")

    # === Pie de página ===
    y -= 40
    p.setFont("Helvetica-Oblique", 9)
    p.drawCentredString(ancho / 2, y, "Gracias por su compra. Consulte nuestras ofertas mayoristas semanales.")

    p.showPage()
    p.save()
    buffer.seek(0)
    return buffer
