from flask import (
    Blueprint, render_template, request, redirect,
    url_for, flash, send_file, abort
)
from models import get_conn
from psycopg2.extras import RealDictCursor
from datetime import datetime
import uuid
from collections import defaultdict
from utils.generar_remito import generar_pdf_remito

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
        # Validar pedido
        cur.execute("SELECT * FROM pedidos WHERE id_pedido = %s", (id_pedido,))
        if not cur.fetchone():
            abort(404, "Pedido no encontrado")

        if request.method == "POST":
            # actualizar cantidades reales y precios
            cantidades_reales = request.form.getlist("cantidad_real")
            id_detalles = request.form.getlist("id_detalle")
            precios = request.form.getlist("precio")

            for id_det, real_str, precio_str in zip(id_detalles, cantidades_reales, precios):
                real = float(real_str.replace(',', '.')) if real_str else 0
                precio = float(precio_str.replace(',', '.')) if precio_str else 0
                cur.execute(
                    "UPDATE detalle_pedido SET cantidad_real=%s, precio=%s WHERE id_detalle=%s",
                    (real, precio, id_det)
                )

            # traer cliente y pedido
            cur.execute("""
                SELECT c.id_cliente, c.nombre, c.direccion, p.fecha_entrega
                FROM pedidos p
                JOIN clientes c ON p.id_cliente=c.id_cliente
                WHERE p.id_pedido=%s
            """, (id_pedido,))
            cli = cur.fetchone()

            # traer detalles actualizados
            cur.execute("""
                SELECT pd.id_detalle, pd.id_producto, pr.descripcion, pr.unidad_base AS unidad,
                       pd.cantidad, pd.cantidad_real, pd.precio
                FROM detalle_pedido pd
                JOIN productos pr ON pd.id_producto=pr.id_producto
                WHERE pd.id_pedido=%s
            """, (id_pedido,))
            detalles_raw = cur.fetchall()

            # calcular total
            total = sum(
                float(row['cantidad_real'] or row['cantidad']) * float(row['precio'] or 0)
                for row in detalles_raw
            )

            # insertar movimientos
            cur.execute("SELECT saldo FROM clientes_cuenta_corriente WHERE id_cliente=%s", (cli['id_cliente'],))
            saldo_anterior = cur.fetchone()["saldo"] if cur.rowcount else 0
            cur.execute(
                "INSERT INTO movimientos_cuenta_corriente(id_movimiento, id_cliente, fecha, tipo_mov, importe) VALUES(%s,%s,%s,'compra',%s)",
                (str(uuid.uuid4()), cli['id_cliente'], datetime.utcnow().date(), total)
            )
            cur.execute(
                "INSERT INTO clientes_cuenta_corriente(id_cliente, saldo) VALUES(%s,%s) ON CONFLICT(id_cliente) DO UPDATE SET saldo=clientes_cuenta_corriente.saldo+EXCLUDED.saldo",
                (cli['id_cliente'], total)
            )

            # guardar remito
            cur.execute(
                "INSERT INTO remitos(id_pedido, fecha, total, saldo_anterior) VALUES(%s,NOW(),%s,%s) RETURNING id_remito",
                (id_pedido, total, saldo_anterior)
            )
            id_remito = cur.fetchone()["id_remito"]

            # detalle_remito: usar id_producto correcto
            for row in detalles_raw:
                cant_real = float(row['cantidad_real'] or row['cantidad'])
                cur.execute(
                    "INSERT INTO detalle_remito(id_remito, id_producto, cantidad, precio) VALUES(%s,%s,%s,%s)",
                    (id_remito, row['id_producto'], cant_real, float(row['precio'] or 0))
                )

            # actualizar estado pedido
            cur.execute("UPDATE pedidos SET estado='entregado' WHERE id_pedido=%s", (id_pedido,))
            conn.commit()

            return redirect(url_for("entregas.visualizador_pdf_remito", id_remito=id_remito))

        # GET: mostrar formulario con detalles previos
        cur.execute("""
            SELECT pd.id_detalle, pr.descripcion, pr.unidad_base AS unidad,
                   pd.cantidad, pd.cantidad_real, pd.precio
            FROM detalle_pedido pd
            JOIN productos pr ON pd.id_producto=pr.id_producto
            WHERE pd.id_pedido=%s
        """, (id_pedido,))
        detalles = [
            {**row,
             'cantidad_real': float(row['cantidad_real'] or row['cantidad']),
             'precio': float(row['precio'] or 0)}
            for row in cur.fetchall()
        ]

        cur.execute("SELECT id_cliente FROM pedidos WHERE id_pedido=%s", (id_pedido,))
        id_cliente = cur.fetchone()["id_cliente"]
        cur.execute("SELECT saldo FROM clientes_cuenta_corriente WHERE id_cliente=%s", (id_cliente,))
        saldo_anterior = cur.fetchone()["saldo"] if cur.rowcount else 0
        cur.execute("""
            SELECT c.nombre AS cliente_nombre, p.fecha_entrega
            FROM pedidos p
            JOIN clientes c ON p.id_cliente=c.id_cliente
            WHERE p.id_pedido=%s
        """, (id_pedido,))
        info_cliente = cur.fetchone()

    return render_template(
        "remito_confirmar.html",
        detalles=detalles,
        productos=obtener_productos(),
        id_pedido=id_pedido,
        saldo_anterior=saldo_anterior,
        cliente_nombre=info_cliente['cliente_nombre'],
        fecha_entrega=info_cliente['fecha_entrega']
    )

@bp_entregas.route("/remito/pdf/<int:id_remito>")
def remito_pdf(id_remito):
    with get_conn() as conn, conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute("SELECT * FROM remitos WHERE id_remito=%s", (id_remito,))
        remito = cur.fetchone()
        if not remito:
            abort(404, "Remito no encontrado")
        # obtener detalles con unidad
        cur.execute("""
            SELECT pr.descripcion, pr.unidad_base AS unidad,
                   dr.cantidad AS cantidad_real, dr.precio
            FROM detalle_remito dr
            JOIN productos pr ON dr.id_producto=pr.id_producto
            WHERE dr.id_remito=%s
        """, (id_remito,))
        detalles = cur.fetchall()
        cur.execute("""
            SELECT c.nombre, c.direccion, p.fecha_entrega
            FROM pedidos p
            JOIN clientes c ON p.id_cliente=c.id_cliente
            WHERE p.id_pedido=%s
        """, (remito['id_pedido'],))
        cli = cur.fetchone()
    total_remito = sum(float(item['cantidad_real'])*float(item['precio']) for item in detalles)
    pdf_buffer = generar_pdf_remito(
        nombre_cliente=cli['nombre'],
        direccion=cli['direccion'],
        fecha_entrega=cli['fecha_entrega'],
        detalles=detalles,
        total_remito=total_remito,
        saldo_anterior=remito['saldo_anterior'],
        id_remito=id_remito
    )
    filename=f"Remito_{cli['nombre'].replace(' ', '_')}_{id_remito}.pdf"
    return send_file(pdf_buffer, mimetype="application/pdf", download_name=filename)

@bp_entregas.route("/remito/visor/<int:id_remito>")
def visualizador_pdf_remito(id_remito):
    return render_template("visor_pdf_remito.html", id_remito=id_remito)
