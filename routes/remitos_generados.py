from flask import Blueprint, render_template, request, redirect, url_for, flash
from models import get_conn
from decoradores import login_requerido, rol_requerido

bp_remitos_generados = Blueprint("remitos_generados", __name__, url_prefix="/remitos_generados")

@bp_remitos_generados.route("/", methods=["GET"])
@login_requerido
@rol_requerido("admin", "empleado")
def lista_remitos():
    cliente = request.args.get("cliente")
    fecha = request.args.get("fecha")

    if cliente == "":
        cliente = None
    if fecha == "":
        fecha = None

    query = """
        SELECT r.id_remito, r.fecha, r.total, r.estado,
               c.nombre AS cliente, r.id_pedido
        FROM remitos r
        JOIN pedidos p ON r.id_pedido = p.id_pedido
        JOIN clientes c ON p.id_cliente = c.id_cliente
        WHERE (%(cliente)s IS NULL OR c.id_cliente = %(cliente)s)
          AND (%(fecha)s IS NULL OR DATE(r.fecha) = %(fecha)s)
        ORDER BY r.fecha DESC
    """
    params = {
        "cliente": cliente,
        "fecha": fecha
    }

    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT id_cliente, nombre FROM clientes ORDER BY nombre;")
            clientes = cur.fetchall()

            cur.execute(query, params)
            remitos = cur.fetchall()
            columnas = [desc[0] for desc in cur.description]

    return render_template("remitos_generados.html", remitos=remitos, columnas=columnas, clientes=clientes)


@bp_remitos_generados.route("/entregar/<int:id_remito>")
@login_requerido
@rol_requerido("admin", "empleado")
def entregar_remito(id_remito):
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                UPDATE remitos
                SET estado = 'entregado'
                WHERE id_remito = %s AND estado = 'emitido'
                RETURNING id_pedido;
            """, (id_remito,))
            result = cur.fetchone()
            if result:
                id_pedido = result[0]
                cur.execute("""
                    UPDATE pedidos
                    SET estado = 'entregado'
                    WHERE id_pedido = %s;
                """, (id_pedido,))
                flash("Remito marcado como entregado.")
            else:
                flash("El remito ya fue entregado o cancelado.")
    return redirect(url_for("remitos_generados.lista_remitos"))


@bp_remitos_generados.route("/cancelar/<int:id_remito>", methods=["POST"])
@login_requerido
@rol_requerido("admin")
def cancelar_remito(id_remito):
    try:
        with get_conn() as conn:
            with conn.cursor() as cur:
                conn.autocommit = False
                cur.execute("""
                    UPDATE remitos
                    SET estado = 'cancelado'
                    WHERE id_remito = %s AND estado != 'entregado'
                    RETURNING id_pedido;
                """, (id_remito,))
                result = cur.fetchone()
                if not result:
                    flash("El remito ya fue entregado y no puede cancelarse.")
                    return redirect(url_for("remitos_generados.lista_remitos"))

                id_pedido = result[0]
                cur.execute("""
                    UPDATE pedidos
                    SET estado = 'cancelado'
                    WHERE id_pedido = %s;
                """, (id_pedido,))

                cur.execute("""
                    SELECT id_movimiento, id_cliente, importe
                    FROM movimientos_cuenta_corriente
                    WHERE id_remito = %s;
                """, (id_remito,))
                mov = cur.fetchone()

                if mov:
                    id_movimiento, id_cliente, importe = mov
                    cur.execute("""
                        UPDATE clientes_cuenta_corriente
                        SET saldo = saldo - %s
                        WHERE id_cliente = %s;
                    """, (importe, id_cliente))

                    cur.execute("""
                        INSERT INTO movimientos_cuenta_corriente (
                            id_movimiento, id_cliente, fecha, tipo_mov, importe, forma_pago, id_remito
                        ) VALUES (
                            uuid_generate_v4()::text, %s, CURRENT_DATE, %s, %s, %s, NULL
                        );
                    """, (id_cliente, 'cancelacion_remito', -importe, 'cancelacion'))

                conn.commit()
                flash("Remito cancelado y cuenta corriente ajustada.")
    except Exception as e:
        conn.rollback()
        flash("Error al cancelar remito. No se aplicaron los cambios.")
        print(f"[ERROR] cancelar_remito: {e}")

    return redirect(url_for("remitos_generados.lista_remitos"))


