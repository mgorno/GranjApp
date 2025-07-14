from flask import Blueprint, render_template, request, redirect, url_for, flash
from models import get_conn

bp_remitos = Blueprint("remitos_generados", __name__, url_prefix="/remitos_generados")

@bp_remitos.route("/", methods=["GET"])
def lista_remitos():
    cliente = request.args.get("cliente")
    fecha = request.args.get("fecha")

    query = """
        SELECT r.id_remito, r.fecha, r.total, r.estado,
               c.nombre AS cliente, r.id_pedido
        FROM remitos r
        JOIN pedidos p ON r.id_pedido = p.id_pedido
        JOIN clientes c ON p.id_cliente = c.id_cliente
        WHERE (%(cliente)s IS NULL OR c.nombre ILIKE %(cliente_like)s)
          AND (%(fecha)s IS NULL OR DATE(r.fecha) = %(fecha)s)
        ORDER BY r.fecha DESC
    """
    params = {
        "cliente": cliente,
        "cliente_like": f"%{cliente}%" if cliente else None,
        "fecha": fecha
    }

    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(query, params)
            remitos = cur.fetchall()
            columnas = [desc[0] for desc in cur.description]

    return render_template("remitos_generados.html", remitos=remitos, columnas=columnas)


@bp_remitos.route("/entregar/<int:id_remito>")
def entregar_remito(id_remito):
    with get_conn() as conn:
        with conn.cursor() as cur:
            # Actualiza el estado del remito si está emitido
            cur.execute("""
                UPDATE remitos
                SET estado = 'entregado'
                WHERE id_remito = %s AND estado = 'emitido'
                RETURNING id_pedido;
            """, (id_remito,))
            result = cur.fetchone()
            if result:
                id_pedido = result[0]
                # También marcamos el pedido como entregado
                cur.execute("""
                    UPDATE pedidos
                    SET estado = 'entregado'
                    WHERE id_pedido = %s;
                """, (id_pedido,))
                flash("Remito marcado como entregado.")
            else:
                flash("El remito ya fue entregado o cancelado.")
    return redirect(url_for("remitos_generados.lista_remitos"))


@bp_remitos.route("/cancelar/<int:id_remito>")
def cancelar_remito(id_remito):
    with get_conn() as conn:
        with conn.cursor() as cur:
            # Solo cancelar si el remito NO está entregado
            cur.execute("""
                UPDATE remitos
                SET estado = 'cancelado'
                WHERE id_remito = %s AND estado != 'entregado'
                RETURNING id_pedido;
            """, (id_remito,))
            result = cur.fetchone()
            if result:
                id_pedido = result[0]
                # Opcional: volver el pedido a "cancelado"
                cur.execute("""
                    UPDATE pedidos
                    SET estado = 'cancelado'
                    WHERE id_pedido = %s;
                """, (id_pedido,))
                flash("Remito cancelado.")
            else:
                flash("El remito ya fue entregado y no puede cancelarse.")
    return redirect(url_for("remitos_generados.lista_remitos"))
