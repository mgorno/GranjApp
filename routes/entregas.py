from flask import (
    Blueprint, render_template, request, redirect,
    url_for, flash, send_file, abort
)
from models import get_conn
from psycopg2.extras import RealDictCursor
from datetime import datetime
import uuid
from collections import defaultdict
from .generar_remito import generar_pdf_remito

bp_entregas = Blueprint("entregas", __name__, url_prefix="/entregas")

@bp_entregas.route("/")
def lista_entregas():
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

def obtener_productos():
    with get_conn() as conn, conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute("SELECT id_producto, descripcion, unidad_base, precio FROM productos ORDER BY descripcion")
        return cur.fetchall()

@bp_entregas.route("/<id_pedido>/remito", methods=["GET", "POST"])
def remito(id_pedido):
    with get_conn() as conn, conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute("SELECT * FROM pedidos WHERE id_pedido = %s", (id_pedido,))
        pedido = cur.fetchone()
        if not pedido:
            abort(404, "Pedido no encontrado")

        if request.method == "POST":
            cantidades_reales = request.form.getlist("cantidad_real")
            id_detalles = request.form.getlist("id_detalle")
            precios = request.form.getlist("precio")
            id_productos = request.form.getlist("id_producto")

            if not (len(cantidades_reales) == len(id_detalles) == len(precios) == len(id_productos)):
                flash("Faltan datos para registrar la entrega.", "error")
                return redirect(url_for("entregas.remito", id_pedido=id_pedido))

            for id_det, real_str, precio_str, id_prod in zip(id_detalles, cantidades_reales, precios, id_productos):
                try:
                    real = float(real_str.replace(',', '.'))
                except Exception:
                    real = 0
                try:
                    precio = float(precio_str.replace(',', '.'))
                except Exception:
                    precio = 0

                cur.execute("""
                    UPDATE detalle_pedido
                    SET cantidad_real = %s,
                        precio = %s,
                        id_producto = %s
                    WHERE id_detalle = %s
                """, (real, precio, id_prod, id_det))

            cur.execute("""
                SELECT c.id_cliente, c.nombre, c.direccion, p.fecha_entrega
                FROM pedidos p
                JOIN clientes c ON p.id_cliente = c.id_cliente
                WHERE p.id_pedido = %s
            """, (id_pedido,))
            cli = cur.fetchone()
            if not cli:
                flash("Cliente no encontrado.", "error")
                return redirect(url_for("entregas.lista_entregas"))

            cur.execute("""
                SELECT pr.descripcion,
                       pd.cantidad,
                       pd.cantidad_real,
                       pd.unidad,
                       pd.precio,
                       pd.id_detalle,
                       pd.id_producto
                FROM detalle_pedido pd
                JOIN productos pr ON pd.id_producto = pr.id_producto
                WHERE pd.id_pedido = %s
            """, (id_pedido,))
            detalles_raw = cur.fetchall()

            total = 0
            detalles = []
            for row in detalles_raw:
                cant_real = row["cantidad_real"]
                if cant_real is None:
                    cant_real = row["cantidad"]
                cant_real = float(cant_real)
                precio = float(row["precio"] or 0)
                total += cant_real * precio
                detalles.append({**row, "cantidad_real": cant_real, "precio": precio})

            cur.execute("SELECT saldo FROM clientes_cuenta_corriente WHERE id_cliente = %s", (cli["id_cliente"],))
            row_saldo = cur.fetchone()
            saldo_anterior = row_saldo["saldo"] if row_saldo else 0

            cur.execute("""
                INSERT INTO movimientos_cuenta_corriente
                    (id_movimiento, id_cliente, fecha, tipo_mov, importe)
                VALUES (%s, %s, %s, 'compra', %s)
            """, (str(uuid.uuid4()), cli["id_cliente"], datetime.utcnow().date(), total))

            cur.execute("""
                INSERT INTO clientes_cuenta_corriente (id_cliente, saldo)
                VALUES (%s, %s)
                ON CONFLICT (id_cliente)
                DO UPDATE SET saldo = clientes_cuenta_corriente.saldo + EXCLUDED.saldo
            """, (cli["id_cliente"], total))

            # Guardar el remito y sus detalles
            cur.execute("""
                INSERT INTO remitos (id_pedido, fecha, total, saldo_anterior)
                VALUES (%s, NOW(), %s, %s)
                RETURNING id_remito
            """, (id_pedido, total, saldo_anterior))
            id_remito = cur.fetchone()["id_remito"]

            for row in detalles:
                cur.execute("""
                    INSERT INTO detalle_remito (id_remito, id_producto, cantidad, precio_unitario)
                    VALUES (%s, %s, %s, %s)
                """, (id_remito, row["id_producto"], row["cantidad_real"], row["precio"]))

            cur.execute("UPDATE pedidos SET estado = 'entregado' WHERE id_pedido = %s", (id_pedido,))
            conn.commit()

            return redirect(url_for("entregas.visualizar_remito", id_remito=id_remito))

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
        """, (id_pedido,))
        detalles_raw = cur.fetchall()

        detalles = []
        for row in detalles_raw:
            cant_real = row["cantidad_real"]
            if cant_real is None:
                cant_real = row["cantidad"]
            cant_real = float(cant_real)
            precio = float(row["precio"] or 0)
            detalles.append({**row, "cantidad_real": cant_real, "precio": precio})

        cur.execute("SELECT id_cliente FROM pedidos WHERE id_pedido = %s", (id_pedido,))
        row = cur.fetchone()
        id_cliente = row["id_cliente"] if row else None

        saldo_anterior = 0
        if id_cliente:
            cur.execute("SELECT saldo FROM clientes_cuenta_corriente WHERE id_cliente = %s", (id_cliente,))
            row_saldo = cur.fetchone()
            saldo_anterior = row_saldo["saldo"] if row_saldo else 0

        cur.execute("""
            SELECT c.nombre AS cliente_nombre, p.fecha_entrega
            FROM pedidos p
            JOIN clientes c ON p.id_cliente = c.id_cliente
            WHERE p.id_pedido = %s
        """, (id_pedido,))
        info_cliente = cur.fetchone()

    return render_template(
        "remito_confirmar.html",
        detalles=detalles,
        productos=obtener_productos(),
        id_pedido=id_pedido,
        saldo_anterior=saldo_anterior,
        cliente_nombre=info_cliente["cliente_nombre"],
        fecha_entrega=info_cliente["fecha_entrega"]
    )

@bp_entregas.route("/remito/visualizar/<int:id_remito>")
def visualizar_remito(id_remito):
    conn = get_conn()
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        # Traemos el remito principal
        cur.execute("SELECT * FROM remitos WHERE id_remito = %s", (id_remito,))
        remito = cur.fetchone()
        if not remito:
            abort(404, "Remito no encontrado")

        # Traemos los detalles del remito
        cur.execute("SELECT * FROM detalle_remito WHERE id_remito = %s", (id_remito,))
        detalles = cur.fetchall()


    # Calculamos total sumando precio * cantidad_real
    total_remito = sum(
        (item.get("precio") or 0) * (item.get("cantidad") or 0) for item in detalles
    )

    return render_template(
        "visualizar_remito.html",
        id_remito=id_remito,
        cliente_nombre=remito.get("cliente"),
        fecha_entrega=remito.get("fecha"),
        detalles=detalles,
        total_remito=total_remito
    )

