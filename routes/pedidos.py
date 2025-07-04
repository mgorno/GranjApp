from flask import Blueprint, render_template, request, redirect, url_for, flash
from models import get_conn
import uuid

bp_pedidos = Blueprint("pedidos", __name__, url_prefix="/pedidos")

@bp_pedidos.route("/pendientes")
def pendientes():
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute("""
            SELECT p.id_pedido, c.nombre, p.fecha_pedido 
            FROM pedidos p 
            JOIN clientes c ON c.id_cliente = p.id_cliente 
            WHERE p.estado = 'pendiente' 
            ORDER BY p.fecha_pedido DESC
        """)
        pedidos = cur.fetchall()
    return render_template("pendientes.html", pedidos=pedidos)

@bp_pedidos.route("/nuevo", methods=["GET", "POST"])
def nuevo():
    with get_conn() as conn, conn.cursor() as cur:
        if request.method == "POST":
            id_cliente = request.form["id_cliente"]
            fecha_entrega = request.form["fecha_entrega"]

            # Verificar si ya hay un pedido pendiente
            cur.execute("""
                SELECT id_pedido FROM pedidos 
                WHERE id_cliente = %s AND DATE(fecha_entrega) = %s AND estado = 'pendiente'
            """, (id_cliente, fecha_entrega))
            existe = cur.fetchone()

            if existe:
                flash("Ya existe un pedido pendiente para este cliente en esa fecha.", "error")
                clientes, productos = obtener_clientes_productos(cur)
                return render_template("nuevo_pedido.html", clientes=clientes, productos=productos)

            id_pedido = str(uuid.uuid4())

            # Insertar cabecera del pedido
            cur.execute("""
                INSERT INTO pedidos (id_pedido, id_cliente, fecha_entrega, estado)
                VALUES (%s, %s, %s, 'pendiente')
            """, (id_pedido, id_cliente, fecha_entrega))

            # Insertar detalle
            ids_producto = request.form.getlist("id_producto")
            cantidades = request.form.getlist("cantidad")
            precios = request.form.getlist("precio")
            unidades = request.form.getlist("unidad")

            for i in range(len(ids_producto)):
                cur.execute("""
                    INSERT INTO detalle_pedido (id_pedido, id_producto, cantidad, precio, unidad)
                    VALUES (%s, %s, %s, %s, %s)
                """, (id_pedido, ids_producto[i], cantidades[i], precios[i], unidades[i]))

            conn.commit()
            flash("Pedido creado correctamente.", "success")
            return redirect(url_for("pedidos.pendientes"))

        # Si es GET
        with get_conn() as conn, conn.cursor() as cur:
            clientes, productos = obtener_clientes_productos(cur)
        return render_template("nuevo_pedido.html", clientes=clientes, productos=productos)

def obtener_clientes_productos(cur):
    cur.execute("SELECT id_cliente, nombre FROM clientes ORDER BY nombre")
    clientes = cur.fetchall()
    cur.execute("SELECT id_producto, descripcion, precio, unidad_base FROM productos ORDER BY descripcion")
    productos = cur.fetchall()
    return clientes, productos
    

@bp_pedidos.route("/marcar_entregado/<id_pedido>")
def marcar_entregado(id_pedido):
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute("""
            UPDATE pedidos SET estado = 'entregado' WHERE id_pedido = %s
        """, (id_pedido,))
        conn.commit()
    flash("Pedido marcado como entregado.", "success")
    return redirect(url_for('pedidos.pendientes'))

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
    return redirect(url_for("pedidos.pendientes"))
