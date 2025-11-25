from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app import db
from app.models.models import Produto, Categoria

produtos_bp = Blueprint("produtos", __name__, url_prefix="/produtos", template_folder="templates")

@produtos_bp.route("/")
def listar_produtos():
    produtos = Produto.query.all()
    return render_template("produtos/lista.html", produtos=produtos)

@produtos_bp.route("/novo", methods=["GET", "POST"])
@login_required
def novo_produto():

    if current_user.tipo_usuario != 'produtor':
        flash("Apenas produtores podem cadastrar produtos.")
        return redirect(url_for('produtos.listar_produtos'))

    if request.method == "POST":

        produto = Produto(
            nome=request.form.get("nome"),
            descricao=request.form.get("descricao"),
            preco=float(request.form.get("preco").replace(",", ".")), 
            unidade=request.form.get("unidade"),
            estoque=int(request.form.get("estoque")),
            categoria_id=int(request.form.get("categoria")),
            produtor_id=current_user.produtor.id  
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
        flash("Você não tem permissão para excluir este produto.")
    else:
        db.session.delete(produto)
        db.session.commit()
        flash("Produto removido.")

    return redirect(url_for('produtos.listar_produtos'))