from flask import Blueprint

bp = Blueprint('root', __name__)

def register_all_blueprints(app):
    from .clientes import bp_clientes
    from .main import bp_main
    from .pagos import bp_pagos
    from .pedidos import bp_pedidos
    from .productos import bp_productos
    from .entregas import bp_entregas  
    from .cuenta_corriente import bp_cuenta_corriente
    from .remitos_generados import bp_remitos_generados
    from .auth import auth

    app.register_blueprint(bp_clientes, url_prefix='/clientes')
    app.register_blueprint(bp_main)
    app.register_blueprint(bp_pagos, url_prefix='/pagos')
    app.register_blueprint(bp_pedidos, url_prefix='/pedidos')
    app.register_blueprint(bp_productos, url_prefix='/productos')
    app.register_blueprint(bp_entregas, url_prefix='/entregas') 
    app.register_blueprint(bp_cuenta_corriente, url_prefix='/cuenta_corriente') 
    app.register_blueprint(bp_remitos_generados, url_prefix='/remitos_generados') 
    app.register_blueprint(auth)
    app.register_blueprint(bp)
