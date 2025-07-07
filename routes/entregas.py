from flask import (
    Blueprint, render_template, request, redirect,
    url_for, flash, send_file, abort
)
from models import get_conn
from psycopg2.extras import RealDictCursor
from datetime import datetime
import uuid
from collections import defaultdict

bp_entregas = Blueprint("entregas", __name__, url_prefix="/entregas")

@bp_entregas.route("/")
def lista_entregas():
    """
    Lista los pedidos pendientes agrupados por fecha de entrega
    """
    with get_conn() as conn, conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute("""
            SELECT p.id_pedido,
                   c.nombre,
                   p.fecha_entrega,
                   COUNT(pd.id_detalle) AS cantidad_items
            FROM pedidos p
            JOIN clientes c     ON p.id_cliente  = c.id_cliente
            JOIN detalle_pedido pd ON pd.id_pedido = p.id_pedido
            WHERE p.estado = 'pendiente'
            GROUP BY p.id_pedido, c.nombre, p.fecha_entrega
            ORDER BY p.fecha_entrega
        """)
        rows = cur.fetchall()

    entregas_por_fecha = defaultdict(list)
    for row in rows:
        entregas_por_fecha[row["fecha_entrega"].strftime("%Y-%m-%d")].append({
            "id_pedido":      row["id_pedido"],
            "cliente":        row["nombre"],
            "fecha_entrega":  row["fecha_entrega"],
            "cantidad_items": row["cantidad_items"]
        })

    return render_template("entregas_pendientes.html", entregas=entregas_por_fecha)

@bp_entregas.route("/<uuid:id_pedido>/remito", methods=["GET", "POST"])
def remito(id_pedido):
    with get_conn() as conn, conn.cursor(cursor_factory=RealDictCursor) as cur:
        # Verificar que exista el pedido
        cur.execute("SELECT * FROM pedidos WHERE id_pedido = %s", (str(id_pedido),))
        pedido = cur.fetchone()
        if not pedido:
            abort(404, "Pedido no encontrado")

        if request.method == "POST":
            cantidades_reales = request.form.getlist("cantidad_real")
            id_detalles = request.form.getlist("id_detalle")

            if len(cantidades_reales) != len(id_detalles):
                flash("Faltan datos para registrar la entrega.", "error")
                return redirect(url_for("entregas.remito", id_pedido=id_pedido))

            for id_det, real in zip(id_detalles, cantidades_reales):
                cur.execute(
                    "UPDATE detalle_pedido SET cantidad_real = %s WHERE id_detalle = %s",
                    (real, id_det)
                )

            # Obtener datos cliente y pedido
            cur.execute("""
                SELECT c.id_cliente, c.nombre, c.direccion, p.fecha_entrega
                FROM pedidos p
                JOIN clientes c ON p.id_cliente = c.id_cliente
                WHERE p.id_pedido = %s
            """, (str(id_pedido),))
            cli = cur.fetchone()
            if not cli:
                flash("Cliente no encontrado.", "error")
                return redirect(url_for("entregas.lista_entregas"))

            # Obtener detalles actualizados
            cur.execute("""
                SELECT pr.descripcion,
                       pd.cantidad_real,
                       pd.unidad,
                       pd.precio,
                       pd.id_detalle
                FROM detalle_pedido pd
                JOIN productos pr ON pd.id_producto = pr.id_producto
                WHERE pd.id_pedido = %s
            """, (str(id_pedido),))
            detalles_raw = cur.fetchall()

            total = 0
            detalles = []
            for row in detalles_raw:
                cant_real = float(row["cantidad_real"] or 0)
                precio = float(row["precio"] or 0)
                total += cant_real * precio
                detalles.append({**row, "cantidad_real": cant_real, "precio": precio})

            mov_id = str(uuid.uuid4())
            cur.execute("""
                INSERT INTO movimientos_cuenta_corriente
                    (id_movimiento, id_cliente, fecha, tipo_mov, importe)
                VALUES (%s, %s, %s, 'compra', %s)
            """, (mov_id, cli["id_cliente"], datetime.utcnow().date(), total))

            cur.execute("""
                INSERT INTO clientes_cuenta_corriente (id_cliente, saldo)
                VALUES (%s, %s)
                ON CONFLICT (id_cliente)
                DO UPDATE SET saldo = clientes_cuenta_corriente.saldo + EXCLUDED.saldo
            """, (cli["id_cliente"], total))

            cur.execute("UPDATE pedidos SET estado = 'entregado' WHERE id_pedido = %s", (str(id_pedido),))
            conn.commit()

            # Aquí deberías tener la función generar_pdf_remito definida o importada
            pdf_buffer = generar_pdf_remito(
                cli["nombre"], cli["direccion"], cli["fecha_entrega"], detalles, total
            )
            filename = f"Remito_{cli['nombre']}_{id_pedido}.pdf"
            return send_file(pdf_buffer, mimetype="application/pdf",
                             as_attachment=True, download_name=filename)

        # --- GET ---
        cur.execute("""
            SELECT pd.id_detalle,
                   pr.descripcion,
                   pd.cantidad,
                   pd.cantidad_real,
                   pd.unidad,
                   pd.precio,
                   pd.id_producto
            FROM detalle_pedido pd
            JOIN productos pr ON pd.id_producto = pr.id_producto
            WHERE pd.id_pedido = %s
        """, (str(id_pedido),))
        items = cur.fetchall()

        cur.execute("SELECT id_cliente FROM pedidos WHERE id_pedido = %s", (str(id_pedido),))
        row = cur.fetchone()
        id_cliente = row["id_cliente"] if row else None

        saldo_anterior = 0
        if id_cliente:
            cur.execute("SELECT saldo FROM clientes_cuenta_corriente WHERE id_cliente = %s", (id_cliente,))
            row_saldo = cur.fetchone()
            saldo_anterior = row_saldo["saldo"] if row_saldo else 0

    return render_template(
        "remito_confirmar.html",
        items=items,
        id_pedido=id_pedido,
        saldo_anterior=saldo_anterior
    )
