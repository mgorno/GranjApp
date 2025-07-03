import os
from flask import Flask
from routes import blueprints
from models import init_db

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev-key")

# Registrar todos los blueprints
for bp in blueprints:
    app.register_blueprint(bp)

# Inicializar base de datos
init_db()

if __name__ == "__main__":
    port  = int(os.environ.get("PORT", 5000))
    debug = os.environ.get("FLASK_DEBUG") == "1"
    app.run(host="0.0.0.0", port=port, debug=debug)
