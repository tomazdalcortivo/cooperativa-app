from app import create_app, db
from app.models.models import Categoria, Usuario, Produtor
from werkzeug.security import generate_password_hash

app = create_app()

with app.app_context():
    db.create_all()
    
    if not Categoria.query.first():
        print("Criando categorias iniciais...")
        cats = ['Hortifruti', 'Laticínios', 'Açougue', 'Padaria', 'Artesanais']
        for nome in cats:
            db.session.add(Categoria(nome=nome))
            
        senha = generate_password_hash("123456")
        user_prod = Usuario(email="produtor@coopvale.com", senha_hash=senha, tipo_usuario="produtor")
        db.session.add(user_prod)
        db.session.commit() 
        
        produtor = Produtor(usuario_id=user_prod.id, nome="João da Silva", telefone="9999-8888")
        db.session.add(produtor)
        
        db.session.commit()
        print("Banco de dados inicializado com sucesso!")
    else:
        print("Banco de dados já existe.")