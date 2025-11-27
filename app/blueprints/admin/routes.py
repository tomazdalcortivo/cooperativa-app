from flask import Blueprint, render_template, redirect, url_for, flash, request # <--- ADICIONE O request AQUI
from flask_login import login_required, current_user
from functools import wraps
from app import db
from app.models.models import Usuario, Pedido, Produto

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")


def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.tipo_usuario != 'admin':
            flash("Acesso negado. Esta área é restrita a administradores.")
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function


@admin_bp.route("/")
@login_required
@admin_required
def dashboard():
    # RF07.1 - Visão Geral (Dashboard)
    total_usuarios = Usuario.query.count()
    total_produtos = Produto.query.count()
    pedidos_pendentes = Pedido.query.filter_by(status='Aguardando').count()

    return render_template("admin/dashboard.html",
                           total_usuarios=total_usuarios,
                           total_produtos=total_produtos,
                           pedidos_pendentes=pedidos_pendentes)


@admin_bp.route("/usuarios")
@login_required
@admin_required
def gerenciar_usuarios():
    # RF07.6 - Gestão de Usuários
    usuarios = Usuario.query.all()
    return render_template("admin/usuarios.html", usuarios=usuarios)


@admin_bp.route("/usuario/<int:id>/editar", methods=["GET", "POST"])
@login_required
@admin_required
def editar_usuario(id):
    usuario = Usuario.query.get_or_404(id)

    if request.method == "POST":
        usuario.tipo_usuario = request.form.get("tipo_usuario")
        usuario.ativo = True if request.form.get("ativo") else False

        db.session.commit()
        flash(f"Usuário {usuario.email} atualizado com sucesso.")
        return redirect(url_for('admin.gerenciar_usuarios'))

    return render_template("admin/editar_usuario.html", usuario=usuario)
