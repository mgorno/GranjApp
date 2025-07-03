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
                cur.execute("SELECT id_cliente, nombre FROM clientes")
                clientes = cur.fetchall()
                cur.execute("SELECT id_producto, descripcion, precio FROM productos ORDER BY descripcion")
                productos = cur.fetchall()
                return render_template("nuevo_pedido.html", clientes=clientes, productos=productos)

            id_pedido = str(uuid.uuid4())
            cur.execute("""
                INSERT INTO pedidos (id_pedido, id_cliente, fecha_entrega)
                VALUES (%s, %s, %s)
            """, (id_pedido, id_cliente, fecha_entrega))

            conn.commit()
            flash("Pedido creado correctamente.", "success")
            return redirect(url_for("pedidos.pendientes"))

        cur.execute("SELECT id_cliente, nombre FROM clientes")
        clientes = cur.fetchall()
        cur.execute("SELECT id_producto, descripcion, precio FROM productos ORDER BY descripcion")
        productos = cur.fetchall()

    return render_template("nuevo_pedido.html", clientes=clientes, productos=productos)

@bp_pedidos.route("/marcar_entregado/<id_pedido>")
def marcar_entregado(id_pedido):
    # lógica para marcar pedido entregado
    ...
    return redirect(url_for('pedidos.pendientes'))