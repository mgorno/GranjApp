from flask import Blueprint, render_template, request, redirect, url_for, flash, send_file
from models import get_conn
import uuid
from datetime import datetime
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from collections import defaultdict




bp_entregas = Blueprint("entregas", __name__, url_prefix="/entregas")

def generar_pdf_remito(cliente, direccion, fecha_entrega, detalles, total):
    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=A4)
    pdf.setFont("Helvetica", 12)
    pdf.drawString(50, 800, f"Remito - {datetime.now().strftime('%d/%m/%Y')}")
    pdf.drawString(50, 780, f"Cliente: {cliente}")
    pdf.drawString(50, 765, f"Dirección: {direccion}")
    pdf.drawString(50, 750, f"Fecha Entrega: {fecha_entrega.strftime('%d/%m/%Y')}")

    y = 720
    pdf.drawString(50, y, "Producto")
    pdf.drawString(250, y, "Cant.")
    pdf.drawString(320, y, "Unidad")
    pdf.drawString(400, y, "Precio")

    for d in detalles:
        y -= 20
        pdf.drawString(50, y, d['descripcion'])
        pdf.drawString(250, y, str(d['cantidad_real']))
        pdf.drawString(320, y, d['unidad'])
        pdf.drawString(400, y, f"${d['precio']:.2f}")

    y -= 30
    pdf.drawString(50, y, f"Total: ${total:.2f}")
    pdf.showPage()
    pdf.save()
    buffer.seek(0)
    return buffer


@bp_entregas.route("/")
def lista_entregas():
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute("""
            SELECT p.id_pedido, c.nombre, p.fecha_entrega, COUNT(dp.id_detalle) as cantidad_items
            FROM pedidos p
            JOIN clientes c ON p.id_cliente = c.id_cliente
            JOIN detalle_pedido dp ON dp.id_pedido = p.id_pedido
            WHERE p.estado = 'pendiente'
            GROUP BY p.id_pedido, c.nombre, p.fecha_entrega
            ORDER BY p.fecha_entrega
        """)
        rows = cur.fetchall()

    entregas_por_fecha = defaultdict(list)
    for id_pedido, nombre, fecha_entrega, cantidad_items in rows:
        fecha_str = fecha_entrega.strftime("%Y-%m-%d")
        entregas_por_fecha[fecha_str].append({
            'id_pedido': id_pedido,
            'cliente': nombre,
            'fecha_entrega': fecha_entrega,
            'cantidad_items': cantidad_items
        })

    return render_template("entregas_pendientes.html", entregas=entregas_por_fecha)



@bp_entregas.route("/<id_pedido>/remito", methods=['GET', 'POST'])
def generar_remito(id_pedido):
    if request.method == 'POST':
        cantidades_reales = request.form.getlist("cantidad_real")
        id_detalles = request.form.getlist("id_detalle")

        if not cantidades_reales or not id_detalles or len(cantidades_reales) != len(id_detalles):
            flash("Faltan datos para registrar la entrega.", "error")
            return redirect(url_for("entregas.generar_remito", id_pedido=id_pedido))

        with get_conn() as conn:
            with conn.cursor() as cur:
                # Actualizar cantidades reales
                for id_det, real in zip(id_detalles, cantidades_reales):
                    cur.execute("""
                        UPDATE detalle_pedido
                        SET cantidad_real = %s
                        WHERE id_detalle = %s
                    """, (real, id_det))

                # Obtener datos del pedido y cliente
                cur.execute("""
                    SELECT p.id_cliente, c.nombre, c.direccion, p.fecha_entrega
                    FROM pedidos p
                    JOIN clientes c ON p.id_cliente = c.id_cliente
                    WHERE p.id_pedido = %s
                """, (id_pedido,))
                pedido_info = cur.fetchone()
                if not pedido_info:
                    flash("Pedido no encontrado.", "error")
                    return redirect(url_for("entregas.lista_entregas"))

                id_cliente, cliente, direccion, fecha_entrega = pedido_info

                # Obtener detalles con cantidades actualizadas
                cur.execute("""
                    SELECT pr.descripcion, dp.cantidad_real, pr.unidad_base, dp.precio
                    FROM detalle_pedido dp
                    JOIN productos pr ON dp.id_producto = pr.id_producto
                    WHERE dp.id_pedido = %s
                """, (id_pedido,))
                detalles_raw = cur.fetchall()

                detalles = []
                total = 0
                for desc, cant_real, unidad, precio in detalles_raw:
                    cant_real = float(cant_real or 0)
                    precio = float(precio or 0)
                    total += cant_real * precio
                    detalles.append({
                        'descripcion': desc,
                        'cantidad_real': cant_real,
                        'unidad': unidad,
                        'precio': precio
                    })

                # Insertar movimiento en cuenta corriente
                cur.execute("""
                    INSERT INTO movimientos_cuenta_corriente (id_movimiento, id_cliente, fecha, tipo_mov, importe)
                    VALUES (%s, %s, %s, %s, %s)
                """, (str(uuid.uuid4()), id_cliente, datetime.now().date(), 'compra', total, 'remito'))

                # Actualizar saldo cliente
                cur.execute("""
                    INSERT INTO clientes_cuenta_corriente (id_cliente, saldo)
                    VALUES (%s, %s)
                    ON CONFLICT (id_cliente) DO UPDATE SET saldo = clientes_cuenta_corriente.saldo + %s
                """, (id_cliente, total, total))

                # Cambiar estado pedido a entregado
                cur.execute("UPDATE pedidos SET estado = 'entregado' WHERE id_pedido = %s", (id_pedido,))

                conn.commit()

                # Generar PDF y enviar
                pdf_buffer = generar_pdf_remito(cliente, direccion, fecha_entrega, detalles, total)
                return send_file(pdf_buffer, mimetype='application/pdf', as_attachment=True,
                                 download_name=f"Remito_{cliente}_{id_pedido}.pdf")

    # GET: Mostrar formulario para confirmar cantidades reales
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute("""
            SELECT dp.id_detalle, pr.descripcion, dp.cantidad, dp.cantidad_real, pr.unidad_base, dp.precio
            FROM detalle_pedido dp
            JOIN productos pr ON dp.id_producto = pr.id_producto
            WHERE dp.id_pedido = %s
        """, (id_pedido,))
        detalles = cur.fetchall()

    return render_template("remito_confirmar.html", detalles=detalles, id_pedido=id_pedido)
