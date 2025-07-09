from io import BytesIO
from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML
from decimal import Decimal
from datetime import datetime
from jinja2 import Environment, FileSystemLoader
env = Environment(loader=FileSystemLoader('templates'))

def generar_pdf_remito(nombre_cliente, direccion, fecha_entrega, detalles, total_remito, saldo_anterior, id_remito):
    env = Environment(loader=FileSystemLoader("."))  # buscar en directorio actual
    template = env.get_template("remito_template.html")

    # Procesar datos
    for item in detalles:
        item["cantidad"] = f"{item['cantidad_real']:.2f}".replace(".", ",")
        item["precio"] = f"${item['precio']:.2f}".replace(".", ",")
        subtotal = item["cantidad_real"] * item["precio"]
        item["subtotal"] = f"${subtotal:.2f}".replace(".", ",")

    total = Decimal(str(total_remito)) + Decimal(str(saldo_anterior))

    html_renderizado = template.render(
        cliente=nombre_cliente,
        direccion=direccion,
        fecha=fecha_entrega.strftime("%d/%m/%Y"),
        id_remito=id_remito,
        detalles=detalles,
        total_remito=f"${total_remito:.2f}".replace(".", ","),
        saldo_anterior=f"${saldo_anterior:.2f}".replace(".", ","),
        saldo_total=f"${total:.2f}".replace(".", ",")
    )

    pdf_buffer = BytesIO()
    HTML(string=html_renderizado).write_pdf(pdf_buffer)
    pdf_buffer.seek(0)
    return pdf_buffer
