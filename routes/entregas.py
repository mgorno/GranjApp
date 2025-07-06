from flask import Blueprint, render_template, request, redirect, url_for, flash, send_file
from models import get_conn
import uuid, io
from datetime import datetime
# from utils import generar_pdf_remito  # cuando tengas lista la generación del PDF

bp_entregas = Blueprint("entregas", __name__, url_prefix="/entregas")

@bp_entregas.route("/")
def lista_entregas():
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute("""
            SELECT p.id_pedido, c.nombre, p.fecha_entrega, COUNT(dp.id_detalle)
            FROM pedidos p
            JOIN clientes c ON p.id_cliente = c.id_cliente
            JOIN detalle_pedido dp ON dp.id_pedido = p.id_pedido
            WHERE p.estado = 'pendiente'
            GROUP BY p.id_pedido, c.nombre, p.fecha_entrega
            ORDER BY p.fecha_entrega
        """)
        entregas = cur.fetchall()

    return render_template("entregas_pendientes.html", entregas=entregas)


@bp_entregas.route("/<id_pedido>/remito", methods=['GET', 'POST'])
def generar_remito(id_pedido):
    if request.method == 'POST':
        cantidades_reales = request.form.getlist("cantidad_real")
        id_detalles       = request.form.getlist("id_detalle")

        if not cantidades_reales or not id_detalles:
            flash("Faltan datos para registrar la entrega.", "error")
            return redirect(url_for("entregas.generar_remito", id_pedido=id_pedido))

        with get_conn() as conn:
            with conn.cursor() as cur:
                # 1. Actualizar cantidades reales
                for id_det, real in zip(id_detalles, cantidades_reales):
                    cur.execute("""
                        UPDATE detalle_pedido
                        SET cantidad_real = %s
                        WHERE id_detalle = %s
                    """, (real, id_det))

                # 2. Obtener cliente y total
                cur.execute("""
                    SELECT p.id_cliente, SUM(dp.cantidad_real * dp.precio)
                    FROM pedidos p
                    JOIN detalle_pedido dp ON dp.id_pedido = p.id_pedido
                    WHERE p.id_pedido = %s
                    GROUP BY p.id_cliente
                """, (id_pedido,))
                id_cliente, total = cur.fetchone()

                # 3. Insertar en movimientos
                cur.execute("""
                    INSERT INTO movimientos_cuenta_corriente (id_movimiento, id_cliente, fecha, tipo_mov, importe, forma_pago)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, (str(uuid.uuid4()), id_cliente, datetime.now().date(), 'venta', total, 'remito'))

                # 4. Actualizar saldo
                cur.execute("""
                    INSERT INTO clientes_cuenta_corriente (id_cliente, saldo)
                    VALUES (%s, %s)
                    ON CONFLICT (id_cliente) DO UPDATE SET saldo = clientes_cuenta_corriente.saldo + %s
                """, (id_cliente, total, total))

                # 5. Cambiar estado del pedido
                cur.execute("UPDATE pedidos SET estado = 'entregado' WHERE id_pedido = %s", (id_pedido,))
            conn.commit()

        flash("Remito generado y entrega confirmada.", "success")
        return redirect(url_for("entregas.lista_entregas"))

    # Si es GET, mostrar form para confirmar cantidades reales
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute("""
            SELECT dp.id_detalle, pr.descripcion, dp.cantidad, dp.precio, pr.unidad_base
            FROM detalle_pedido dp
            JOIN productos pr ON dp.id_producto = pr.id_producto
            WHERE dp.id_pedido = %s
        """, (id_pedido,))
        detalles = cur.fetchall()

    return render_template("remito_confirmar.html", detalles=detalles, id_pedido=id_pedido)
