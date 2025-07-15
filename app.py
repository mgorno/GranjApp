import os
from flask import Flask
from flask_login import LoginManager
from models import init_db, get_conn
from routes import register_all_blueprints

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev-key")


init_db()

register_all_blueprints(app)

print("Blueprints registrados:")
for name, blueprint in app.blueprints.items():
    print(f"- {name}: {blueprint.url_prefix}")
# Configurar Flask-Login
login_manager = LoginManager()
login_manager.login_view = "auth.login" 
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT usuario FROM usuarios WHERE id_usuario = %s", (user_id,))
            row = cur.fetchone()
            if row:
                return Usuario(user_id, row[0])
    return None

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


if __name__ == "__main__":
    port  = int(os.environ.get("PORT", 5000))
    debug = os.environ.get("FLASK_DEBUG") == "1"
    app.run(host="0.0.0.0", port=port, debug=debug)
