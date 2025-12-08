from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app import db
from app.models.models import Cliente, Pedido

cliente_bp = Blueprint("cliente", __name__, url_prefix="/cliente")



@cliente_bp.route("/painel")
@login_required
def painel():
    if current_user.tipo_usuario != 'cliente':
        flash("Acesso restrito a clientes.")
        return redirect(url_for('index'))

    ultimos_pedidos = Pedido.query.filter_by(cliente_id=current_user.cliente.id)\
                                  .order_by(Pedido.data.desc()).limit(5).all()

    return render_template("cliente/painel.html", pedidos=ultimos_pedidos)


@cliente_bp.route("/perfil", methods=["GET", "POST"])
@login_required
def perfil():
    if current_user.tipo_usuario != 'cliente':
        return redirect(url_for('index'))

    cliente = current_user.cliente

    if request.method == "POST":
        cliente.nome = request.form.get("nome")
        cliente.cpf = request.form.get("cpf")
        cliente.telefone = request.form.get("telefone")
        cliente.enderecos = request.form.get("endereco") 

        db.session.commit()
        flash("Seus dados foram atualizados com sucesso!")
        return redirect(url_for('cliente.painel'))

    return render_template("cliente/perfil.html", cliente=cliente)
