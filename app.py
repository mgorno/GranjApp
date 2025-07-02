import os
from flask import Flask
from routes import bp
from models import init_db

app = Flask(__name__)

# 1) Clave secreta segura
app.secret_key = os.environ.get("SECRET_KEY", "dev-key")

# Blueprint con todas tus rutas
app.register_blueprint(bp)

# 2) Crear tablas al arrancar
init_db()

if __name__ == "__main__":
    # 3) Puerto y debug según variables de entorno
    port   = int(os.environ.get("PORT", 5000))
    debug  = os.environ.get("FLASK_DEBUG") == "1"
    app.run(host="0.0.0.0", port=port, debug=debug)
