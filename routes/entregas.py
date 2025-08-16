from flask import Blueprint, render_template, request, redirect, url_for, flash, abort, send_file, jsonify
from models import get_conn
from psycopg2 import sql
from psycopg2.extras import RealDictCursor
from datetime import datetime, date
import uuid
from collections import defaultdict
from utils.generar_remito import generar_pdf_remito
from decimal import Decimal
import json


bp_entregas = Blueprint("entregas", __name__, url_prefix="/entregas")

@bp_entregas.route("/")
def lista_entregas():
    with get_conn() as conn, conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute("""
            SELECT p.id_pedido,
                   c.nombre,
                   p.fecha_entrega,
                    (
                    SELECT COUNT(*)
                    FROM detalle_pedido dp
                    WHERE dp.id_pedido = p.id_pedido
                    ) cantidad_items,
                   EXISTS (
                     SELECT 1 FROM remitos r WHERE r.id_pedido = p.id_pedido
                   ) AS tiene_remito,
                   (
                     SELECT id_remito FROM remitos r WHERE r.id_pedido = p.id_pedido LIMIT 1
                   ) AS id_remito
            FROM pedidos p
            JOIN clientes c     ON p.id_cliente  = c.id_cliente
            LEFT JOIN remitos r      ON r.id_pedido   = p.id_pedido
            LEFT JOIN detalle_remito dr ON dr.id_remito = r.id_remito
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
                # Guardar pesos que el usuario ya había ingresado (temporalmente)
                pesos_ingresados = dict(zip(
                    request.form.getlist("id_detalle[]"),
                    request.form.getlist("peso[]")
                ))

                # Insertar nuevo producto
                nuevo_id_producto = request.form.get("nuevo_id_producto")
                nueva_cantidad = request.form.get("nuevo_cantidad")
                if nuevo_id_producto and nueva_cantidad:
                    try:
                        cur.execute("SELECT id_remito FROM remitos WHERE id_pedido = %s", (id_pedido,))
                        existe = cur.fetchone()
                        cant = float(nueva_cantidad.replace(',', '.'))

                        if cant > 0 and not existe:
                            cur.execute("""
                                INSERT INTO detalle_pedido (id_pedido, id_producto, cantidad)
                                VALUES (%s, %s, %s)
                            """, (id_pedido, nuevo_id_producto, cant))
                            conn.commit()
                            flash("Producto agregado correctamente", "success")
                    except Exception as e:
                        flash(f"Error al agregar producto: {e}", "danger")

                return redirect(url_for("entregas.remito", id_pedido=id_pedido, pesos_temporales=json.dumps(pesos_ingresados)))
                

            elif accion == "guardar_peso":
                pesos = request.form.getlist("peso[]")
                id_detalles = request.form.getlist("id_detalle[]")
                for id_det, peso_str in zip(id_detalles, pesos):
                    try:
                        peso = float(peso_str.replace(",", ".")) if peso_str else None
                        cur.execute("""
                            UPDATE detalle_remito
                            SET peso = %s
                            WHERE id_detalle = %s
                        """, (peso, id_det))
                    except:
                        continue
                conn.commit()
                flash("Pesos actualizados correctamente.", "success")
                return redirect(url_for("entregas.remito", id_pedido=id_pedido))

            elif accion == "confirmar_remito":
                id_detalles = request.form.getlist("id_detalle[]")
                pesos = request.form.getlist("peso[]")

                # Obtener cliente del pedido
                cur.execute("""
                    SELECT c.id_cliente, c.nombre, c.direccion, p.fecha_entrega
                    FROM pedidos p
                    JOIN clientes c ON p.id_cliente = c.id_cliente
                    WHERE p.id_pedido = %s
                """, (id_pedido,))
                cliente = cur.fetchone()

                if not cliente:
                    flash("Pedido no encontrado", "danger")
                    return redirect(url_for("entregas.pedidos_pendientes"))

                # Obtener productos del pedido
                cur.execute("""
                    SELECT dp.id_detalle, dp.id_producto, dp.cantidad, pr.precio, pr.unidad_base
                    FROM detalle_pedido dp
                    JOIN productos pr ON dp.id_producto = pr.id_producto
                    WHERE dp.id_pedido = %s
                """, (id_pedido,))
                detalles = cur.fetchall()

                # Mapear detalle_pedido por ID para fácil acceso
                mapa_detalles = {str(d["id_detalle"]): d for d in detalles}

                total = 0
                filas_a_insertar = []

                for id_det, peso_str in zip(id_detalles, pesos):
                    det = mapa_detalles.get(id_det)
                    if not det:
                        continue

                    unidad = det["unidad_base"].lower()
                    cantidad = float(det["cantidad"])
                    precio = float(det["precio"])
                    peso = float(peso_str.replace(",", ".")) if peso_str.strip() else None

                    subtotal = peso * precio if unidad == "kg" and peso else cantidad * precio
                    total += subtotal

                    filas_a_insertar.append({
                        "id_producto": det["id_producto"],
                        "cantidad": cantidad,
                        "peso": peso,
                        "precio": precio
                    })

                # Obtener saldo anterior del cliente
                cur.execute("SELECT saldo FROM clientes_cuenta_corriente WHERE id_cliente = %s", (cliente["id_cliente"],))
                saldo_anterior = cur.fetchone()["saldo"] if cur.rowcount else 0

                # Verificar si ya existe un remito
                cur.execute("SELECT id_remito FROM remitos WHERE id_pedido = %s", (id_pedido,))
                existe = cur.fetchone()

                if existe:
                    id_remito = existe["id_remito"]
                else:
                    # Insertar remito
                    cur.execute("""
                        INSERT INTO remitos (id_pedido, total, saldo_anterior)
                        VALUES (%s, %s, %s)
                        RETURNING id_remito
                    """, (id_pedido, total, saldo_anterior))
                    id_remito = cur.fetchone()["id_remito"]

                    # Insertar detalle_remito
                    for f in filas_a_insertar:
                        cur.execute("""
                            INSERT INTO detalle_remito (id_remito, id_producto, cantidad, peso, precio)
                            VALUES (%s, %s, %s, %s, %s)
                        """, (id_remito, f["id_producto"], f["cantidad"], f["peso"], f["precio"]))

                    # Actualizar estado del pedido
                    cur.execute("UPDATE pedidos SET estado = 'preparado' WHERE id_pedido = %s", (id_pedido,))

                    # Insertar movimiento si no existe
                    cur.execute("""
                        SELECT id_movimiento FROM movimientos_cuenta_corriente 
                        WHERE id_cliente = %s AND tipo_mov = 'compra' AND importe = %s AND id_remito = %s
                    """, (cliente["id_cliente"], total, id_remito))
                    existe_mov = cur.fetchone()

                    if not existe_mov:
                        cur.execute("""
                            INSERT INTO movimientos_cuenta_corriente
                                (id_cliente, fecha, tipo_mov, importe, id_remito)
                            VALUES (%s, %s, 'compra', %s, %s)
                        """, (cliente['id_cliente'], datetime.utcnow().date(), total, id_remito))

                        cur.execute("""
                            INSERT INTO clientes_cuenta_corriente (id_cliente, saldo)
                            VALUES (%s, %s)
                            ON CONFLICT (id_cliente)
                            DO UPDATE SET saldo = clientes_cuenta_corriente.saldo + EXCLUDED.saldo
                        """, (cliente['id_cliente'], total))

                conn.commit()
                return redirect(url_for("entregas.visualizador_pdf_remito", id_remito=id_remito))


        # ---------- Datos para GET ----------
        cur.execute("SELECT id_remito FROM remitos WHERE id_pedido = %s", (id_pedido,))
        remito = cur.fetchone()
        id_remito = remito["id_remito"] if remito else None

        if id_remito:
            # Hay remito: traemos los productos reales con sus pesos definitivos
            cur.execute("""
                SELECT dr.id_detalle, pr.descripcion, dr.cantidad, dr.precio, dr.peso, pr.unidad_base
                FROM detalle_remito dr
                JOIN productos pr ON dr.id_producto = pr.id_producto
                WHERE dr.id_remito = %s
                ORDER BY pr.descripcion
            """, (id_remito,))
            detalles = cur.fetchall()

        else:
            # Aún no se generó el remito: traemos los productos del pedido
            cur.execute("""
                SELECT dp.id_detalle, pr.descripcion, dp.cantidad, pr.precio, NULL AS peso, pr.unidad_base
                FROM detalle_pedido dp
                JOIN productos pr ON dp.id_producto = pr.id_producto
                WHERE dp.id_pedido = %s
                ORDER BY pr.descripcion
            """, (id_pedido,))
            detalles = cur.fetchall()

            pesos_temporales = request.args.get("pesos_temporales")
            if pesos_temporales:
                try:
                    pesos_dict = json.loads(pesos_temporales)
                    for item in detalles:
                        id_det = str(item["id_detalle"])
                        if id_det in pesos_dict:
                            item["peso"] = pesos_dict[id_det]
                except Exception as e:
                    # Silencio, si no vienen pesos temporales válidos
                    pass

        cur.execute("""
            SELECT c.nombre AS cliente_nombre, c.telefono, p.estado, p.fecha_entrega, c.id_cliente
            FROM pedidos p
            JOIN clientes c ON p.id_cliente = c.id_cliente
            WHERE p.id_pedido = %s
        """, (id_pedido,))
        info_cliente = cur.fetchone()

        cur.execute("SELECT id_cliente, nombre FROM clientes ORDER BY nombre")
        clientes = cur.fetchall()

        cur.execute("""
            SELECT id_producto, descripcion, unidad_base, precio
            FROM productos
            WHERE id_producto NOT IN (
                SELECT id_producto
                FROM detalle_pedido
                WHERE id_pedido = %s
            )
            ORDER BY descripcion
        """, (id_pedido,))
        productos_disponibles = cur.fetchall()

        # Obtener saldo anterior de la cuenta corriente
        cur.execute("""
            SELECT saldo
            FROM clientes_cuenta_corriente
            WHERE id_cliente = %s
        """, (info_cliente["id_cliente"],))
        cuenta = cur.fetchone()
        saldo_anterior = cuenta["saldo"] if cuenta else 0
        cantidad_items = len(detalles)
        return render_template("remito_confirmar.html",
                               id_pedido=id_pedido,
                               detalles=detalles,
                               cliente_nombre=info_cliente["cliente_nombre"],
                               telefono=info_cliente["telefono"],
                               estado=info_cliente["estado"],
                               fecha_entrega=info_cliente["fecha_entrega"].strftime("%Y-%m-%d"),
                               id_cliente=info_cliente["id_cliente"],
                               clientes=clientes,
                               productos=productos_disponibles,
                               remito_generado=True,
                               fecha_hoy=date.today().strftime("%Y-%m-%d"),
                               saldo_anterior=saldo_anterior,
                               cantidad_items=cantidad_items)


@bp_entregas.route("/remito/pdf/<int:id_remito>")
def remito_pdf(id_remito):
    with get_conn() as conn, conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute("SELECT * FROM remitos WHERE id_remito = %s", (id_remito,))
        remito = cur.fetchone()
        if not remito:
            abort(404, "Remito no encontrado")

        cur.execute("""
            SELECT pr.descripcion,
                   dr.cantidad,
                   dr.peso,
                   dr.precio,
                   pr.unidad_base,
                   r.total
            FROM detalle_remito dr
            JOIN remitos r ON dr.id_remito = r.id_remito
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


    pdf_buffer = generar_pdf_remito(
        nombre_cliente=cli['nombre'],
        direccion=cli['direccion'],
        fecha_entrega=cli['fecha_entrega'],
        detalles=detalles,
        total_remito=detalles[0]['total'],
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
            SELECT cantidad, precio
            FROM detalle_remito
            WHERE id_remito = %s
        """, (id_remito,))
        detalles = cur.fetchall()

        total_remito = sum(
            Decimal(str(d['cantidad'])) * Decimal(str(d['precio']))
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

@bp_entregas.route("/api/agregar_item", methods=["POST"])
def api_agregar_item():
    id_pedido = request.form.get("nuevo_id_pedido")
    id_producto = request.form.get("nuevo_id_producto")
    cantidad = request.form.get("nuevo_cantidad")

    if not (id_pedido and id_producto and cantidad):
        return jsonify({"ok": False, "error": "Datos incompletos"})

    try:
        cantidad_float = float(cantidad.replace(",", "."))
        if cantidad_float <= 0:
            raise ValueError("Cantidad inválida")

        with get_conn() as conn, conn.cursor() as cur:
            cur.execute("""
                INSERT INTO detalle_pedido (id_pedido, id_producto, cantidad)
                VALUES (%s, %s, %s)
                RETURNING id_detalle
            """, (id_pedido, id_producto, cantidad_float))
            id_detalle = cur.fetchone()[0]
            conn.commit()

        return jsonify({"ok": True, "id_detalle": id_detalle, "id_pedido": id_pedido})

    except Exception as e:
        return jsonify({"ok": False, "error": str(e)})
