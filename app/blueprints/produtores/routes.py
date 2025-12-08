from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app import db
from app.models.models import Produto, Produtor, ItemPedido, Pedido, Categoria 
from functools import wraps
from sqlalchemy import func

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

@produtor_bp.route("/meu-perfil")
@login_required
@produtor_required
def ver_perfil():
    perfil = current_user.produtor
    return render_template("produtores/ver_perfil.html", perfil=perfil)

@produtor_bp.route("/")
@login_required
@produtor_required
def painel():
    meus_produtos = Produto.query.filter_by(produtor_id=current_user.produtor.id).all()
    

    vendas_por_produto = db.session.query(
        Produto.nome,
        func.sum(ItemPedido.quantidade).label('total_qtd'),
        func.sum(ItemPedido.preco_unitario * ItemPedido.quantidade).label('total_valor')
    ).join(Produto).filter(
        Produto.produtor_id == current_user.produtor.id
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

@produtor_bp.route("/perfil", methods=["GET", "POST"])
@login_required
def perfil():
    perfil = current_user.produtor 

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
        return redirect(url_for('produtor.painel'))

    todas_categorias = Categoria.query.all()
    return render_template("produtores/perfil.html", perfil=perfil, categorias=todas_categorias)