from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, UserMixin
from werkzeug.security import check_password_hash, generate_password_hash
from models import get_conn

# Aquí quitamos url_prefix para poder hacer rutas sin /auth
auth = Blueprint("auth", __name__)  

class Usuario(UserMixin):
    def __init__(self, id_usuario, usuario):
        self.id = id_usuario
        self.usuario = usuario

def es_hash_valido(hash_str):
    return isinstance(hash_str, str) and any(hash_str.startswith(prefix) for prefix in ("pbkdf2:", "sha256:", "bcrypt:", "scrypt:"))

@auth.route("/auth/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        usuario = request.form["usuario"]
        clave = request.form["clave"]

        with get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT id_usuario, clave_hash FROM usuarios WHERE usuario = %s", (usuario,))
                row = cur.fetchone()

        if row and es_hash_valido(row[1]) and check_password_hash(row[1], clave):
            user = Usuario(row[0], usuario)
            login_user(user)
            flash("Ingreso exitoso.")
            return redirect(url_for("remitos_generados.lista_remitos"))
        else:
            flash("Usuario o clave incorrectos.")

    return render_template("login.html")

@auth.route("/auth/logout")
def logout():
    logout_user()
    flash("Sesión cerrada.")
    return redirect(url_for("auth.login"))


@auth.route("/registrar_usuario", methods=["GET", "POST"])
def registrar_usuario():
    if request.method == "POST":
        usuario = request.form["usuario"]
        clave = request.form["clave"]

        clave_hash = generate_password_hash(clave)

        with get_conn() as conn:
            with conn.cursor() as cur:
                # Verificar si ya existe el usuario
                cur.execute("SELECT id_usuario FROM usuarios WHERE usuario = %s", (usuario,))
                if cur.fetchone():
                    flash("El usuario ya existe.")
                    return redirect(url_for("auth.registrar_usuario"))

                # Insertar nuevo usuario
                cur.execute("INSERT INTO usuarios (usuario, clave_hash) VALUES (%s, %s)", (usuario, clave_hash))
                conn.commit()
                flash("Usuario registrado correctamente. Ingresá con tus credenciales.")
                return redirect(url_for("auth.login"))

    return render_template("registrar_usuario.html")
