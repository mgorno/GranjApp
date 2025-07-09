import os
from flask import Flask
from models import init_db
from routes import register_all_blueprints

app = Flask(__name__)
init_db()
app.secret_key = os.environ.get("SECRET_KEY", "dev-key")
register_all_blueprints(app)
for rule in app.url_map.iter_rules():
    print(rule.endpoint, "->", rule)
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
        return f"{int(n)}" if n == int(n) else f"${n:.2f}".rstrip("0").rstrip(".")
    except (ValueError, TypeError):
        return "$0"    

def formato_precio_arg(value):
    s = f"${int(value):,}"
    return s.replace(",", ".")      
  

app.jinja_env.filters["formato_cantidad"] = formato_cantidad
app.jinja_env.filters["formato_precio"] = formato_precio
app.jinja_env.filters["formato_precio_sin_signo"] = formato_precio_sin_signo
app.jinja_env.filters["formato_precio_arg"] = formato_precio_arg

if __name__ == "__main__":
    port  = int(os.environ.get("PORT", 5000))
    debug = os.environ.get("FLASK_DEBUG") == "1"
    app.run(host="0.0.0.0", port=port, debug=debug)
