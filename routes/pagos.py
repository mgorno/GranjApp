from datetime import datetime, timedelta
from flask import Blueprint, render_template, request, redirect, url_for, flash
from models import get_conn
import uuid

bp_pagos = Blueprint("pagos", __name__, url_prefix="/pagos")

@bp_pagos.route("/", methods=["GET", "POST"])
def lista():
    with get_conn() as conn:
        with conn.cursor() as cur:
            if request.method == "POST":
                id_cliente = request.form['id_cliente']
                monto_pagado = float(request.form['monto_pagado'])
                medio_pago = request.form['medio_pago']
                observaciones = request.form.get('observaciones') or ""

                ahora = datetime.utcnow()
                hace_un_minuto = ahora - timedelta(minutes=1)

                # Verifica si ya existe un pago igual en los últimos 60 segundos
                cur.execute("""
                    SELECT 1 FROM pagos
                    WHERE id_cliente = %s
                      AND monto_pagado = %s
                      AND medio_pago = %s
                      AND COALESCE(observaciones, '') = %s
                      AND fecha_pago >= %s
                    LIMIT 1
                """, (id_cliente, monto_pagado, medio_pago, observaciones, hace_un_minuto))
                existe = cur.fetchone()

                if existe:
                    flash("Ya existe un pago similar registrado hace menos de un minuto.", "warning")
                    return redirect(url_for('pagos.lista'))

                # 1. Insertar pago
                cur.execute("""
                    INSERT INTO pagos (id_cliente, monto_pagado, medio_pago, observaciones)
                    VALUES (%s, %s, %s, %s)
                """, (id_cliente, monto_pagado, medio_pago, observaciones))

                # 2. Insertar movimiento en cuenta corriente
                id_movimiento = str(uuid.uuid4())
                cur.execute("""
                    INSERT INTO movimientos_cuenta_corriente (
                        id_movimiento, id_cliente, fecha, tipo_mov, importe, forma_pago
                    ) VALUES (%s, %s, CURRENT_DATE, 'pago', %s, %s)
                """, (id_movimiento, id_cliente, monto_pagado, medio_pago))

                # 3. Actualizar saldo (sumar el pago al saldo actual)
                cur.execute("""
                    INSERT INTO clientes_cuenta_corriente (id_cliente, saldo)
                    VALUES (%s, %s)
                    ON CONFLICT (id_cliente)
                    DO UPDATE SET saldo = clientes_cuenta_corriente.saldo + EXCLUDED.saldo
                """, (id_cliente, monto_pagado))

                conn.commit()
                flash("Pago registrado correctamente", "success")
                return redirect(url_for('pagos.lista'))

            # GET: mostrar últimos pagos
            cur.execute("""
                SELECT pg.id_pago, c.nombre, pg.monto_pagado, pg.fecha_pago, pg.medio_pago 
                FROM pagos pg 
                JOIN clientes c ON c.id_cliente = pg.id_cliente 
                ORDER BY pg.fecha_pago DESC
                LIMIT 5
            """)
            pagos = cur.fetchall()

            cur.execute("SELECT id_cliente, nombre FROM clientes ORDER BY nombre")
            clientes = cur.fetchall()

    return render_template("pagos.html", pagos=pagos, clientes=clientes)
