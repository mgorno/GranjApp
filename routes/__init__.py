from flask import Blueprint

bp = Blueprint('root', __name__)

def register_all_blueprints(app):
    from .clientes import bp_clientes
    from .main import bp_main
    from .pagos import bp_pagos
    from .pedidos import bp_pedidos
    from .productos import bp_productos

    app.register_blueprint(bp_clientes)
    app.register_blueprint(bp_main)
    app.register_blueprint(bp_pagos)
    app.register_blueprint(bp_pedidos)
    app.register_blueprint(bp_productos)
    app.register_blueprint(bp)
    
