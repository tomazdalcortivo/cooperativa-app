from app import db
from flask_login import UserMixin

class Usuario(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True)
    senha_hash = db.Column(db.String(255))
    tipo_usuario = db.Column(db.String(20))  # admin, produtor, cliente
    ativo = db.Column(db.Boolean, default=True)

class Produto(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100))
    descricao = db.Column(db.Text)
    preco = db.Column(db.Float)
    unidade = db.Column(db.String(10))
    estoque = db.Column(db.Integer)

    produtor_id = db.Column(db.Integer, db.ForeignKey("produtor.id"))
    categoria_id = db.Column(db.Integer, db.ForeignKey("categoria.id"))
