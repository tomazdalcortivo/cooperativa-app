from app import db
from flask_login import UserMixin
from datetime import datetime

favoritos = db.Table('favoritos',
                     db.Column('cliente_id', db.Integer, db.ForeignKey(
                         'cliente.id'), primary_key=True),
                     db.Column('produto_id', db.Integer, db.ForeignKey(
                         'produto.id'), primary_key=True)
                     )

produtor_categoria = db.Table('produtor_categoria',
                              db.Column('produtor_id', db.Integer, db.ForeignKey(
                                  'produtor.id'), primary_key=True),
                              db.Column('categoria_id', db.Integer, db.ForeignKey(
                                  'categoria.id'), primary_key=True)
                              )


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


class Cliente(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey(
        "usuario.id"), unique=True, nullable=False)
    nome = db.Column(db.String(100), nullable=False)
    cpf = db.Column(db.String(14))
    telefone = db.Column(db.String(20))

    enderecos_texto = db.Column(db.Text)

    receber_notificacoes = db.Column(db.Boolean, default=True)

    lista_enderecos = db.relationship(
        'Endereco', backref='cliente', lazy=True)
    pedidos = db.relationship('Pedido', backref='cliente', lazy=True)
    produtos_favoritos = db.relationship(
        'Produto', secondary=favoritos, backref='clientes_que_favoritaram')


class Endereco(db.Model):  # RF09.3
    id = db.Column(db.Integer, primary_key=True)
    cliente_id = db.Column(db.Integer, db.ForeignKey(
        'cliente.id'), nullable=False)
    titulo = db.Column(db.String(50))
    rua = db.Column(db.String(150))
    numero = db.Column(db.String(20))
    bairro = db.Column(db.String(100))
    cidade = db.Column(db.String(100))
    cep = db.Column(db.String(20))
    principal = db.Column(db.Boolean, default=False)


class Avaliacao(db.Model):
    __tablename__ = 'avaliacoes'

    id = db.Column(db.Integer, primary_key=True)
    nota = db.Column(db.Integer, nullable=False)
    comentario = db.Column(db.Text, nullable=True)
    data = db.Column(db.DateTime, default=datetime.utcnow)

    produto_id = db.Column(db.Integer, db.ForeignKey('produto.id'), nullable=False)
    pedido_item_id = db.Column(db.Integer, db.ForeignKey('pedidos_itens.id'), nullable=False, unique=True)

    produto = db.relationship('Produto', backref='avaliacoes')
    pedido_item = db.relationship('ItemPedido', backref=db.backref('avaliacao', uselist=False))

class Produto(db.Model):
    __tablename__ = 'produto'  # Adicione isso para consistência

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    descricao = db.Column(db.Text)
    preco = db.Column(db.Float, nullable=False)
    unidade = db.Column(db.String(10))
    estoque = db.Column(db.Integer, default=0)
    imagens = db.Column(db.String(200))

    preco_promocional = db.Column(db.Float, nullable=True)
    quantidade_minima = db.Column(db.Float, default=1.0)
    origem = db.Column(db.String(100), nullable=True)
    info_nutricional = db.Column(db.Text, nullable=True)
    disponivel_inicio = db.Column(db.Date, nullable=True)
    disponivel_fim = db.Column(db.Date, nullable=True)

    produtor_id = db.Column(db.Integer, db.ForeignKey(
        "produtor.id"), nullable=False)
    categoria_id = db.Column(db.Integer, db.ForeignKey(
        "categoria.id"), nullable=False)

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

    @property
    def media_avaliacao(self):
        notas = [a.nota for a in self.avaliacoes]
        if notas:
            return round(sum(notas) / len(notas), 1)
        return 0


class Produtor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey(
        "usuario.id"), unique=True, nullable=False)
    nome = db.Column(db.String(100), nullable=False)
    cpf = db.Column(db.String(14))
    telefone = db.Column(db.String(20))
    endereco = db.Column(db.Text)
    certificacoes = db.Column(db.Text)
    produtos = db.relationship("Produto", backref="produtor", lazy=True)
    categorias = db.relationship('Categoria', secondary=produtor_categoria,
                                 lazy='subquery', backref=db.backref('produtores', lazy=True))


class Categoria(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(50), unique=True, nullable=False)
    descricao = db.Column(db.Text)
    icone = db.Column(db.String(50))
    valor_minimo = db.Column(db.Float, default=0.0)
    produtos = db.relationship("Produto", backref="categoria", lazy=True)


class Pedido(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    cliente_id = db.Column(db.Integer, db.ForeignKey(
        'cliente.id'), nullable=False)
    data = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default='Aguardando')
    forma_pagamento = db.Column(db.String(50))
    total = db.Column(db.Float, default=0.0)
    data_agendada = db.Column(db.Date, nullable=True)
    ponto_retirada_id = db.Column(
        db.Integer, db.ForeignKey('ponto_retirada.id'), nullable=True)
    taxa_entrega = db.Column(db.Float, default=0.0)
    regiao_id = db.Column(
        db.Integer, db.ForeignKey('regiao.id'), nullable=True)
    regiao = db.relationship('Regiao')
    ponto_retirada = db.relationship('PontoRetirada')
    itens = db.relationship('ItemPedido', backref='pedido', lazy=True)


class ItemPedido(db.Model):
    __tablename__ = 'pedidos_itens'

    id = db.Column(db.Integer, primary_key=True)

    pedido_id = db.Column(db.Integer, db.ForeignKey(
        'pedido.id'), nullable=False)
    produto_id = db.Column(db.Integer, db.ForeignKey(
        'produto.id'), nullable=False)
    quantidade = db.Column(db.Integer, nullable=False)
    preco_unitario = db.Column(db.Float, nullable=False)

    produto = db.relationship('Produto')

    @property
    def foi_avaliado(self):
        return self.avaliacao is not None


class PontoRetirada(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    endereco = db.Column(db.String(200), nullable=False)
    horarios = db.Column(db.String(100))


class Regiao(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    taxa = db.Column(db.Float, default=0.0)
