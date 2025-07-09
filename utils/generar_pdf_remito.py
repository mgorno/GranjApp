from io import BytesIO
from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML
from decimal import Decimal
from datetime import datetime
import os

def generar_pdf_remito(nombre_cliente, direccion, fecha_entrega, detalles, total_remito, saldo_anterior, id_remito):
    # Configurar Jinja2 para cargar templates desde carpeta 'templates' al nivel superior
    template_dir = os.path.join(os.path.dirname(__file__), '..', 'templates')
    env = Environment(loader=FileSystemLoader(template_dir))
    template = env.get_template("remito_template.html")

    # Convertir números y calcular subtotales correctamente
    for item in detalles:
        cantidad = float(item["cantidad_real"])  # siempre como número
        precio = float(item["precio"])           # siempre como número

        subtotal_val = cantidad * precio         # cálculo numérico subtotal

        # Guardar las versiones formateadas para mostrar en plantilla HTML
        item["cantidad"] = f"{cantidad:.2f}".replace(".", ",")
        item["precio"] = f"${precio:.2f}".replace(".", ",")
        item["subtotal"] = f"${subtotal_val:.2f}".replace(".", ",")

    # Calcular el saldo total (suma de totales y saldo anterior)
    total = Decimal(str(total_remito)) + Decimal(str(saldo_anterior))

    # Formatear los totales para mostrar
    total_remito_fmt = f"${float(total_remito):.2f}".replace(".", ",")
    saldo_anterior_fmt = f"${float(saldo_anterior):.2f}".replace(".", ",")
    saldo_total_fmt = f"${float(total):.2f}".replace(".", ",")

    # Renderizar el HTML con los datos
    html_renderizado = template.render(
        cliente=nombre_cliente,
        direccion=direccion,
        fecha=fecha_entrega.strftime("%d/%m/%Y"),
        id_remito=id_remito,
        detalles=detalles,
        total_remito=total_remito_fmt,
        saldo_anterior=saldo_anterior_fmt,
        saldo_total=saldo_total_fmt
    )

    # Generar PDF en memoria con WeasyPrint
    pdf_buffer = BytesIO()
    HTML(string=html_renderizado).write_pdf(pdf_buffer)
    pdf_buffer.seek(0)
    return pdf_buffer
