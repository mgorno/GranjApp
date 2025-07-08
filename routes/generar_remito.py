routes/fn_generar_remito.py from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.platypus import Table, TableStyle


def generar_pdf_remito(nombre_cliente, direccion, fecha_entrega, detalles, total_remito, saldo_anterior):
    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=A4)

    ancho, alto = A4
    margen_x = 40
    y = alto - 40

    # Logo y título
    p.setFont("Helvetica-Bold", 18)
    p.drawCentredString(ancho / 2, y, "REMITO DE ENTREGA")
    y -= 40

    # Cliente
    p.setFont("Helvetica", 11)
    p.drawString(margen_x, y, f"Cliente: {nombre_cliente}")
    y -= 15
    p.drawString(margen_x, y, f"Dirección: {direccion}")
    y -= 15
    p.drawString(margen_x, y, f"Fecha de entrega: {fecha_entrega.strftime('%d/%m/%Y')}")
    y -= 30

    # Tabla de productos
    data = [["Producto", "Cantidad", "Precio", "Subtotal"]]
    for item in detalles:
        desc = item["descripcion"]
        cant = f"{item['cantidad_real']:.2f}"
        precio = f"${item['precio']:.2f}"
        subtotal = f"${item['cantidad_real'] * item['precio']:.2f}"
        data.append([desc, cant, precio, subtotal])

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

    # Totales
    p.setFont("Helvetica-Bold", 11)
    p.line(margen_x, y, ancho - margen_x, y)
    y -= 20
    p.drawRightString(ancho - margen_x, y, f"Total del remito: ${total_remito:.2f}")
    y -= 15
    p.drawRightString(ancho - margen_x, y, f"Saldo anterior: ${saldo_anterior:.2f}")
    y -= 15
    p.drawRightString(ancho - margen_x, y, f"Saldo total: ${total_remito + saldo_anterior:.2f}")

    y -= 40
    p.setFont("Helvetica-Oblique", 9)
    p.drawString(margen_x, y, "Gracias por su compra. Consulte por nuestras promociones mayoristas.")

    p.showPage()
    p.save()
    buffer.seek(0)
    return buffer
