from flask import Blueprint, render_template
from flask_login import login_required

bp_main = Blueprint("main", __name__)

@bp_main.route("/index")
@login_required
def index():
    return render_template("index.html")


