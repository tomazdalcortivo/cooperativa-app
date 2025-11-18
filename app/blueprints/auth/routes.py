from flask import Blueprint, render_template, redirect, request, flash
from werkzeug.security import generate_password_hash, check_password_hash
from app import db
from app.models.models import Usuario

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        senha = request.form["senha"]

        usuario = Usuario.query.filter_by(email=email).first()

        if not usuario or not check_password_hash(usuario.senha_hash, senha):
            flash("Credenciais incorretas")
            return redirect("/auth/login")

        return redirect("/")

    return render_template("auth/login.html")