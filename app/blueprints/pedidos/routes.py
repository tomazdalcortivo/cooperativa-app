from flask import Blueprint, render_template, redirect, url_for, request, session, flash
from flask_login import login_required, current_user
from app import db
from app.models.models import Produto, Pedido, ItemPedido
from datetime import datetime

pedidos_bp = Blueprint("pedidos", __name__, url_prefix="/pedidos")


@pedidos_bp.route("/adicionar/<int:produto_id>", methods=["POST"])
def adicionar_ao_carrinho(produto_id):
    carrinho = session.get('carrinho', {})
    
    quantidade = int(request.form.get("quantidade", 1))
    id_str = str(produto_id) 
    
    if id_str in carrinho:
        carrinho[id_str] += quantidade
    else:
        carrinho[id_str] = quantidade
        
    session['carrinho'] = carrinho
    session.modified = True
    
    flash("Produto adicionado ao carrinho.")
    return redirect(request.referrer or url_for('produtos.listar_produtos'))

@pedidos_bp.route("/carrinho")
def ver_carrinho():
    carrinho = session.get('carrinho', {})
    itens_carrinho = []
    total_geral = 0
    
    if carrinho:
        produtos = Produto.query.filter(Produto.id.in_(carrinho.keys())).all()
        for p in produtos:
            qtd = carrinho[str(p.id)]
            subtotal = p.preco * qtd
            total_geral += subtotal
            itens_carrinho.append({
                'produto': p,
                'quantidade': qtd,
                'subtotal': subtotal
            })
            
    return render_template("pedidos/carrinho.html", itens=itens_carrinho, total=total_geral)

@pedidos_bp.route("/remover/<int:produto_id>")
def remover_do_carrinho(produto_id):
    carrinho = session.get('carrinho', {})
    id_str = str(produto_id)
    
    if id_str in carrinho:
        del carrinho[id_str]
        session['carrinho'] = carrinho
        session.modified = True
        
    return redirect(url_for('pedidos.ver_carrinho'))


@pedidos_bp.route("/checkout", methods=["GET", "POST"])
@login_required
def checkout():
    carrinho = session.get('carrinho', {})
    if not carrinho:
        flash("Seu carrinho está vazio.")
        return redirect(url_for('produtos.listar_produtos'))

    if request.method == "POST":
        novo_pedido = Pedido(
            cliente_id=current_user.cliente.id,
            data=datetime.now(),
            status="Aguardando Confirmação",
            forma_pagamento=request.form.get("pagamento"),
            total=0 
        )
        db.session.add(novo_pedido)
        db.session.commit() 
        
        total_pedido = 0
        produtos = Produto.query.filter(Produto.id.in_(carrinho.keys())).all()
        
        for p in produtos:
            qtd = carrinho[str(p.id)]
            preco_momento = p.preco
            subtotal = preco_momento * qtd
            total_pedido += subtotal
            
            item = ItemPedido(
                pedido_id=novo_pedido.id,
                produto_id=p.id,
                quantidade=qtd,
                preco_unitario=preco_momento
            )
            db.session.add(item)
            
            p.estoque -= qtd
            

        novo_pedido.total = total_pedido
        db.session.commit()
        
        session.pop('carrinho', None)
        flash(f"Pedido #{novo_pedido.id} realizado com sucesso!")
        return redirect(url_for('pedidos.meus_pedidos'))
        

    total_geral = 0
    itens_checkout = []
    produtos = Produto.query.filter(Produto.id.in_(carrinho.keys())).all()
    for p in produtos:
        qtd = carrinho[str(p.id)]
        total_geral += p.preco * qtd
        itens_checkout.append({'produto': p, 'quantidade': qtd, 'subtotal': p.preco * qtd})

    return render_template("pedidos/checkout.html", itens=itens_checkout, total=total_geral)

@pedidos_bp.route("/meus-pedidos")
@login_required
def meus_pedidos():
    if not current_user.cliente:
         flash("Apenas clientes podem ver seus pedidos.")
         return redirect(url_for('index'))
         
    pedidos = Pedido.query.filter_by(cliente_id=current_user.cliente.id).order_by(Pedido.data.desc()).all()
    return render_template("pedidos/meus_pedidos.html", pedidos=pedidos)