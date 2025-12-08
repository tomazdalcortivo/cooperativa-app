from flask import Blueprint, render_template, request, flash, redirect, url_for, current_app
from flask_login import login_required, current_user
from app import db
from app.models.models import Produto, Categoria, Produtor
from datetime import datetime
import os
from werkzeug.utils import secure_filename

produtos_bp = Blueprint("produtos", __name__, url_prefix="/produtos")


def parse_data_form(data_str):
    if not data_str:
        return None
    try:
        return datetime.strptime(data_str, '%Y-%m-%d').date()
    except ValueError:
        return None


def salvar_imagem(imagem_file):
    filename = secure_filename(imagem_file.filename)
    if not os.path.exists(current_app.config['UPLOAD_FOLDER']):
        os.makedirs(current_app.config['UPLOAD_FOLDER'])
    path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
    imagem_file.save(path)
    return filename



@produtos_bp.route("/")
def listar_produtos():
    busca = request.args.get('busca', '')
    categoria_id = request.args.get('categoria')
    produtor_id = request.args.get('produtor')
    ordem = request.args.get('ordem', 'padrao')

    query = Produto.query

    if busca:
        query = query.filter(Produto.nome.ilike(
            f'%{busca}%') | Produto.descricao.ilike(f'%{busca}%'))
    if categoria_id:
        query = query.filter_by(categoria_id=int(categoria_id))
    if produtor_id:
        query = query.filter_by(produtor_id=int(produtor_id))

    if ordem == 'menor_preco':
        query = query.order_by(Produto.preco.asc())
    elif ordem == 'maior_preco':
        query = query.order_by(Produto.preco.desc())
    elif ordem == 'promocao':
        query = query.order_by(Produto.preco_promocional.isnot(None).desc())

    produtos = query.all()
    categorias = Categoria.query.all()
    produtores = Produtor.query.all()

    return render_template("produtos/lista.html",
                           produtos=produtos,
                           categorias=categorias,
                           produtores=produtores)


@produtos_bp.route("/novo", methods=["GET", "POST"])
@login_required
def novo_produto():
    if current_user.tipo_usuario != 'produtor':
        flash("Apenas produtores podem cadastrar produtos.")
        return redirect(url_for('produtos.listar_produtos'))

    if request.method == "POST":
        nome_produto = request.form.get("nome")

        produto_existente = Produto.query.filter_by(
            nome=nome_produto,
            produtor_id=current_user.produtor.id
        ).first()

        if produto_existente:
            flash(f"O produto '{nome_produto}' já existe! Use a opção Editar.")
            return redirect(url_for('produtos.listar_produtos'))

        nome_imagem = None
        if 'imagem' in request.files:
            arquivo = request.files['imagem']
            if arquivo and arquivo.filename != '':
                nome_imagem = salvar_imagem(arquivo)

        preco_promo = request.form.get("preco_promocional")
        if preco_promo:
            preco_promo = float(preco_promo.replace(",", "."))
        else:
            preco_promo = None

        qtd_min = request.form.get("quantidade_minima")
        qtd_min = float(qtd_min) if qtd_min else 1.0

        produto = Produto(
            nome=nome_produto,
            descricao=request.form.get("descricao"),
            preco=float(request.form.get("preco").replace(",", ".")),
            unidade=request.form.get("unidade"),
            estoque=int(request.form.get("estoque")),
            categoria_id=int(request.form.get("categoria")),
            produtor_id=current_user.produtor.id,
            imagens=nome_imagem,

            preco_promocional=preco_promo,
            origem=request.form.get("origem"),
            info_nutricional=request.form.get("info_nutricional"),
            disponivel_inicio=parse_data_form(
                request.form.get("disponivel_inicio")),
            disponivel_fim=parse_data_form(request.form.get("disponivel_fim")),
            quantidade_minima=qtd_min
        )

        db.session.add(produto)
        db.session.commit()
        flash("Produto cadastrado com sucesso!")
        return redirect(url_for('produtos.listar_produtos'))

    categorias = Categoria.query.all()
    return render_template("produtos/cadastro.html", categorias=categorias)


@produtos_bp.route("/editar/<int:id>", methods=["GET", "POST"])
@login_required
def editar_produto(id):
    produto = Produto.query.get_or_404(id)

    if current_user.tipo_usuario != 'admin' and produto.produtor_id != current_user.produtor.id:
        flash("Você não tem permissão para editar este produto.")
        return redirect(url_for('produtos.listar_produtos'))

    if request.method == "POST":
        produto.nome = request.form.get("nome")
        produto.descricao = request.form.get("descricao")
        produto.preco = float(request.form.get("preco").replace(",", "."))
        produto.unidade = request.form.get("unidade")
        produto.estoque = int(request.form.get("estoque"))
        produto.categoria_id = int(request.form.get("categoria"))

        if 'imagem' in request.files:
            arquivo = request.files['imagem']
            if arquivo and arquivo.filename != '':
                produto.imagens = salvar_imagem(arquivo)

        preco_promo = request.form.get("preco_promocional")
        if preco_promo:
            produto.preco_promocional = float(preco_promo.replace(",", "."))
        else:
            produto.preco_promocional = None

        produto.origem = request.form.get("origem")
        produto.info_nutricional = request.form.get("info_nutricional")
        produto.disponivel_inicio = parse_data_form(
            request.form.get("disponivel_inicio"))
        produto.disponivel_fim = parse_data_form(
            request.form.get("disponivel_fim"))

        qtd_min = request.form.get("quantidade_minima")
        produto.quantidade_minima = float(qtd_min) if qtd_min else 1.0

        db.session.commit()
        flash("Produto atualizado!")
        return redirect(url_for('produtos.listar_produtos'))

    categorias = Categoria.query.all()
    return render_template("produtos/cadastro.html", categorias=categorias, produto=produto)


@produtos_bp.route("/deletar/<int:id>")
@login_required
def deletar_produto(id):
    produto = Produto.query.get_or_404(id)

    if current_user.tipo_usuario != 'admin' and produto.produtor_id != current_user.produtor.id:
        flash("Sem permissão.")
    else:
        db.session.delete(produto)
        db.session.commit()
        flash("Produto removido.")

    return redirect(url_for('produtos.listar_produtos'))

@produtos_bp.route("/detalhe/<int:id>")
def detalhe_produto(id):
    produto = Produto.query.get_or_404(id)
    
    item_id_para_avaliar = None
    
    if current_user.is_authenticated and current_user.tipo_usuario == 'cliente':
        from app.models.models import ItemPedido, Pedido
        
        item = ItemPedido.query.join(Pedido).filter(
            Pedido.cliente_id == current_user.cliente.id,
            ItemPedido.produto_id == produto.id,
            Pedido.status == 'Entregue',
            ItemPedido.avaliacao == None
        ).first()
        
        if item:
            item_id_para_avaliar = item.id
    
    return render_template("produtos/detalhe.html", 
                          p=produto, 
                          item_id_para_avaliar=item_id_para_avaliar)