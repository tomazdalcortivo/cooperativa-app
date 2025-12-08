from app import create_app, db
from app.models.models import Usuario, Produtor, Cliente, Categoria, PontoRetirada, Regiao 
from werkzeug.security import generate_password_hash

app = create_app()

with app.app_context():
    db.create_all()
    print("Tabelas criadas com sucesso!")

    if not Categoria.query.first():
        print("Criando categorias...")
        categorias = [
            {'nome': 'Hortifruti', 'minimo': 0.0},
            {'nome': 'Laticínios', 'minimo': 0.0},
            {'nome': 'Açougue', 'minimo': 50.0},
            {'nome': 'Padaria', 'minimo': 0.0},
            {'nome': 'Artesanais', 'minimo': 0.0}
        ]
        for cat_data in categorias:
            cat = Categoria(nome=cat_data['nome'],
                            valor_minimo=cat_data['minimo'])
            db.session.add(cat)
        db.session.commit()

    if not Usuario.query.filter_by(email="admin@coopvale.com").first():
        print("Criando Administrador...")
        admin_user = Usuario(
            email="admin@coopvale.com",
            senha_hash=generate_password_hash("admin123"),
            tipo_usuario="admin",
            ativo=True
        )
        db.session.add(admin_user)
        db.session.commit()

    if not Usuario.query.filter_by(email="produtor@coopvale.com").first():
        print("Criando Produtor...")
        produtor_user = Usuario(
            email="produtor@coopvale.com",
            senha_hash=generate_password_hash("123456"),
            tipo_usuario="produtor",
            ativo=True
        )
        db.session.add(produtor_user)
        db.session.commit()

        novo_produtor = Produtor(
            usuario_id=produtor_user.id,
            nome="João da Silva",
            cpf="111.222.333-44",
            telefone="(41) 99999-8888",
            endereco="Sítio Recanto Verde, Estrada Rural km 5",
            certificacoes="Orgânico Certificado"
        )
        db.session.add(novo_produtor)
        db.session.commit()

    if not Usuario.query.filter_by(email="cliente@coopvale.com").first():
        print("Criando Cliente...")
        cliente_user = Usuario(
            email="cliente@coopvale.com",
            senha_hash=generate_password_hash("123456"),
            tipo_usuario="cliente",
            ativo=True
        )
        db.session.add(cliente_user)
        db.session.commit()

        novo_cliente = Cliente(
            usuario_id=cliente_user.id,
            nome="Maria Compradora",
            cpf="999.888.777-66",
            telefone="(41) 98888-7777",
            receber_notificacoes=True
        )
        db.session.add(novo_cliente)
        db.session.commit()

    if not PontoRetirada.query.first():
        print("Criando Pontos de Retirada...")
        pontos = [
            PontoRetirada(nome="Sede da Cooperativa",
                          endereco="Rua das Flores, 123 - Centro", horarios="Seg-Sex, 08h-18h"),
            PontoRetirada(nome="Feira de Sábado",
                          endereco="Praça da Matriz", horarios="Sábados, 06h-12h")
        ]
        db.session.add_all(pontos)
        db.session.commit()

    if not Regiao.query.first():
        print("Criando Regiões de Entrega...")
        regioes = [
            Regiao(nome="Centro (Urbano)", taxa=5.00),
            Regiao(nome="Bairros Afastados", taxa=10.00),
            Regiao(nome="Zona Rural Próxima", taxa=15.00)
        ]
        db.session.add_all(regioes)
        db.session.commit()

    print("\n--- BANCO DE DADOS ATUALIZADO COM SUCESSO! ---")
    print("Login Admin: admin@coopvale.com / admin123")
    print("Login Produtor: produtor@coopvale.com / 123456")
    print("Login Cliente: cliente@coopvale.com / 123456")
