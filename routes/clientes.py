from flask import Blueprint, render_template, request, redirect, url_for, flash
from models import get_conn
import uuid, re



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
        return redirect(url_for('clientes.lista_clientes'))

    return render_template('nuevo_cliente.html')
# routes.py
@bp_clientes.route("/")
def clientes():
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute("SELECT id_cliente, nombre, telefono FROM clientes ORDER BY nombre")
        clientes = cur.fetchall()
    return render_template("clientes.html", clientes=clientes)

@bp_clientes.route("/crear", methods=["POST"])
def crear_cliente():
    nombre     = request.form["nombre"].strip()
    telefono   = request.form["telefono"].strip()
    direccion  = request.form["direccion"].strip()
    mail       = request.form["mail"].strip()
    id_cliente = str(uuid.uuid4())

    with get_conn() as conn, conn.cursor() as cur:
        cur.execute("""
            INSERT INTO clientes (id_cliente, nombre, telefono, direccion, mail)
            VALUES (%s, %s, %s, %s, %s)
        """, (id_cliente, nombre, telefono or None, direccion or None, mail or None))
        conn.commit()

    flash("Cliente creado correctamente.", "success")
    return redirect(url_for("main.clientes"))
@bp_clientes.route("/editar/<id_cliente>", methods=["POST"])
def editar_cliente(id_cliente):
    nombre = request.form.get("nombre")
    telefono = request.form.get("telefono")
    direccion = request.form.get("direccion")
    mail = request.form.get("mail")

    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                UPDATE clientes SET nombre=%s, telefono=%s, direccion=%s, mail=%s
                WHERE id_cliente=%s
            """, (nombre, telefono, direccion, mail, id_cliente))
        conn.commit()

    flash("Cliente actualizado", "success")
    return redirect(url_for("main.lista_clientes"))  # asegurate de usar el nombre correcto

@bp_clientes.route("/borrar/<id_cliente>")
def borrar_cliente(id_cliente):
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM clientes WHERE id_cliente = %s", (id_cliente,))
        conn.commit()

    flash("Cliente eliminado", "success")
    return redirect(url_for("main.lista_clientes"))