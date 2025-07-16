from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from models import get_conn
import uuid, re
from collections import defaultdict

bp_clientes = Blueprint("clientes", __name__, url_prefix="/clientes")

# ---------------- Clientes ----------------
@bp_clientes.route("/nuevo", methods=['GET', 'POST'])
def nuevo_cliente():
    if request.method == 'POST':
        nombre = request.form.get('nombre', '').strip()
        telefono = request.form.get('telefono', '').strip()
        direccion = request.form.get('direccion', '').strip()
        mail = request.form.get('mail', '').strip()

        errores = []
        if not nombre:
            errores.append("El nombre es obligatorio.")
        if telefono and not re.fullmatch(r'\d{10,12}', telefono):
            errores.append("El teléfono debe tener solo números y entre 10 y 12 dígitos.")
        if mail and not re.fullmatch(r"[^@]+@[^@]+\.[^@]+", mail):
            errores.append("El email no es válido.")

        if errores:
            for e in errores:
                flash(e, "error")
            # Devuelvo el form con datos para que no se pierdan
            return render_template('nuevo_cliente.html',
                                   nombre=nombre,
                                   telefono=telefono,
                                   direccion=direccion,
                                   mail=mail)

        # VALIDAR SI EL CLIENTE YA EXISTE POR NOMBRE
        with get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT 1 FROM clientes WHERE LOWER(nombre) = LOWER(%s)", (nombre,))
                existe = cur.fetchone()

        if existe:
            flash(f"El cliente '{nombre}' ya existe.", "warning")
            if request.headers.get("X-Requested-With") == "XMLHttpRequest":
                return jsonify({"status": "error", "message": "Cliente ya existe"}), 400
            return redirect(url_for('clientes.clientes'))

        # SI NO EXISTE, CREAR NUEVO CLIENTE
        id_cliente = str(uuid.uuid4())
        with get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO clientes (id_cliente, nombre, telefono, direccion, mail) VALUES (%s, %s, %s, %s, %s)",
                    (id_cliente, nombre, telefono or None, direccion or None, mail or None)
                )
            conn.commit()

        flash("Cliente creado correctamente.", "success")

        # AJAX: devolver JSON. HTML normal: redirigir
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return jsonify({"status": "ok"}), 200
        else:
            return redirect(url_for('clientes.clientes'))

    return render_template('nuevo_cliente.html')


@bp_clientes.route("/")
def clientes():
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute("""
            SELECT id_cliente, nombre, telefono, direccion, mail
            FROM clientes
            ORDER BY nombre
        """)
        clientes = cur.fetchall()

    return render_template("clientes.html", clientes=clientes)


@bp_clientes.route("/editar/<id_cliente>", methods=["POST"])
def editar_cliente(id_cliente):
    nombre = request.form.get("nombre")
    telefono = request.form.get("telefono")
    direccion = request.form.get("direccion")
    mail = request.form.get("mail")
    activo = request.form.get("activo") == "true"  
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                UPDATE clientes
                SET nombre=%s, telefono=%s, direccion=%s, mail=%s, activo=%s
                WHERE id_cliente=%s
            """, (nombre, telefono, direccion, mail, activo, id_cliente))
        conn.commit()

    flash("Cliente actualizado", "success")
    return redirect(url_for("clientes.clientes"))



@bp_clientes.route("/borrar/<id_cliente>")
def borrar_cliente(id_cliente):
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT COUNT(*) FROM pedidos WHERE id_cliente = %s", (id_cliente,))
            cantidad_pedidos = cur.fetchone()[0]

            if cantidad_pedidos > 0:
                flash("No se puede eliminar el cliente porque tiene pedidos cargados.", "warning")
                return redirect(url_for("clientes.clientes"))
            cur.execute("DELETE FROM clientes WHERE id_cliente = %s", (id_cliente,))
        conn.commit()

    flash("Cliente eliminado correctamente", "success")
    return redirect(url_for("clientes.clientes"))
