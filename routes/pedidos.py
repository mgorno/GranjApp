from flask import Blueprint, render_template, request, redirect, url_for, flash
from models import get_conn
import uuid
from datetime import date

bp_pedidos = Blueprint("pedidos", __name__, url_prefix="/pedidos")



@bp_pedidos.route("/nuevo", methods=["GET", "POST"])
def nuevo():
    hoy = date.today().isoformat()

    if request.method == "POST":
        try:
            with get_conn() as conn, conn.cursor() as cur:
                id_cliente = request.form["id_cliente"]
                fecha_entrega = request.form["fecha_entrega"]

                # Verificar si ya hay un pedido pendiente
                cur.execute("""
                    SELECT id_pedido FROM pedidos 
                    WHERE id_cliente = %s AND DATE(fecha_entrega) = %s AND TRIM(LOWER(estado)) = 'pendiente'
                """, (id_cliente, fecha_entrega))
                existe = cur.fetchone()

                if existe:
                    flash("Ya existe un pedido pendiente para este cliente en esa fecha.", "error")
                    clientes = obtener_clientes(cur)
                    productos = obtener_productos(cur)
                    return render_template("nuevo_pedido.html", clientes=clientes, productos=productos, fecha_hoy=hoy)

                id_pedido = str(uuid.uuid4())

                # Insertar cabecera
                cur.execute("""
                    INSERT INTO pedidos (id_pedido, id_cliente, fecha_entrega, estado)
                    VALUES (%s, %s, %s, 'pendiente')
                """, (id_pedido, id_cliente, fecha_entrega))

                # Insertar detalle
                ids_producto = request.form.getlist("id_producto")
                cantidades = request.form.getlist("cantidad")
                precios = request.form.getlist("precio")
                unidades = request.form.getlist("unidad")

                detalles_insertados = 0
                for i in range(len(ids_producto)):
                    if ids_producto[i] and cantidades[i]:
                        cur.execute("""
                            INSERT INTO detalle_pedido (id_pedido, id_producto, cantidad, precio, unidad)
                            VALUES (%s, %s, %s, %s, %s)
                        """, (
                            id_pedido,
                            ids_producto[i],
                            float(cantidades[i].replace(",", ".")),
                            float(precios[i].replace(",", ".")) if precios[i] else 0,
                            unidades[i]
                        ))
                        detalles_insertados += 1

                if detalles_insertados == 0:
                    conn.rollback()
                    flash("No se agregó ningún producto al pedido.", "error")
                    clientes = obtener_clientes(cur)
                    productos = obtener_productos(cur, excluir_ids=ids_producto)
                    return render_template("nuevo_pedido.html", clientes=clientes, productos=productos, fecha_hoy=hoy)

                conn.commit()
                flash("Pedido creado correctamente.", "success")
                return redirect(url_for("pedidos.nuevo"))

        except Exception as e:
            conn.rollback()
            flash(f"Ocurrió un error al crear el pedido: {e}", "danger")
            with get_conn() as conn, conn.cursor() as cur:
                clientes = obtener_clientes(cur)
                productos = obtener_productos(cur)
            return render_template("nuevo_pedido.html", clientes=clientes, productos=productos, fecha_hoy=hoy)

    # Si es GET
    with get_conn() as conn, conn.cursor() as cur:
        clientes = obtener_clientes(cur)
        productos = obtener_productos(cur)
    return render_template("nuevo_pedido.html", clientes=clientes, productos=productos, fecha_hoy=hoy)


def obtener_clientes(cur):
    cur.execute("SELECT id_cliente, nombre FROM clientes WHERE activo is true ORDER BY nombre")
    return cur.fetchall()


def obtener_productos(cur, excluir_ids=None):
    query = "SELECT id_producto, descripcion, precio, unidad_base FROM productos"
    params = []

    if excluir_ids:
        placeholders = ','.join(['%s'] * len(excluir_ids))
        query += f" WHERE id_producto NOT IN ({placeholders})"
        params.extend(excluir_ids)

    query += " ORDER BY descripcion"
    cur.execute(query, params)
    return cur.fetchall()


@bp_pedidos.route("/eliminar/<id_pedido>", methods=["POST", "GET"])
def eliminar(id_pedido):
    """
    Borra un pedido y sus líneas de detalle.
    Si preferís “marcar borrado” en lugar de borrar físicamente,
    cambiá el DELETE por un UPDATE de estado.
    """
    with get_conn() as conn, conn.cursor() as cur:
        # Primero borro las líneas para respetar la FK
        cur.execute("DELETE FROM detalle_pedido WHERE id_pedido = %s", (id_pedido,))
        # Luego la cabecera
        cur.execute("DELETE FROM pedidos WHERE id_pedido = %s", (id_pedido,))
        conn.commit()

    flash("Pedido eliminado correctamente.", "success")
    return redirect(url_for("pedidos.nuevo"))
