from flask import Flask
from routes import bp
from models import init_db

app = Flask(__name__)
app.secret_key = 'esto-es-secreto-y-unico'
app.register_blueprint(bp)

if __name__ == "__main__":
    init_db()
    app.run(debug=True, host="0.0.0.0", port=5000)
