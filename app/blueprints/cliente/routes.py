from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app import db
from app.models.models import Cliente, Pedido, Endereco, Produto, Avaliacao, ItemPedido
from app.forms import AvaliacaoForm

cliente_bp = Blueprint("cliente", __name__, url_prefix="/cliente")


@cliente_bp.route("/painel")
@login_required
def painel():
    if current_user.tipo_usuario != 'cliente':
        flash("Acesso restrito a clientes.")
        return redirect(url_for('index'))

    todos_pedidos = Pedido.query.filter_by(
        cliente_id=current_user.cliente.id).all()

    total_pedidos = len(todos_pedidos)
    pedidos_concluidos = [p for p in todos_pedidos if p.status == 'Entregue']
    total_gasto = sum([p.total for p in pedidos_concluidos])

    ultimos_pedidos = sorted(
        todos_pedidos, key=lambda x: x.data, reverse=True)[:5]

    from app.models.models import Endereco
    endereco_principal = Endereco.query.filter_by(
        cliente_id=current_user.cliente.id, principal=True).first()
    if not endereco_principal:
        endereco_principal = Endereco.query.filter_by(
            cliente_id=current_user.cliente.id).first()

    return render_template("cliente/painel.html",
                           pedidos=ultimos_pedidos,
                           total_pedidos=total_pedidos,
                           total_gasto=total_gasto,
                           endereco_principal=endereco_principal)


@cliente_bp.route("/perfil", methods=["GET", "POST"])
@login_required
def perfil():
    cliente = current_user.cliente
    if request.method == "POST":
        cliente.nome = request.form.get("nome")
        cliente.telefone = request.form.get("telefone")
        cliente.receber_notificacoes = True if request.form.get(
            "notificacoes") else False
        db.session.commit()
        flash("Dados atualizados!")
        return redirect(url_for('cliente.painel'))
    return render_template("cliente/perfil.html", cliente=cliente)


@cliente_bp.route("/enderecos", methods=["GET", "POST"])
@login_required
def enderecos():
    if request.method == "POST":
        novo_end = Endereco(
            cliente_id=current_user.cliente.id,
            titulo=request.form.get("titulo"),
            rua=request.form.get("rua"),
            numero=request.form.get("numero"),
            bairro=request.form.get("bairro"),
            cidade=request.form.get("cidade"),
            cep=request.form.get("cep")
        )
        db.session.add(novo_end)
        db.session.commit()
        flash("Endereço adicionado!")
        return redirect(url_for('cliente.enderecos'))

    lista = Endereco.query.filter_by(cliente_id=current_user.cliente.id).all()
    return render_template("cliente/enderecos.html", enderecos=lista)


@cliente_bp.route("/enderecos/deletar/<int:id>")
@login_required
def deletar_endereco(id):
    end = Endereco.query.get_or_404(id)
    if end.cliente_id == current_user.cliente.id:
        db.session.delete(end)
        db.session.commit()
    return redirect(url_for('cliente.enderecos'))


@cliente_bp.route("/favoritar/<int:produto_id>")
@login_required
def favoritar(produto_id):
    produto = Produto.query.get_or_404(produto_id)
    cliente = current_user.cliente

    if produto in cliente.produtos_favoritos:
        cliente.produtos_favoritos.remove(produto)
        flash(f"Removido dos favoritos: {produto.nome}")
    else:
        cliente.produtos_favoritos.append(produto)
        flash(f"Adicionado aos favoritos: {produto.nome}")

    db.session.commit()
    return redirect(request.referrer or url_for('produtos.listar_produtos'))


@cliente_bp.route("/favoritos")
@login_required
def lista_favoritos():
    return render_template("cliente/favoritos.html", produtos=current_user.cliente.produtos_favoritos)


@cliente_bp.route("/avaliar/<int:item_id>", methods=['GET', 'POST'])
@login_required
def avaliar_produto(item_id):
    if current_user.tipo_usuario != 'cliente':
        flash("Acesso restrito a clientes.", "danger")
        return redirect(url_for('index'))

    item = ItemPedido.query.get_or_404(item_id)

    if item.pedido.status != 'Entregue':
        flash("Você só pode avaliar itens de pedidos já entregues.", "danger")
        return redirect(url_for('pedidos.meus_pedidos'))

    if item.pedido.cliente_id != current_user.cliente.id:
        flash("Acesso negado: Este item não pertence a um de seus pedidos.", "danger")
        return redirect(url_for('pedidos.meus_pedidos'))

    if item.foi_avaliado:
        flash(f"O produto '{item.produto.nome}' já foi avaliado neste pedido.", "warning")
        return redirect(url_for('pedidos.meus_pedidos'))

    if request.method == 'POST':
        nota = request.form.get('nota', type=int)
        comentario = request.form.get('comentario', '').strip()

        if not nota or nota < 1 or nota > 5:
            flash("Por favor, selecione uma nota entre 1 e 5.", "danger")
            return render_template("cliente/avaliar_produto_simples.html", item=item)

        nova_avaliacao = Avaliacao(
            nota=nota,
            comentario=comentario if comentario else None,
            produto_id=item.produto_id,
            pedido_item_id=item.id
        )
        
        try:
            db.session.add(nova_avaliacao)
            db.session.commit()
            flash(f"Avaliação para o produto '{item.produto.nome}' enviada com sucesso!", "success")
            return redirect(url_for('produtos.detalhe_produto', id=item.produto_id))
        except Exception as e:
            db.session.rollback()
            flash(f"Erro ao salvar avaliação: {str(e)}", "danger")
            return render_template("cliente/avaliar_produto_simples.html", item=item)

    return render_template("cliente/avaliar_produto_simples.html", item=item)
    