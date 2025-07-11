from flask import Blueprint, render_template, request
from models import get_conn

bp_cuenta_corriente = Blueprint("cuenta_corriente", __name__, url_prefix="/cuenta_corriente")

@bp_cuenta_corriente.route("/", methods=["GET"])
def cuenta_corriente():
    # Acá obtenés el parámetro 'cliente' que viene del formulario (select name="cliente")
    cliente_id = request.args.get("cliente")  
    fecha_desde = request.args.get("desde")
    fecha_hasta = request.args.get("hasta")

    query = """
        SELECT 
            m.id_movimiento,
            c.nombre,
            m.fecha,
            m.tipo_mov,
            m.importe,
            m.forma_pago
        FROM movimientos_cuenta_corriente m
        LEFT JOIN clientes c ON c.id_cliente = m.id_cliente
        WHERE 1=1
    """
    params = []

    if cliente_id:
        query += " AND m.id_cliente = %s"
        params.append(cliente_id)
    if fecha_desde:
        query += " AND m.fecha >= %s"
        params.append(fecha_desde)
    if fecha_hasta:
        query += " AND m.fecha <= %s"
        params.append(fecha_hasta)

    query += " ORDER BY m.fecha DESC"

    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(query, tuple(params))
            movimientos = cur.fetchall()

            # También necesitás la lista de clientes para el select
            cur.execute("SELECT id_cliente, nombre FROM clientes ORDER BY nombre")
            clientes = cur.fetchall()

    # Finalmente le pasás movimientos y clientes a la plantilla
    return render_template("cuenta_corriente.html", movimientos=movimientos, clientes=clientes)
