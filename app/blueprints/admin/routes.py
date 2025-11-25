from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from functools import wraps
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