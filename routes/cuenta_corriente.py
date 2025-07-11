from flask import Blueprint, render_template, request
from models import get_conn

bp_cuenta_corriente = Blueprint("cuenta_corriente", __name__, url_prefix="/cuenta_corriente")

@bp_cuenta_corriente.route("/", methods=["GET"])
def cuenta_corriente():
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

    with get_conn() as conn, conn.cursor() as cur:
        # Movimientos filtrados
        cur.execute(query, tuple(params))
        movimientos = cur.fetchall()

        # Lista de clientes para el filtro
        cur.execute("SELECT id_cliente, nombre FROM clientes ORDER BY nombre")
        clientes = cur.fetchall()

        # Traer saldo actual del cliente si se seleccionó uno
        if cliente_id:
            cur.execute("SELECT saldo FROM clientes_cuenta_corriente WHERE id_cliente = %s", (cliente_id,))
            row = cur.fetchone()
            saldo_actual = row[0] if row and row[0] is not None else 0
        else:
            saldo_actual = 0

    return render_template("cuenta_corriente.html", movimientos=movimientos, clientes=clientes, saldo_actual=saldo_actual)
