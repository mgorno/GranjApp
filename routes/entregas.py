from flask import Blueprint, render_template, request, redirect, url_for, flash, abort, send_file, jsonify
from models import get_conn
from psycopg2 import sql
from psycopg2.extras import RealDictCursor
from datetime import datetime, date
import uuid
from collections import defaultdict
from utils.generar_remito import generar_pdf_remito
from decimal import Decimal


bp_entregas = Blueprint("entregas", __name__, url_prefix="/entregas")

@bp_entregas.route("/")
def lista_entregas():
    with get_conn() as conn, conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute("""
            SELECT p.id_pedido,
                   c.nombre,
                   p.fecha_entrega,
                   COUNT(pd.id_detalle) AS cantidad_items,
                   EXISTS (
                     SELECT 1 FROM remitos r WHERE r.id_pedido = p.id_pedido
                   ) AS tiene_remito,
                   (
                     SELECT id_remito FROM remitos r WHERE r.id_pedido = p.id_pedido LIMIT 1
                   ) AS id_remito
            FROM pedidos p
            JOIN clientes c     ON p.id_cliente  = c.id_cliente
            JOIN detalle_pedido pd ON pd.id_pedido = p.id_pedido
            WHERE p.estado in ('pendiente', 'preparado')
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
            "cantidad_items": row["cantidad_items"],
            "tiene_remito":   row["tiene_remito"],
            "id_remito":      row["id_remito"],
        })

    fecha_hoy = date.today().strftime("%Y-%m-%d")

    return render_template("entregas_pendientes.html", entregas=entregas_por_fecha, fecha_hoy=fecha_hoy)




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

            if accion == "editar_cliente_fecha":
                nuevo_cliente = request.form.get("nuevo_cliente")
                nueva_fecha_entrega = request.form.get("nueva_fecha_entrega")

                if nuevo_cliente and nueva_fecha_entrega:
                    try:
                        cur.execute("""
                            UPDATE pedidos
                            SET id_cliente = %s,
                                fecha_entrega = %s
                            WHERE id_pedido = %s
                        """, (nuevo_cliente, nueva_fecha_entrega, id_pedido))
                        conn.commit()
                        flash("Cliente y fecha de entrega actualizados correctamente.", "success")
                    except Exception as e:
                        flash(f"Error al actualizar cliente o fecha: {e}", "danger")

                return redirect(url_for("entregas.remito", id_pedido=id_pedido))

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
                        INSERT INTO remitos (id_pedido, fecha, total, saldo_anterior, estado)
                        VALUES (%s, NOW(), %s, %s, 'emitido')
                        RETURNING id_remito
                    """, (id_pedido, total, saldo_anterior))
                    id_remito = cur.fetchone()["id_remito"]

                    for row in detalles_raw:
                        cant_real = float(row['cantidad_real'] or row['cantidad'])
                        cur.execute("""
                            INSERT INTO detalle_remito (id_remito, id_producto, cantidad, precio)
                            VALUES (%s, %s, %s, %s)
                        """, (id_remito, row['id_producto'], cant_real, float(row['precio'] or 0)))

                    cur.execute("UPDATE pedidos SET estado = 'preparado' WHERE id_pedido = %s", (id_pedido,))

   

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
            SELECT c.nombre AS cliente_nombre, p.fecha_entrega, c.telefono, p.estado
            FROM pedidos p
            JOIN clientes c ON p.id_cliente = c.id_cliente
            WHERE p.id_pedido = %s
        """, (id_pedido,))
        info_cliente = cur.fetchone()

        # Excluir productos ya cargados
        cur.execute("SELECT id_producto FROM detalle_pedido WHERE id_pedido = %s", (id_pedido,))
        ids_ya_cargados = [row["id_producto"] for row in cur.fetchall()]
        productos_disponibles = obtener_productos(excluir_ids=ids_ya_cargados)
        fecha_entrega_str = info_cliente["fecha_entrega"].strftime("%Y-%m-%d")
        fecha_hoy_str = date.today().strftime("%Y-%m-%d")

        cur.execute("SELECT id_cliente, nombre FROM clientes ORDER BY nombre")
        clientes = cur.fetchall()
        cur.execute("SELECT COUNT(*) AS cantidad FROM detalle_pedido WHERE id_pedido = %s", (id_pedido,))
        cantidad_items = cur.fetchone()["cantidad"]
        total_remito = sum(
            float(row['cantidad_real'] or row['cantidad']) * float(row['precio'] or 0)
            for row in detalles_raw 
        )
            
        saldo_total = saldo_anterior + Decimal(total_remito)
    
        # Si existe un remito ya generado
        cur.execute("SELECT id_remito FROM remitos WHERE id_pedido = %s", (id_pedido,))
        remito_generado = cur.fetchone()
        id_remito = remito_generado["id_remito"] if remito_generado else None


    return render_template(
        "remito_confirmar.html",
        detalles=detalles,
        productos=productos_disponibles,
        id_pedido=id_pedido,
        saldo_anterior=saldo_anterior,
        saldo_total = saldo_total,
        cliente_nombre=info_cliente["cliente_nombre"],
        telefono=info_cliente["telefono"],
        estado=info_cliente["estado"],
        fecha_entrega=fecha_entrega_str,
        fecha_hoy=fecha_hoy_str,
        clientes=clientes,
        cantidad_items=cantidad_items,
        id_remito=id_remito,
        remito_generado=bool(id_remito)
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
    with get_conn() as conn, conn.cursor(cursor_factory=RealDictCursor) as cur:
        # Buscar remito
        cur.execute("SELECT * FROM remitos WHERE id_remito = %s", (id_remito,))
        remito = cur.fetchone()
        if not remito:
            abort(404, "Remito no encontrado")

        # Traer datos del cliente y pedido
        cur.execute("""
            SELECT p.id_pedido, c.telefono, c.nombre AS cliente_nombre, p.fecha_entrega
            FROM pedidos p
            JOIN clientes c ON p.id_cliente = c.id_cliente
            WHERE p.id_pedido = %s
        """, (remito['id_pedido'],))
        pedido_info = cur.fetchone()

        # Traer los detalles del remito para calcular el total
        cur.execute("""
            SELECT cantidad AS cantidad_real, precio
            FROM detalle_remito
            WHERE id_remito = %s
        """, (id_remito,))
        detalles = cur.fetchall()

        total_remito = sum(
            Decimal(str(d['cantidad_real'])) * Decimal(str(d['precio']))
            for d in detalles
        )
        saldo_anterior = remito.get("saldo_anterior", 0)
        saldo_total = saldo_anterior + total_remito

        fecha_entrega_str = pedido_info["fecha_entrega"].strftime("%Y-%m-%d")

    return render_template(
        "visor_pdf_remito.html",
        id_remito=id_remito,
        telefono=pedido_info["telefono"],
        total_remito=total_remito,
        saldo_anterior=saldo_anterior,
        saldo_total=saldo_total,
        fecha_entrega=fecha_entrega_str
    )


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


@bp_entregas.route("/api/eliminar_item", methods=["POST"])
def api_eliminar_item():
    data = request.get_json()
    id_pedido = data.get("id_pedido")
    id_detalle = data.get("id_item") 
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("SELECT COUNT(*) FROM detalle_pedido WHERE id_pedido = %s", (id_pedido,))
    cantidad = cur.fetchone()[0]

    if cantidad <= 1:
        response = {"ok": False, "error": "No se puede eliminar el último producto del pedido"}
    else:
        cur.execute("DELETE FROM detalle_pedido WHERE id_detalle = %s AND id_pedido = %s", (id_detalle, id_pedido))
        conn.commit()
        response = {"ok": True}

    cur.close()
    conn.close()
    return jsonify(response)

