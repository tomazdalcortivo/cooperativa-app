from app import db
from flask_login import UserMixin
from datetime import datetime

produtor_categoria = db.Table('produtor_categoria',
    db.Column('produtor_id', db.Integer, db.ForeignKey('produtor.id'), primary_key=True),
    db.Column('categoria_id', db.Integer, db.ForeignKey('categoria.id'), primary_key=True)
)
class PontoRetirada(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False) 
    endereco = db.Column(db.String(200), nullable=False)
    horarios = db.Column(db.String(100)) 
class ItemPedido(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    pedido_id = db.Column(db.Integer, db.ForeignKey('pedido.id'), nullable=False)
    produto_id = db.Column(db.Integer, db.ForeignKey('produto.id'), nullable=False)
    quantidade = db.Column(db.Integer, nullable=False)
    preco_unitario = db.Column(db.Float, nullable=False)

    produto = db.relationship('Produto')

class Usuario(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    senha_hash = db.Column(db.String(255), nullable=False)
    tipo_usuario = db.Column(db.String(20), nullable=False) 
    ativo = db.Column(db.Boolean, default=True)
    
    produtor = db.relationship("Produtor", backref="usuario", uselist=False)
    cliente = db.relationship("Cliente", backref="usuario", uselist=False)

    @property
    def is_active(self):
        return self.ativo

class Produtor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey("usuario.id"), unique=True, nullable=False)
    nome = db.Column(db.String(100), nullable=False)
    cpf = db.Column(db.String(14))
    telefone = db.Column(db.String(20))
    endereco = db.Column(db.Text)
    certificacoes = db.Column(db.Text)
    
    produtos = db.relationship("Produto", backref="produtor", lazy=True)
    categorias = db.relationship('Categoria', secondary=produtor_categoria, lazy='subquery',
        backref=db.backref('produtores', lazy=True))

class Cliente(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey("usuario.id"), unique=True, nullable=False)
    nome = db.Column(db.String(100), nullable=False)
    cpf = db.Column(db.String(14))
    telefone = db.Column(db.String(20))
    enderecos = db.Column(db.Text) 
    
    pedidos = db.relationship('Pedido', backref='cliente', lazy=True)

class Categoria(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(50), unique=True, nullable=False)
    descricao = db.Column(db.Text)
    icone = db.Column(db.String(50))
    
    produtos = db.relationship("Produto", backref="categoria", lazy=True)

class Produto(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    descricao = db.Column(db.Text)
    preco = db.Column(db.Float, nullable=False)
    unidade = db.Column(db.String(10))
    estoque = db.Column(db.Integer, default=0)
    imagens = db.Column(db.String(200))
    
    produtor_id = db.Column(db.Integer, db.ForeignKey("produtor.id"), nullable=False)
    categoria_id = db.Column(db.Integer, db.ForeignKey("categoria.id"), nullable=False)

    preco_promocional = db.Column(db.Float, nullable=True) 
    
    disponivel_inicio = db.Column(db.Date, nullable=True)
    disponivel_fim = db.Column(db.Date, nullable=True)

    origem = db.Column(db.String(100), nullable=True)
    info_nutricional = db.Column(db.Text, nullable=True) 


    @property
    def preco_atual(self):
        if self.preco_promocional and self.preco_promocional > 0:
            return self.preco_promocional
        return self.preco

    @property
    def esta_disponivel_sazonalmente(self):
        if not self.disponivel_inicio or not self.disponivel_fim:
            return True 
        hoje = datetime.today().date()
        return self.disponivel_inicio <= hoje <= self.disponivel_fim

class Pedido(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    cliente_id = db.Column(db.Integer, db.ForeignKey('cliente.id'), nullable=False)
    data = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default='Aguardando')
    forma_pagamento = db.Column(db.String(50))
    total = db.Column(db.Float, default=0.0)
    
    data_agendada = db.Column(db.Date, nullable=True) 
    ponto_retirada_id = db.Column(db.Integer, db.ForeignKey('ponto_retirada.id'), nullable=True)
    
    ponto_retirada = db.relationship('PontoRetirada')
    itens = db.relationship('ItemPedido', backref='pedido', lazy=True)