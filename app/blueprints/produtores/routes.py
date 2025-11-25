from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app import db
from app.models.models import Produto, Produtor
from functools import wraps

produtor_bp = Blueprint("produtor", __name__, url_prefix="/produtor")


def produtor_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.tipo_usuario != 'produtor':
            flash("Acesso não autorizado. Área restrita a Produtores.")
            return redirect(url_for('index'))
        if not current_user.produtor:
            flash("Perfil de Produtor não configurado. Por favor, complete seu cadastro.")
            return redirect(url_for('produtor.perfil'))
        return f(*args, **kwargs)
    return decorated_function


@produtor_bp.route("/")
@login_required
@produtor_required
def painel():
    meus_produtos = Produto.query.filter_by(produtor_id=current_user.produtor.id).all()
    # Futuramente: Aqui listaremos pedidos pendentes para este produtor
    
    return render_template("produtores/painel.html", meus_produtos=meus_produtos)

@produtor_bp.route("/perfil", methods=["GET", "POST"])
@login_required
def perfil():
    if current_user.tipo_usuario == 'produtor' and not current_user.produtor:
        perfil = Produtor(usuario_id=current_user.id)
        db.session.add(perfil)
        db.session.commit()
    elif current_user.tipo_usuario == 'produtor':
        perfil = current_user.produtor
    else:
        flash("Funcionalidade apenas para Produtores.")
        return redirect(url_for('index'))

    if request.method == "POST":
        perfil.nome = request.form.get("nome")
        perfil.cpf = request.form.get("cpf")
        perfil.telefone = request.form.get("telefone")
        perfil.endereco = request.form.get("endereco")
        perfil.certificacoes = request.form.get("certificacoes")

        db.session.commit()
        flash("Seu perfil foi atualizado com sucesso!")
        return redirect(url_for('produtor.painel'))

    return render_template("produtores/perfil.html", perfil=perfil)