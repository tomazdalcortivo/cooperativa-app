from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app import db
from app.models.models import Produto, Produtor, ItemPedido, Categoria, Pedido, PontoRetirada
from functools import wraps
from sqlalchemy import func

produtor_bp = Blueprint("produtor", __name__, url_prefix="/produtor")


def produtor_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.tipo_usuario != 'produtor':
            flash("Acesso não autorizado.")
            return redirect(url_for('index'))
        if not current_user.produtor:
            return redirect(url_for('produtor.perfil'))
        return f(*args, **kwargs)
    return decorated_function


@produtor_bp.route("/")
@login_required
@produtor_required
def painel():
    meus_produtos = Produto.query.filter_by(
        produtor_id=current_user.produtor.id).all()

    vendas_por_produto = db.session.query(
        Produto.nome,
        func.sum(ItemPedido.quantidade).label('total_qtd'),
        func.sum(ItemPedido.preco_unitario *
                 ItemPedido.quantidade).label('total_valor')
    ).select_from(ItemPedido).join(Produto).join(Pedido).filter(
        Produto.produtor_id == current_user.produtor.id,
        Pedido.status == 'Entregue'
    ).group_by(Produto.nome).all()

    faturamento_total = sum([v.total_valor for v in vendas_por_produto])

    minhas_vendas = db.session.query(ItemPedido).join(Produto).filter(
        Produto.produtor_id == current_user.produtor.id
    ).order_by(ItemPedido.id.desc()).all()

    return render_template("produtores/painel.html",
                           meus_produtos=meus_produtos,
                           minhas_vendas=minhas_vendas,
                           vendas_por_produto=vendas_por_produto,
                           faturamento_total=faturamento_total)



@produtor_bp.route("/meu-perfil")
@login_required
@produtor_required
def ver_perfil():
    perfil = current_user.produtor
    return render_template("produtores/ver_perfil.html", perfil=perfil)



@produtor_bp.route("/perfil", methods=["GET", "POST"])
@login_required
def perfil():
    if current_user.tipo_usuario == 'produtor' and not current_user.produtor:
        perfil = Produtor(usuario_id=current_user.id, nome="Novo Produtor")
        db.session.add(perfil)
        db.session.commit()
    elif current_user.tipo_usuario == 'produtor':
        perfil = current_user.produtor
    else:
        return redirect(url_for('index'))

    if request.method == "POST":
        perfil.nome = request.form.get("nome")
        perfil.cpf = request.form.get("cpf")
        perfil.telefone = request.form.get("telefone")
        perfil.endereco = request.form.get("endereco")
        perfil.certificacoes = request.form.get("certificacoes")

        categoria_ids = request.form.getlist('categorias')
        perfil.categorias = []
        for cat_id in categoria_ids:
            cat = Categoria.query.get(int(cat_id))
            if cat:
                perfil.categorias.append(cat)

        db.session.commit()
        flash("Perfil atualizado com sucesso!")
        return redirect(url_for('produtor.ver_perfil'))

    todas_categorias = Categoria.query.all()
    return render_template("produtores/perfil.html", perfil=perfil, categorias=todas_categorias)



@produtor_bp.route("/pedido/<int:pedido_id>/status", methods=["POST"])
@login_required
@produtor_required
def atualizar_status(pedido_id):
    pedido = Pedido.query.get_or_404(pedido_id)
    novo_status = request.form.get("novo_status")

    tem_produto_meu = False
    for item in pedido.itens:
        if item.produto.produtor_id == current_user.produtor.id:
            tem_produto_meu = True
            break

    if not tem_produto_meu:
        flash("Sem permissão.")
    elif novo_status:
        pedido.status = novo_status
        db.session.commit()
        flash(f"Status atualizado para '{novo_status}'.")

    return redirect(url_for('produtor.painel'))




@produtor_bp.route("/pontos", methods=["GET", "POST"])
@login_required
@produtor_required
def gerenciar_pontos():
    if request.method == "POST":
        nome = request.form.get("nome")
        endereco = request.form.get("endereco")
        horarios = request.form.get("horarios")

        novo_ponto = PontoRetirada(
            nome=nome, endereco=endereco, horarios=horarios)
        db.session.add(novo_ponto)
        db.session.commit()
        flash("Ponto cadastrado!")
        return redirect(url_for('produtor.gerenciar_pontos'))

    pontos = PontoRetirada.query.all()
    return render_template("produtores/pontos.html", pontos=pontos)


@produtor_bp.route("/pontos/deletar/<int:id>")
@login_required
@produtor_required
def deletar_ponto(id):
    ponto = PontoRetirada.query.get_or_404(id)
    db.session.delete(ponto)
    db.session.commit()
    flash("Ponto removido.")
    return redirect(url_for('produtor.gerenciar_pontos'))
