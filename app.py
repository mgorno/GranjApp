import os
from flask import Flask, redirect, url_for, request
from flask_login import LoginManager, current_user
from models import init_db, get_conn
from routes import register_all_blueprints
from routes.auth import Usuario

# Crear la app
app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev-key")

# Inicializar base de datos y registrar blueprints
init_db()
register_all_blueprints(app)

# Configurar Flask-Login
login_manager = LoginManager()
login_manager.login_view = "auth.login"  # Si no está logueado, redirige acá
login_manager.init_app(app)

# Recuperar usuario desde la base
@login_manager.user_loader
def load_user(user_id):
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT usuario, rol FROM usuarios WHERE id_usuario = %s", (user_id,))
            row = cur.fetchone()
            if row:
                return Usuario(user_id, row[0], row[1])  
    return None


# Hacer current_user disponible en los templates
@app.context_processor
def inject_user():
    return dict(current_user=current_user)

# Redirección raíz
@app.route("/")
def root():
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))
    else:
        return redirect(url_for("auth.login"))

# Filtro global: protege toda la app excepto ciertas rutas públicas
@app.before_request
def require_login():
    rutas_publicas = (
        "auth.login",
        "auth.logout",
        "auth.registrar_usuario",
        "static",  # permite acceder a CSS, JS, imágenes, etc.
    )

    endpoint = request.endpoint or ""
    if any(endpoint.startswith(r) for r in rutas_publicas):
        return  # permitir acceso

    if not current_user.is_authenticated:
        return redirect(url_for("auth.login"))

# Filtros Jinja para formato
def formato_cantidad(n):
    try:
        n = float(n)
        return str(int(n)) if n == int(n) else f"{n:.3f}".rstrip("0").replace(".", ",")
    except (ValueError, TypeError):
        return "0"

def formato_precio(n):
    try:
        n = float(n)
        return f"${int(n)}" if n == int(n) else f"${n:.2f}".rstrip("0").rstrip(".")
    except (ValueError, TypeError):
        return "$0"

def formato_precio_sin_signo(n):
    try:
        n = float(n)
        return f"{int(n)}" if n == int(n) else f"{n:.2f}".rstrip("0").rstrip(".")
    except (ValueError, TypeError):
        return "0"

def formato_precio_arg(value):
    try:
        s = f"${int(value):,}"
        return s.replace(",", ".")
    except (ValueError, TypeError):
        return "$0"

app.jinja_env.filters["formato_cantidad"] = formato_cantidad
app.jinja_env.filters["formato_precio"] = formato_precio
app.jinja_env.filters["formato_precio_sin_signo"] = formato_precio_sin_signo
app.jinja_env.filters["formato_precio_arg"] = formato_precio_arg

# Ejecutar en modo local
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    debug = os.environ.get("FLASK_DEBUG") == "1"
    app.run(host="0.0.0.0", port=port, debug=debug)
