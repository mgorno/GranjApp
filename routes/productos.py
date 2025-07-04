from flask import Blueprint, render_template, request, redirect, url_for, flash
from models import get_conn
import uuid, re

bp_productos = Blueprint("productos", __name__, url_prefix="/productos")

@bp_productos.route("/")
def productos():
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute("""
            SELECT id_producto, descripcion, unidad_base, precio
            FROM productos
            ORDER BY descripcion
        """)
        productos = cur.fetchall()                # [(id, desc, unidad, precio), …]
    return render_template("productos.html", productos=productos)

@bp_productos.route("/nuevo", methods=["GET", "POST"])
def nuevo():
    if request.method == "POST":
        descripcion = request.form.get("descripcion", "").strip()
        unidad_base = request.form.get("unidad_base", "").strip()
        precio = request.form.get("precio", "").strip()

        errores = []
        if not descripcion:
            errores.append("La descripción es obligatoria.")
        if not unidad_base:
            errores.append("La unidad base es obligatoria.")
        if not precio or not re.fullmatch(r"^\d+(\.\d{1,2})?$", precio):
            errores.append("El precio debe ser un número válido.")

        if errores:
            for e in errores:
                flash(e, "error")
            return render_template("producto.html",
                                   descripcion=descripcion,
                                   unidad_base=unidad_base,
                                   precio=precio)

        id_producto = str(uuid.uuid4())
        with get_conn() as conn, conn.cursor() as cur:
            cur.execute("""
                INSERT INTO productos (id_producto, descripcion, unidad_base, precio) 
                VALUES (%s, %s, %s, %s)
            """, (id_producto, descripcion, unidad_base, float(precio)))
            conn.commit()

        flash("Producto creado correctamente.", "success")
        return redirect(url_for("productos.nuevo"))

    return render_template("producto.html")
