from flask import Flask
from flask_login import LoginManager
from .auth import Usuario
from models import get_conn

# Importá y registrá todos los blueprints acá
def register_all_blueprints(app):
    from .clientes import bp_clientes
    from .main import bp_main
    from .pagos import bp_pagos
    from .pedidos import bp_pedidos
    from .productos import bp_productos
    from .cuenta_corriente import bp_cuenta_corriente
    from .remitos_generados import bp_remitos_generados
    from .entregas import bp_entregas
    from .auth import auth

    app.register_blueprint(bp_clientes, url_prefix="/clientes")
    app.register_blueprint(bp_main)
    app.register_blueprint(bp_pagos)
    app.register_blueprint(bp_pedidos)
    app.register_blueprint(bp_productos)
    app.register_blueprint(bp_cuenta_corriente)
    app.register_blueprint(bp_remitos_generados)
    app.register_blueprint(bp_entregas)
    app.register_blueprint(auth)


