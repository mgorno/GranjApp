from .main import bp_main
from .clientes import bp_clientes
from .pedidos import bp_pedidos
from .pagos import bp_pagos
from .productos import bp_productos
from models import get_conn


# Podés crear una lista si querés iterar
blueprints = [bp_main, bp_clientes, bp_pedidos, bp_pagos, bp_productos]
