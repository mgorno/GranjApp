import os
from flask import Flask
from models import init_db
from routes import register_all_blueprints
from models import init_db 
app = Flask(__name__)
init_db()
app.secret_key = os.environ.get("SECRET_KEY", "dev-key")
register_all_blueprints(app) 

if __name__ == "__main__":
    port  = int(os.environ.get("PORT", 5000))
    debug = os.environ.get("FLASK_DEBUG") == "1"
    app.run(host="0.0.0.0", port=port, debug=debug)
