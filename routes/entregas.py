from flask import Blueprint, render_template, request, redirect, url_for, flash, abort, send_file
from models import get_conn
from psycopg2 import sql
from psycopg2.extras import RealDictCursor
from datetime import datetime, date
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
            "fecha_entrega":  row["fecha_entrega"].strftime("%Y-%m-%d"),
            "cantidad_items": row["cantidad_items"]
        })
    fecha_hoy = date.today().strftime("%Y-%m-%d")
    return render_template("entregas_pendientes.html", entregas=entregas_por_fecha, fecha_hoy=fecha_hoy)

from psycopg2 import sql

def obtener_productos(excluir_ids=None):
    query = "SELECT id_producto, descripcion, unidad_base, precio FROM productos"
    params = []

    if excluir_ids:
        placeholders = ','.join(['%s'] * len(excluir_ids))
        query += f" WHERE id_producto NOT IN ({placeholders})"
        params.extend(excluir_ids)

    query += " ORDER BY descripcion"

    with get_conn() as conn, conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute(query, params)
        return cur.fetchall()


@bp_entregas.route("/<id_pedido>/remito", methods=["GET", "POST"])
def remito(id_pedido):
    with get_conn() as conn, conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute("SELECT * FROM pedidos WHERE id_pedido = %s", (id_pedido,))
        pedido = cur.fetchone()
        if not pedido:
            abort(404, "Pedido no encontrado")

        if request.method == "POST":
            accion = request.form.get("accion")

            if accion == "agregar":
                nuevo_id_producto = request.form.get("nuevo_id_producto")
                nueva_cantidad = request.form.get("nuevo_cantidad")
                if nuevo_id_producto and nueva_cantidad:
                    try:
                        cant = float(nueva_cantidad.replace(',', '.'))
                        if cant > 0:
                            cur.execute("SELECT precio, unidad_base FROM productos WHERE id_producto = %s", (nuevo_id_producto,))
                            precio_producto = cur.fetchone()
                            precio_val = float(precio_producto['precio']) if precio_producto else 0
                            unidad_val = precio_producto['unidad_base'] if precio_producto else 'unidad'

                            cur.execute("""
                                INSERT INTO detalle_pedido (id_pedido, id_producto, cantidad, cantidad_real, precio, unidad)
                                VALUES (%s, %s, %s, %s, %s, %s)
                            """, (id_pedido, nuevo_id_producto, cant, cant, precio_val, unidad_val))
                            conn.commit()
                            flash("Producto agregado correctamente", "success")
                    except Exception as e:
                        flash(f"Error al agregar producto nuevo: {e}", "danger")

                return redirect(url_for("entregas.remito", id_pedido=id_pedido))

            elif accion == "confirmar":
                cantidades_reales = request.form.getlist("cantidad_real[]")
                id_detalles = request.form.getlist("id_detalle[]")
                precios = request.form.getlist("precio[]")

                for id_det, real_str, precio_str in zip(id_detalles, cantidades_reales, precios):
                    try:
                        real = float(real_str.replace(',', '.'))
                    except:
                        real = 0
                    try:
                        precio = float(precio_str.replace(',', '.'))
                    except:
                        precio = 0
                    cur.execute("""
                        UPDATE detalle_pedido
                        SET cantidad_real = %s,
                            precio = %s
                        WHERE id_detalle = %s
                    """, (real, precio, id_det))

                cur.execute("""
                    SELECT c.id_cliente, c.nombre, c.direccion, p.fecha_entrega
                    FROM pedidos p
                    JOIN clientes c ON p.id_cliente = c.id_cliente
                    WHERE p.id_pedido = %s
                """, (id_pedido,))
                cli = cur.fetchone()

                cur.execute("""
                    SELECT pr.descripcion,
                           pr.unidad_base, 
                           pd.cantidad,
                           pd.cantidad_real,
                           pd.precio,
                           pd.id_producto
                    FROM detalle_pedido pd
                    JOIN productos pr ON pd.id_producto = pr.id_producto
                    WHERE pd.id_pedido = %s
                """, (id_pedido,))
                detalles_raw = cur.fetchall()

                total = sum(
                    float(row['cantidad_real'] or row['cantidad']) * float(row['precio'] or 0)
                    for row in detalles_raw
                )

                cur.execute("SELECT saldo FROM clientes_cuenta_corriente WHERE id_cliente = %s", (cli['id_cliente'],))
                saldo_anterior = cur.fetchone()["saldo"] if cur.rowcount else 0

                cur.execute("SELECT id_remito FROM remitos WHERE id_pedido = %s", (id_pedido,))
                remito_existente = cur.fetchone()

                if remito_existente:
                    id_remito = remito_existente["id_remito"]
                else:
                    cur.execute("""
                        INSERT INTO remitos (id_pedido, fecha, total, saldo_anterior)
                        VALUES (%s, NOW(), %s, %s)
                        RETURNING id_remito
                    """, (id_pedido, total, saldo_anterior))
                    id_remito = cur.fetchone()["id_remito"]

                    for row in detalles_raw:
                        cant_real = float(row['cantidad_real'] or row['cantidad'])
                        cur.execute("""
                            INSERT INTO detalle_remito (id_remito, id_producto, cantidad, precio)
                            VALUES (%s, %s, %s, %s)
                        """, (id_remito, row['id_producto'], cant_real, float(row['precio'] or 0)))

                    cur.execute("UPDATE pedidos SET estado = 'entregado' WHERE id_pedido = %s", (id_pedido,))

                cur.execute("""
                    SELECT id_movimiento FROM movimientos_cuenta_corriente 
                    WHERE id_cliente = %s AND tipo_mov = 'compra' AND importe = %s AND id_remito = %s
                """, (cli['id_cliente'], total, id_remito))
                mov_existente = cur.fetchone()

                if not mov_existente:
                    cur.execute("""
                        INSERT INTO movimientos_cuenta_corriente
                            (id_movimiento, id_cliente, fecha, tipo_mov, importe, id_remito)
                        VALUES (%s, %s, %s, 'compra', %s, %s)
                    """, (str(uuid.uuid4()), cli['id_cliente'], datetime.utcnow().date(), total, id_remito))

                    cur.execute("""
                        INSERT INTO clientes_cuenta_corriente (id_cliente, saldo)
                        VALUES (%s, %s)
                        ON CONFLICT (id_cliente)
                        DO UPDATE SET saldo = clientes_cuenta_corriente.saldo + EXCLUDED.saldo
                    """, (cli['id_cliente'], total))

                conn.commit()
                return redirect(url_for("entregas.visualizador_pdf_remito", id_remito=id_remito))

        # ---- GET o POST sin acción válida ----
        cur.execute("""
            SELECT pd.id_detalle,
                   pr.descripcion,
                   pd.cantidad,
                   pd.cantidad_real,
                   pd.precio,
                   pr.unidad_base
            FROM detalle_pedido pd
            JOIN productos pr ON pd.id_producto = pr.id_producto
            WHERE pd.id_pedido = %s
        """, (id_pedido,))
        detalles_raw = cur.fetchall()

        detalles = [
            {
                **row,
                'cantidad_real': float(row['cantidad_real'] or row['cantidad']),
                'precio': float(row['precio'] or 0)
            }
            for row in detalles_raw
        ]

        cur.execute("SELECT id_cliente FROM pedidos WHERE id_pedido = %s", (id_pedido,))
        id_cliente = cur.fetchone()["id_cliente"]

        cur.execute("SELECT saldo FROM clientes_cuenta_corriente WHERE id_cliente = %s", (id_cliente,))
        saldo_anterior = cur.fetchone()["saldo"] if cur.rowcount else 0

        cur.execute("""
            SELECT c.nombre AS cliente_nombre, p.fecha_entrega
            FROM pedidos p
            JOIN clientes c ON p.id_cliente = c.id_cliente
            WHERE p.id_pedido = %s
        """, (id_pedido,))
        info_cliente = cur.fetchone()

        # Excluir productos ya cargados
        cur.execute("SELECT id_producto FROM detalle_pedido WHERE id_pedido = %s", (id_pedido,))
        ids_ya_cargados = [row["id_producto"] for row in cur.fetchall()]
        productos_disponibles = obtener_productos(excluir_ids=ids_ya_cargados)

    return render_template(
        "remito_confirmar.html",
        detalles=detalles,
        productos=productos_disponibles,
        id_pedido=id_pedido,
        saldo_anterior=saldo_anterior,
        cliente_nombre=info_cliente["cliente_nombre"],
        fecha_entrega=info_cliente["fecha_entrega"]
    )

@bp_entregas.route("/remito/pdf/<int:id_remito>")
def remito_pdf(id_remito):
    with get_conn() as conn, conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute("SELECT * FROM remitos WHERE id_remito = %s", (id_remito,))
        remito = cur.fetchone()
        if not remito:
            abort(404, "Remito no encontrado")

        cur.execute("""
            SELECT pr.descripcion,
                   dr.cantidad AS cantidad_real,
                   dr.precio,
                   pr.unidad_base 
            FROM detalle_remito dr
            JOIN productos pr ON dr.id_producto = pr.id_producto
            WHERE dr.id_remito = %s
        """, (id_remito,))
        detalles = cur.fetchall()

        cur.execute("""
            SELECT c.nombre, c.direccion, p.fecha_entrega
            FROM pedidos p
            JOIN clientes c ON p.id_cliente = c.id_cliente
            WHERE p.id_pedido = %s
        """, (remito['id_pedido'],))
        cli = cur.fetchone()

    total_remito = sum(
        float(item['cantidad_real']) * float(item['precio']) for item in detalles
    )

    pdf_buffer = generar_pdf_remito(
        nombre_cliente=cli['nombre'],
        direccion=cli['direccion'],
        fecha_entrega=cli['fecha_entrega'],
        detalles=detalles,
        total_remito=total_remito,
        saldo_anterior=remito['saldo_anterior'],
        id_remito=id_remito
    )
    filename = f"Remito_{cli['nombre'].replace(' ', '_')}_{id_remito}.pdf"
    return send_file(pdf_buffer, mimetype="application/pdf", download_name=filename)

@bp_entregas.route("/remito/visor/<int:id_remito>")
def visualizador_pdf_remito(id_remito):
    return render_template("visor_pdf_remito.html", id_remito=id_remito)

@bp_entregas.route("/<id_pedido>/cancelar", methods=["POST"])
def cancelar_pedido(id_pedido):
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute("SELECT estado FROM pedidos WHERE id_pedido = %s", (id_pedido,))
        pedido = cur.fetchone()
        if not pedido:
            abort(404, "Pedido no encontrado")

        if pedido[0] == 'entregado':
            flash("No se puede cancelar un pedido ya entregado.", "danger")
        else:
            cur.execute("UPDATE pedidos SET estado = 'cancelado' WHERE id_pedido = %s", (id_pedido,))
            conn.commit()
            flash("Pedido cancelado exitosamente.", "success")

    return redirect(url_for("entregas.lista_entregas"))
