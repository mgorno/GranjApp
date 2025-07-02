from flask import Blueprint, render_template, request, redirect, url_for, flash
from models import get_conn
from datetime import datetime
import uuid
import re

bp = Blueprint('main', __name__)

# ---------------- Inicio ----------------
@bp.route("/")
def index():
    return render_template("index.html")

# ---------------- Clientes ----------------
@bp.route("/clientes/nuevo", methods=['GET', 'POST'])
def nuevo_cliente():
    if request.method == 'POST':
        nombre = request.form.get('nombre', '').strip()
        telefono = request.form.get('telefono', '').strip()
        direccion = request.form.get('direccion', '').strip()
        mail = request.form.get('mail', '').strip()

        errores = []
        if not nombre:
            errores.append("El nombre es obligatorio.")
        if telefono and not re.fullmatch(r'\d{6,15}', telefono):
            errores.append("El teléfono debe tener solo números y entre 6 y 15 dígitos.")
        if mail and not re.fullmatch(r"[^@]+@[^@]+\.[^@]+", mail):
            errores.append("El email no es válido.")

        if errores:
            for e in errores:
                flash(e, "error")
            return render_template('nuevo_cliente.html',
                                   nombre=nombre,
                                   telefono=telefono,
                                   direccion=direccion,
                                   mail=mail)

        id_cliente = str(uuid.uuid4())

        with get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO clientes (id_cliente, nombre, telefono, direccion, mail) VALUES (%s, %s, %s, %s, %s)",
                    (id_cliente, nombre, telefono or None, direccion or None, mail or None)
                )
            conn.commit()

        flash("Cliente creado correctamente.", "success")
        return redirect(url_for('main.nuevo_cliente'))

    return render_template('nuevo_cliente.html')

# ---------------- Pedidos ----------------
@bp.route("/pendientes")
def pendientes():
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT p.id_pedido, c.nombre, p.fecha_pedido "
                "FROM pedidos p JOIN clientes c ON c.id_cliente = p.id_cliente "
                "WHERE p.estado = 'pendiente' ORDER BY p.fecha_pedido DESC"
            )
            pedidos = cur.fetchall()
    return render_template("pendientes.html", pedidos=pedidos)

@bp.route("/nuevo", methods=['GET','POST'])
def nuevo():
    with get_conn() as conn:
        with conn.cursor() as cur:
            if request.method == 'POST':
                id_pedido = str(uuid.uuid4())
                cur.execute(
                    "INSERT INTO pedidos (id_pedido, id_cliente, fecha_entrega) VALUES (%s, %s, %s)",
                    (
                        id_pedido,
                        request.form['id_cliente'],
                        request.form['fecha_entrega']
                    )
                )
                conn.commit()
                return redirect(url_for('main.pendientes'))

            cur.execute("SELECT id_cliente, nombre FROM clientes")
            clientes = cur.fetchall()
    return render_template("nuevo_pedido.html", clientes=clientes)

@bp.route("/marcar_entregado/<id_pedido>")
def marcar_entregado(id_pedido):
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "UPDATE pedidos SET estado = 'entregado', fecha_entrega = NOW() WHERE id_pedido = %s",
                (id_pedido,)
            )
        conn.commit()
    return redirect(url_for('main.pendientes'))

# ---------------- Pagos ----------------
@bp.route("/pagos", methods=['GET','POST'])
def pagos():
    with get_conn() as conn:
        with conn.cursor() as cur:
            if request.method == 'POST':
                cur.execute(
                    "INSERT INTO pagos (id_cliente, monto_pagado, medio_pago, observaciones) VALUES (%s, %s, %s, %s)",
                    (
                        request.form['id_cliente'],
                        request.form['monto_pagado'],
                        request.form['medio_pago'],
                        request.form.get('observaciones')
                    )
                )
                conn.commit()
                return redirect(url_for('main.pagos'))

            cur.execute(
                "SELECT pg.id_pago, c.nombre, pg.monto_pagado, pg.fecha_pago, pg.medio_pago "
                "FROM pagos pg JOIN clientes c ON c.id_cliente = pg.id_cliente "
                "ORDER BY pg.fecha_pago DESC"
            )
            pagos = cur.fetchall()

            cur.execute("SELECT id_cliente, nombre FROM clientes")
            clientes = cur.fetchall()

    return render_template("pagos.html", pagos=pagos, clientes=clientes)
