from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, UserMixin, login_required, current_user
from werkzeug.security import check_password_hash, generate_password_hash
from models import get_conn
import uuid

auth = Blueprint("auth", __name__)

class Usuario(UserMixin):
    def __init__(self, id_usuario, usuario, rol):
        self.id = id_usuario
        self.usuario = usuario
        self.rol = rol

@auth.route("/auth/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        usuario = request.form["usuario"]
        clave = request.form["clave"]

        with get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT id_usuario, clave_hash, rol FROM usuarios WHERE usuario = %s", (usuario,))
                row = cur.fetchone()

        if row and check_password_hash(row[1], clave):
            user = Usuario(row[0], usuario, row[2])
            login_user(user)
            flash("Ingreso exitoso.", "success")
            return redirect(url_for("main.index"))
        else:
            flash("Usuario o clave incorrectos.", "danger")

    return render_template("login.html")

@auth.route("/auth/logout")
def logout():
    logout_user()
    flash("Sesión cerrada.", "info")
    return redirect(url_for("auth.login"))

@auth.route("/registrar_usuario", methods=["POST"])
@login_required
def registrar_usuario():
    if current_user.rol != "admin":
        flash("Acceso denegado.", "danger")
        return redirect(url_for("main.index"))

    usuario = request.form["usuario"]
    clave = request.form["clave"]
    rol = request.form["rol"]
    nombre = request.form.get("nombre", usuario)

    clave_hash = generate_password_hash(clave)
    nuevo_id = str(uuid.uuid4())

    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT id_usuario FROM usuarios WHERE usuario = %s", (usuario,))
            if cur.fetchone():
                flash("El usuario ya existe.", "warning")
                return redirect(url_for("auth.listar_usuarios"))

            cur.execute(
                "INSERT INTO usuarios (id_usuario, nombre, usuario, clave_hash, rol) VALUES (%s, %s, %s, %s, %s)",
                (nuevo_id, nombre, usuario, clave_hash, rol)
            )
            conn.commit()
            flash("Usuario registrado correctamente.", "success")
            return redirect(url_for("auth.listar_usuarios"))

@auth.route("/usuarios")
@login_required
def listar_usuarios():
    if current_user.rol != "admin":
        flash("Acceso denegado.", "danger")
        return redirect(url_for("main.index"))

    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT id_usuario, nombre, usuario, rol FROM usuarios ORDER BY usuario")
            usuarios = [dict(id_usuario=u[0], nombre=u[1], usuario=u[2], rol=u[3]) for u in cur.fetchall()]

    return render_template("usuarios.html", usuarios=usuarios)

@auth.route("/usuarios/eliminar/<id_usuario>", methods=["POST"])
@login_required
def eliminar_usuario(id_usuario):
    if current_user.rol != "admin":
        flash("Acceso denegado.", "danger")
        return redirect(url_for("main.index"))

    if current_user.id == id_usuario:
        flash("No podés eliminar tu propio usuario Rey.", "warning")
        return redirect(url_for("auth.listar_usuarios"))

    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM usuarios WHERE id_usuario = %s", (id_usuario,))
            conn.commit()
            flash("Usuario eliminado correctamente.", "success")

    return redirect(url_for("auth.listar_usuarios"))

@auth.route("/usuarios/cambiar_clave", methods=["GET", "POST"])
@login_required
def cambiar_clave():
    if request.method == "POST":
        clave_actual = request.form["clave_actual"]
        nueva_clave = request.form["nueva_clave"]
        confirmar_clave = request.form["confirmar_clave"]

        if nueva_clave != confirmar_clave:
            flash("La nueva contraseña no coincide con la confirmación.", "danger")
            return redirect(url_for("auth.cambiar_clave"))

        with get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT clave_hash FROM usuarios WHERE id_usuario = %s", (current_user.id,))
                row = cur.fetchone()

                if not row or not check_password_hash(row[0], clave_actual):
                    flash("La contraseña actual no es correcta.", "danger")
                    return redirect(url_for("auth.cambiar_clave"))

                nueva_hash = generate_password_hash(nueva_clave)
                cur.execute("UPDATE usuarios SET clave_hash = %s WHERE id_usuario = %s", (nueva_hash, current_user.id))
                conn.commit()

        flash("Contraseña actualizada exitosamente.", "success")
        return redirect(url_for("main.index"))

    return render_template("cambiar_clave.html")
