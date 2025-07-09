from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.platypus import Table, TableStyle
from decimal import Decimal
from datetime import datetime
from formatos_numeros import formato_precio_arg, formato_cantidad


def generar_pdf_remito(nombre_cliente, direccion, fecha_entrega, detalles, total_remito, saldo_anterior, id_remito):
    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=A4)
    ancho, alto = A4
    margen_x = 40
    y = alto - 40


    # === Encabezado elegante ===
    p.setFont("Helvetica-Bold", 16)
    p.setFillColor(colors.darkblue)
    p.drawString(margen_x, y, "Pollería Do Pollo")
    p.setFillColor(colors.black)
    p.setFont("Helvetica", 10)
    y -= 15
    p.drawString(margen_x, y, "CUIT: 30-12345678-9  |  Tel: 11-2345-6789")
    y -= 15
    p.drawString(margen_x, y, "Dirección: Av. de los Cruz 1234, CABA")
    y -= 20

    # Línea divisoria
    p.setStrokeColor(colors.grey)
    p.setLineWidth(0.5)
    p.line(margen_x, y, ancho - margen_x, y)
    y -= 25

    # === Título y datos del remito ===
    p.setFont("Helvetica-Bold", 18)
    p.setFillColor(colors.black)
    p.drawCentredString(ancho / 2, y, "REMITO")
    y -= 25
    p.setFont("Helvetica", 11)
    fecha_str = fecha_entrega.strftime('%d/%m/%Y') if isinstance(fecha_entrega, datetime) else ""
    p.drawRightString(ancho - margen_x, y, f"Fecha: {fecha_str}")
    y -= 15
    p.drawRightString(ancho - margen_x, y, f"N.º Remito: {id_remito}")
    y -= 25

    # === Datos del cliente ===
    p.setFont("Helvetica-Bold", 11)
    p.drawString(margen_x, y, "Cliente:")
    p.setFont("Helvetica", 10)
    p.drawString(margen_x + 50, y, nombre_cliente or "")
    y -= 15
    p.drawString(margen_x, y, "Dirección:")
    p.drawString(margen_x + 50, y, direccion or "")
    y -= 30

    # === Tabla de productos ===
    data = [["Producto", "Cantidad", "Precio Unit.", "Subtotal"]]
    for item in detalles:
        desc = item.get("descripcion", "")
        cantidad = formato_cantidad(item.get("cantidad_real", 0))
        precio_unit = item.get("precio", 0)
        precio = formato_precio_arg(precio_unit)
        subtotal_val = Decimal(str(item.get("cantidad_real", 0))) * Decimal(str(precio_unit))
        subtotal = formato_precio_arg(subtotal_val)
        data.append([desc, cantidad, precio, subtotal])

    table = Table(data, colWidths=[220, 80, 80, 80])
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#dfe9f3")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.darkblue),
        ("ALIGN", (1, 1), (-1, -1), "RIGHT"),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
        ("FONTSIZE", (0, 0), (-1, -1), 10),
        ("GRID", (0, 0), (-1, -1), 0.3, colors.grey),
        ("BOTTOMPADDING", (0, 0), (-1, 0), 6),
        ("TOPPADDING", (0, 1), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 1), (-1, -1), 4),
    ]))
    table.wrapOn(p, ancho, alto)
    table_height = table._height
    table.drawOn(p, margen_x, y - table_height)

    y -= table_height + 30

    # === Totales ===
    p.setFont("Helvetica-Bold", 11)
    p.setStrokeColor(colors.black)
    p.setLineWidth(0.7)
    p.line(margen_x, y, ancho - margen_x, y)
    y -= 20
    p.drawRightString(ancho - margen_x, y, f"Total del remito: {formato_precio_arg(total_remito)}")
    y -= 15
    p.drawRightString(ancho - margen_x, y, f"Saldo anterior: {formato_precio_arg(saldo_anterior)}")
    y -= 15
    total = Decimal(str(total_remito)) + Decimal(str(saldo_anterior))
    p.drawRightString(ancho - margen_x, y, f"Saldo total: {formato_precio_arg(total)}")

    # === Firmas ===
    y -= 60
    p.setFont("Helvetica", 10)a
    p.drawString(margen_x, y, "__________________________")
    p.drawString(margen_x, y - 12, "Firma del Cliente")
    p.drawRightString(ancho - margen_x, y, "__________________________")
    p.drawRightString(ancho - margen_x, y - 12, "Firma del Vendedor")

    # === Pie de página ===
    y -= 40
    p.setFont("Helvetica-Oblique", 9)
    p.setFillColor(colors.grey)
    p.drawCentredString(ancho / 2, y, "Aca se puede agregar algo o lo dejamos vacio?")
    p.setFillColor(colors.black)

    p.showPage()
    p.save()
    buffer.seek(0)
    return buffer
