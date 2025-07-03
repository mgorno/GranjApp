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

@bp.route("/nuevo", methods=['GET', 'POST'])
def nuevo():
    with get_conn() as conn:
        with conn.cursor() as cur:
            if request.method == 'POST':
                id_cliente = request.form['id_cliente']
                fecha_entrega = request.form['fecha_entrega']

                # Verificar si ya hay un pedido pendiente
                cur.execute("""
                    SELECT id_pedido FROM pedidos 
                    WHERE id_cliente = %s 
                      AND DATE(fecha_entrega) = %s
                      AND estado = 'pendiente'
                """, (id_cliente, fecha_entrega))
                existe = cur.fetchone()

                if existe:
                    flash("Ya existe un pedido pendiente para este cliente en esa fecha.", "error")
                    # Traer clientes y productos para rearmar el formulario
                    cur.execute("SELECT id_cliente, nombre FROM clientes")
                    clientes = cur.fetchall()
                    cur.execute("SELECT id_producto, descripcion, precio FROM productos ORDER BY descripcion")
                    productos = cur.fetchall()
                    return render_template("nuevo_pedido.html", clientes=clientes, productos=productos)

                # Crear el pedido (solo cabecera por ahora)
                id_pedido = str(uuid.uuid4())
                cur.execute("""
                    INSERT INTO pedidos (id_pedido, id_cliente, fecha_entrega)
                    VALUES (%s, %s, %s)
                """, (id_pedido, id_cliente, fecha_entrega))

                # Acá podés insertar los productos si querés desde el mismo formulario (ver abajo)
                # pero ahora solo redirigís
                conn.commit()
                flash("Pedido creado correctamente.", "success")
                return redirect(url_for('main.pendientes'))

            # GET: mostrar formulario
            cur.execute("SELECT id_cliente, nombre FROM clientes")
            clientes = cur.fetchall()
            cur.execute("SELECT id_producto, descripcion, precio FROM productos ORDER BY descripcion")
            productos = cur.fetchall()

    return render_template("nuevo_pedido.html", clientes=clientes, productos=productos)
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


# ---------------- Productos ----------------
@bp.route("/productos/nuevo", methods=['GET', 'POST'])
def nuevo_producto():
    if request.method == 'POST':
        descripcion = request.form.get('descripcion', '').strip()
        unidad_base = request.form.get('unidad_base', '').strip()
        precio = request.form.get('precio', '').strip()

        errores = []
        if not descripcion:
            errores.append("La descripción es obligatoria.")
        if not unidad_base:
            errores.append("La unidad base es obligatoria.")
        if not precio or not re.fullmatch(r'^\d+(\.\d{1,2})?$', precio):
            errores.append("El precio debe ser un número válido.")

        if errores:
            for e in errores:
                flash(e, "error")
            return render_template('nuevo_producto.html',
                                   descripcion=descripcion,
                                   unidad_base=unidad_base,
                                   precio=precio)

        id_producto = str(uuid.uuid4())
        with get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO productos (id_producto, descripcion, unidad_base, precio) VALUES (%s, %s, %s, %s)",
                    (id_producto, descripcion, unidad_base, float(precio))
                )
            conn.commit()
        flash("Producto creado correctamente.", "success")
        return redirect(url_for('main.nuevo_producto'))

    return render_template('nuevo_producto.html')
