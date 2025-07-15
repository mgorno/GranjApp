from flask import Blueprint, render_template
from flask_login import login_required

bp_main = Blueprint("main", __name__)

@bp_main.route("/inicio")
@login_required
def inicio():
    return render_template("inicio.html")


