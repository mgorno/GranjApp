from flask import Blueprint, render_template, request, redirect, url_for, flash
from models import get_conn

bp_pagos = Blueprint("pagos", __name__, url_prefix="/pagos")

@bp_pagos.route("/", methods=["GET", "POST"])
def lista():
    with get_conn() as conn, conn.cursor() as cur:
        if request.method == "POST":
            cur.execute("""
                INSERT INTO pagos (id_cliente, monto_pagado, medio_pago, observaciones) 
                VALUES (%s, %s, %s, %s)
            """, (
                request.form['id_cliente'],
                request.form['monto_pagado'],
                request.form['medio_pago'],
                request.form.get('observaciones')
            ))
            conn.commit()
            flash("Pago registrado correctamente", "success")
            return redirect(url_for('pagos.lista'))

        cur.execute("""
            SELECT pg.id_pago, c.nombre, pg.monto_pagado, pg.fecha_pago, pg.medio_pago 
            FROM pagos pg 
            JOIN clientes c ON c.id_cliente = pg.id_cliente 
            ORDER BY pg.fecha_pago DESC
        """)
        pagos = cur.fetchall()

        cur.execute("SELECT id_cliente, nombre FROM clientes")
        clientes = cur.fetchall()

    return render_template("pagos.html", pagos=pagos, clientes=clientes)
