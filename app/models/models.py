from app import db
from flask_login import UserMixin
from datetime import datetime

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

class Produtor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey("usuario.id"), unique=True, nullable=False)
    nome = db.Column(db.String(100), nullable=False)
    cpf = db.Column(db.String(14))
    telefone = db.Column(db.String(20))
    endereco = db.Column(db.Text)
    certificacoes = db.Column(db.Text)
    
    produtos = db.relationship("Produto", backref="produtor", lazy=True)

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
    imagens = db.Column(db.Text)
    
    produtor_id = db.Column(db.Integer, db.ForeignKey("produtor.id"), nullable=False)
    categoria_id = db.Column(db.Integer, db.ForeignKey("categoria.id"), nullable=False)

class Pedido(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    cliente_id = db.Column(db.Integer, db.ForeignKey('cliente.id'), nullable=False)
    data = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default='Aguardando')
    forma_pagamento = db.Column(db.String(50))
    total = db.Column(db.Float, default=0.0)
    
    itens = db.relationship('ItemPedido', backref='pedido', lazy=True)