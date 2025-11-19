from flask import Blueprint, render_template, redirect, request, flash, url_for
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user, login_required, current_user
from app import db
from app.models.models import Usuario, Cliente

auth_bp = Blueprint("auth", __name__, url_prefix="/auth", template_folder="templates")


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        senha = request.form.get("senha")

        usuario = Usuario.query.filter_by(email=email).first()

        if usuario and check_password_hash(usuario.senha_hash, senha):
            login_user(usuario)
            return redirect(url_for('index'))
        else:
            flash("Email ou senha incorretos.")

    return render_template("auth/login.html")


@auth_bp.route("/registro", methods=["GET", "POST"])
def registro():
    if request.method == "POST":
        email = request.form.get("email")
        nome = request.form.get("nome")
        senha = request.form.get("senha")

        if Usuario.query.filter_by(email=email).first():
            flash("Email já cadastrado.")
            return redirect(url_for('auth.registro'))

        novo_usuario = Usuario(
            email=email,
            senha_hash=generate_password_hash(senha),
            tipo_usuario='cliente'
        )
        db.session.add(novo_usuario)
        db.session.commit()

        novo_cliente = Cliente(usuario_id=novo_usuario.id, nome=nome)
        db.session.add(novo_cliente)
        db.session.commit()

        login_user(novo_usuario)
        return redirect(url_for('index'))

    return render_template("auth/registro.html")


@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))
