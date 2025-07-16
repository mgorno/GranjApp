
from .formatos_numeros import formato_precio_arg, formato_cantidad
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

    # Encabezado institucional
    p.setFont("Helvetica-Bold", 14)
    p.drawString(margen_x, y, "LA ESCUELA DEL ÁRBOL")
    p.setFont("Helvetica", 10)
    y -= 15
    p.drawString(margen_x, y, "de Green School S.A.")
    y -= 12
    p.drawString(margen_x, y, "Zapiola 955 - C1426ATS - CABA")
    y -= 12
    p.drawString(margen_x, y, "Tel.: 4551-5630 / 4554-1589 - www.laescueladelarbol.com.ar")
    y -= 12
    p.drawString(margen_x, y, "infolaescueladelarbol@gmail.com")
    y -= 12
    p.drawString(margen_x, y, "C.U.I.T.: 30-65679856-0 | INGRESOS BRUTOS: EXENTO")
    y -= 12
    p.drawString(margen_x, y, "CAJA PREV. COMERCIO Nº 65679856 | I.V.A.: EXENTO")
    y -= 20

    # Línea divisoria
    p.setStrokeColor(colors.grey)
    p.setLineWidth(0.5)
    p.line(margen_x, y, ancho - margen_x, y)
    y -= 20

    # Fecha y Número
    fecha_str = fecha_entrega.strftime('%d/%m/%Y') if isinstance(fecha_entrega, datetime) else ""
    p.setFont("Helvetica-Bold", 11)
    p.drawString(margen_x, y, f"Fecha: {fecha_str}")
    p.drawRightString(ancho - margen_x, y, f"Recibo N.º: {id_remito}")
    y -= 20

    # Datos cliente
    p.setFont("Helvetica", 10)
    p.drawString(margen_x, y, f"Señor: {nombre_cliente or ''}")
    y -= 12
    p.drawString(margen_x, y, f"Domicilio: {direccion or ''}")
    y -= 12
    p.drawString(margen_x, y, f"CUIL: _______________________")  # Se puede pasar como parámetro
    y -= 20

    # Tabla de conceptos
    data = [["Concepto", "Cantidad", "Importe Unitario", "Importe Total"]]
    for item in detalles:
        concepto = item.get("descripcion", "")
        cantidad = formato_cantidad(item.get("cantidad_real", 0))
        precio_unit = item.get("precio", 0)
        total = Decimal(str(item.get("cantidad_real", 0))) * Decimal(str(precio_unit))
        data.append([
            concepto,
            cantidad,
            formato_precio_arg(precio_unit),
            formato_precio_arg(total)
        ])

    tabla = Table(data, colWidths=[230, 70, 90, 90])
    tabla.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#f0f0f0")),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("ALIGN", (1, 1), (-1, -1), "RIGHT"),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("FONTSIZE", (0, 0), (-1, -1), 10),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))

    tabla.wrapOn(p, ancho, alto)
    tabla_altura = tabla._height
    tabla.drawOn(p, margen_x, y - tabla_altura)
    y -= tabla_altura + 20

    # Totales y medios de pago
    p.setFont("Helvetica-Bold", 10)
    p.drawRightString(ancho - margen_x, y, f"TOTAL: {formato_precio_arg(total_remito)}")
    y -= 15
    p.setFont("Helvetica", 9)
    y -= 20



    p.showPage()
    p.save()
    buffer.seek(0)
    return buffer
