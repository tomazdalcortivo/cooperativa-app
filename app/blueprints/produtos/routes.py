from flask import Blueprint, render_template
from app.models.models import Produto

produtos_bp = Blueprint("produtos", __name__, url_prefix="/produtos")

@produtos_bp.route("/")
def listar_produtos():
    produtos = Produto.query.all()
    return render_template("produtos/lista.html", produtos=produtos)