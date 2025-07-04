from flask import Blueprint, render_template, request, redirect, url_for
from models import get_conn

bp_main = Blueprint("main", __name__)

@bp_main.route("/")
def index():
    return render_template("index.html")

@bp_main.route("/nuevo")
def redirigir_a_formulario():
    tipo = request.args.get("tipo")

    destinos = {
        "cliente": "clientes.clientes",
        "producto": "productos.productos",
        "pedido": "pedidos.nuevo_pedido",
        "pago": "pagos.pagos",
    }

    if tipo in destinos:
        return redirect(url_for(destinos[tipo]))
    else:
        return (
            f"Tipo inválido: {tipo}. Usá uno de: {', '.join(destinos.keys())}",
            400
        )

