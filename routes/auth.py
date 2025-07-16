from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, UserMixin
from werkzeug.security import check_password_hash, generate_password_hash
from models import get_conn
import uuid

auth = Blueprint("auth", __name__)

class Usuario(UserMixin):
    def __init__(self, id_usuario, usuario, rol):
        self.id = id_usuario
        self.usuario = usuario
        self.usuario_rol = rol

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

@auth.route("/registrar_usuario", methods=["GET", "POST"])
def registrar_usuario():
    if request.method == "POST":
        usuario = request.form["usuario"]
        clave = request.form["clave"]
        rol = request.form["rol"]

        clave_hash = generate_password_hash(clave)
        nuevo_id = str(uuid.uuid4())

        with get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT id_usuario FROM usuarios WHERE usuario = %s", (usuario,))
                if cur.fetchone():
                    flash("El usuario ya existe.")
                    return redirect(url_for("auth.registrar_usuario"))

                cur.execute(
                    "INSERT INTO usuarios (id_usuario, nombre, usuario, clave_hash, rol) VALUES (%s, %s, %s, %s, %s)",
                    (nuevo_id, usuario, usuario, clave_hash, rol)
                )
                conn.commit()
                flash("Usuario registrado correctamente.")
                return redirect(url_for("auth.login"))

    return render_template("registrar_usuario.html")