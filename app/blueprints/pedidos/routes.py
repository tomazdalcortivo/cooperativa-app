from flask import Blueprint, render_template, redirect, url_for, request, session, flash, abort
from flask_login import login_required, current_user
from app import db
from app.models.models import Produto, Pedido, ItemPedido, PontoRetirada, Categoria
from datetime import datetime

pedidos_bp = Blueprint("pedidos", __name__, url_prefix="/pedidos")


@pedidos_bp.route("/adicionar/<int:produto_id>", methods=["POST"])
def adicionar_ao_carrinho(produto_id):
    produto = Produto.query.get_or_404(produto_id) 
    carrinho = session.get('carrinho', {})
    
    quantidade_solicitada = int(request.form.get("quantidade", 1))
    
    if quantidade_solicitada < produto.quantidade_minima:
        quantidade_solicitada = int(produto.quantidade_minima)
        flash(f"Atenção: A venda mínima para {produto.nome} é de {produto.quantidade_minima} {produto.unidade}. Adicionamos o mínimo para você.")
    
    id_str = str(produto_id)
    
    if id_str in carrinho:
        nova_qtd = carrinho[id_str] + quantidade_solicitada
    else:
        nova_qtd = quantidade_solicitada
        
    carrinho[id_str] = nova_qtd
    session['carrinho'] = carrinho
    return redirect(request.referrer or url_for('produtos.listar_produtos'))


@pedidos_bp.route("/atualizar", methods=["POST"])
def atualizar_carrinho():
    carrinho = session.get('carrinho', {})
    
    for key in request.form:
        if key.startswith('qtd_'):
            parts = key.split('_')
            if len(parts) >= 2:
                produto_id = parts[1]
                produto = Produto.query.get(produto_id) 
                
                try:
                    nova_qtd = int(request.form.get(key))
                    
                    if 0 < nova_qtd < produto.quantidade_minima:
                        carrinho[produto_id] = int(produto.quantidade_minima)
                        flash(f"Quantidade de {produto.nome} ajustada para o mínimo de {produto.quantidade_minima} {produto.unidade}.")
                    elif nova_qtd > 0:
                        carrinho[produto_id] = nova_qtd
                    else:
                        carrinho.pop(produto_id, None) 
                except ValueError:
                    pass
                
    session['carrinho'] = carrinho
    session.modified = True
    return redirect(url_for('pedidos.ver_carrinho'))


@pedidos_bp.route("/carrinho")
def ver_carrinho():
    carrinho = session.get('carrinho', {})
    itens_carrinho = []
    total_geral = 0
    totais_categoria = {}

    if carrinho:
        produtos = Produto.query.filter(Produto.id.in_(carrinho.keys())).all()
        for p in produtos:
            qtd = carrinho[str(p.id)]
            preco = p.preco_atual
            subtotal = preco * qtd
            total_geral += subtotal

            cat_nome = p.categoria.nome
            totais_categoria[cat_nome] = totais_categoria.get(
                cat_nome, 0) + subtotal

            itens_carrinho.append({
                'produto': p,
                'quantidade': qtd,
                'preco_unitario': preco,
                'subtotal': subtotal
            })

    alertas_minimo = []
    categorias_db = Categoria.query.all()

    for cat in categorias_db:
        total_atual = totais_categoria.get(cat.nome, 0)
        if total_atual > 0 and total_atual < cat.valor_minimo:
            faltam = cat.valor_minimo - total_atual
            alertas_minimo.append(
                f"{cat.nome}: Mínimo R$ {cat.valor_minimo:.2f} (Faltam R$ {faltam:.2f})")

    return render_template("pedidos/carrinho.html",
                           itens=itens_carrinho,
                           total=total_geral,
                           alertas_minimo=alertas_minimo)


@pedidos_bp.route("/remover/<int:produto_id>")
def remover_do_carrinho(produto_id):
    carrinho = session.get('carrinho', {})
    id_str = str(produto_id)
    if id_str in carrinho:
        del carrinho[id_str]
        session['carrinho'] = carrinho
    return redirect(url_for('pedidos.ver_carrinho'))



@pedidos_bp.route("/checkout", methods=["GET", "POST"])
@login_required
def checkout():
    carrinho = session.get('carrinho', {})
    if not carrinho:
        return redirect(url_for('produtos.listar_produtos'))

    produtos = Produto.query.filter(Produto.id.in_(carrinho.keys())).all()
    
    for p in produtos:
        qtd = carrinho[str(p.id)]
        if qtd < p.quantidade_minima:
            flash(f"Você precisa comprar no mínimo {p.quantidade_minima} {p.unidade} de {p.nome}.")
            return redirect(url_for('pedidos.ver_carrinho'))
    carrinho = session.get('carrinho', {})
    if not carrinho:
        return redirect(url_for('produtos.listar_produtos'))

    produtos = Produto.query.filter(Produto.id.in_(carrinho.keys())).all()
    totais_categoria = {}
    for p in produtos:
        qtd = carrinho[str(p.id)]
        totais_categoria[p.categoria.nome] = totais_categoria.get(
            p.categoria.nome, 0) + (p.preco_atual * qtd)

    categorias_db = Categoria.query.all()
    for cat in categorias_db:
        total = totais_categoria.get(cat.nome, 0)
        if total > 0 and total < cat.valor_minimo:
            flash(
                f"Categoria {cat.nome} não atingiu o mínimo de R$ {cat.valor_minimo:.2f}")
            return redirect(url_for('pedidos.ver_carrinho'))

    if request.method == "POST":
        data_str = request.form.get("data_agendada")
        data_agendada = None
        if data_str:
            try:
                data_agendada = datetime.strptime(data_str, '%Y-%m-%d').date()
            except ValueError:
                pass

        novo_pedido = Pedido(
            cliente_id=current_user.cliente.id,
            data=datetime.now(),
            status="Aguardando Confirmação",
            forma_pagamento=request.form.get("pagamento"),
            data_agendada=data_agendada,
            ponto_retirada_id=int(request.form.get("ponto_retirada")) if request.form.get(
                "ponto_retirada") else None,
            total=0
        )
        db.session.add(novo_pedido)
        db.session.commit()

        total_pedido = 0
        for p in produtos:
            qtd = carrinho[str(p.id)]
            preco = p.preco_atual
            item = ItemPedido(pedido_id=novo_pedido.id,
                              produto_id=p.id, quantidade=qtd, preco_unitario=preco)
            db.session.add(item)
            total_pedido += (preco * qtd)

            if p.estoque >= qtd:
                p.estoque -= qtd

        novo_pedido.total = total_pedido
        db.session.commit()
        session.pop('carrinho', None)
        flash(f"Pedido #{novo_pedido.id} realizado com sucesso!")
        return redirect(url_for('cliente.painel'))

    pontos = PontoRetirada.query.all()
    total_geral = sum([p.preco_atual * carrinho[str(p.id)] for p in produtos])
    itens_checkout = [{'produto': p, 'quantidade': carrinho[str(
        p.id)], 'preco_unitario': p.preco_atual, 'subtotal': p.preco_atual * carrinho[str(p.id)]} for p in produtos]

    return render_template("pedidos/checkout.html", itens=itens_checkout, total=total_geral, pontos=pontos, datetime=datetime)



@pedidos_bp.route("/cancelar/<int:pedido_id>", methods=["POST"])
@login_required
def cancelar_pedido(pedido_id):
    pedido = Pedido.query.get_or_404(pedido_id)

    if current_user.tipo_usuario != 'admin' and pedido.cliente_id != current_user.cliente.id:
        flash("Não autorizado.")
        return redirect(url_for('cliente.painel'))

    if pedido.status in ['Entregue', 'Cancelado']:
        flash("Este pedido não pode ser cancelado pois já foi finalizado.")
        return redirect(url_for('cliente.painel'))

    for item in pedido.itens:
        produto = Produto.query.get(item.produto_id)
        if produto:
            produto.estoque += item.quantidade

    pedido.status = "Cancelado"
    db.session.commit()

    flash(f"Pedido #{pedido.id} cancelado.")
    return redirect(url_for('cliente.painel'))



@pedidos_bp.route("/comprovante/<int:pedido_id>")
@login_required
def comprovante(pedido_id):
    pedido = Pedido.query.get_or_404(pedido_id)

    if current_user.tipo_usuario != 'admin' and \
       (current_user.cliente and pedido.cliente_id != current_user.cliente.id) and \
       (current_user.tipo_usuario != 'produtor'):
        flash("Acesso negado.")
        return redirect(url_for('index'))

    return render_template("pedidos/comprovante.html", pedido=pedido)


@pedidos_bp.route("/meus-pedidos")
@login_required
def meus_pedidos():
    if not current_user.cliente:
        flash("Apenas clientes podem ver seus pedidos.")
        return redirect(url_for('index'))

    pedidos = Pedido.query.filter_by(
        cliente_id=current_user.cliente.id).order_by(Pedido.data.desc()).all()
    return render_template("pedidos/meus_pedidos.html", pedidos=pedidos)
