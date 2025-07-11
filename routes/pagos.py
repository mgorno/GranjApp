from datetime import datetime, timedelta
from flask import Blueprint, render_template, request, redirect, url_for, flash
from models import get_conn

bp_pagos = Blueprint("pagos", __name__, url_prefix="/pagos")

@bp_pagos.route("/", methods=["GET", "POST"])
def lista():
    with get_conn() as conn, conn.cursor() as cur:
        if request.method == "POST":
            id_cliente = request.form['id_cliente']
            monto_pagado = float(request.form['monto_pagado'])
            medio_pago = request.form['medio_pago']
            observaciones = request.form.get('observaciones') or ""

            # Tiempo actual y hace 1 minuto
            ahora = datetime.utcnow()
            hace_un_minuto = ahora - timedelta(minutes=1)

            # Verificamos si hay un pago similar en los últimos 60 segundos
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

            # Insertar pago
            cur.execute("""
                INSERT INTO pagos (id_cliente, monto_pagado, medio_pago, observaciones) 
                VALUES (%s, %s, %s, %s)
            """, (id_cliente, monto_pagado, medio_pago, observaciones))
            conn.commit()
            flash("Pago registrado correctamente", "success")
            return redirect(url_for('pagos.lista'))

        # Mostrar últimos 5 pagos
        cur.execute("""
            SELECT pg.id_pago, c.nombre, pg.monto_pagado, pg.fecha_pago, pg.medio_pago 
            FROM pagos pg 
            JOIN clientes c ON c.id_cliente = pg.id_cliente 
            ORDER BY pg.fecha_pago DESC
            LIMIT 5
        """)
        pagos = cur.fetchall()

        cur.execute("SELECT id_cliente, nombre FROM clientes")
        clientes = cur.fetchall()

    return render_template("pagos.html", pagos=pagos, clientes=clientes)
