from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user
from werkzeug.security import check_password_hash
from models import get_conn
from flask_login import UserMixin

auth = Blueprint("auth", __name__)

class Usuario(UserMixin):
    def __init__(self, id_usuario, usuario):
        self.id = id_usuario
        self.usuario = usuario

@auth.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        usuario = request.form["usuario"]
        clave = request.form["clave"]

        with get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT id_usuario, clave_hash FROM usuarios WHERE usuario = %s", (usuario,))
                row = cur.fetchone()

        if row and check_password_hash(row[1], clave):
            user = Usuario(row[0], usuario)
            login_user(user)
            flash("Ingreso exitoso.")
            return redirect(url_for("remitos_generados.lista_remitos"))
        else:
            flash("Usuario o clave incorrectos.")

    return render_template("login.html")

@auth.route("/logout")
def logout():
    logout_user()
    flash("Sesión cerrada.")
    return redirect(url_for("auth.login"))
