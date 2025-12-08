from flask import Blueprint, render_template, redirect, request, flash, url_for
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user, login_required, current_user
from flask_mail import Message
from app import mail, create_app
from itsdangerous import URLSafeTimedSerializer
from app import db
from app.models.models import Usuario, Cliente, Produtor

auth_bp = Blueprint("auth", __name__, url_prefix="/auth", template_folder="templates")

def send_reset_email(user):
    s = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    token = s.dumps(user.email, salt='recover-key')
    
    msg = Message('Recuperação de Senha - CoopVale',
                  sender='noreply@coopvale.com',
                  recipients=[user.email])
                  
    link = url_for('auth.reset_token', token=token, _external=True)
    
    msg.body = f'''Para redefinir sua senha, clique no link a seguir:
{link}

Se você não fez essa solicitação, ignore este email.
'''
    mail.send(msg)

@auth_bp.route("/reset_password", methods=['GET', 'POST'])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
        
    if request.method == "POST":
        email = request.form.get('email')
        user = Usuario.query.filter_by(email=email).first()
        if user:
            send_reset_email(user)
            flash('Um email foi enviado com instruções para redefinir sua senha.', 'info')
            return redirect(url_for('auth.login'))
        else:
            flash('Email não encontrado.')
            
    return render_template('auth/reset_request.html')

# Rota 2: Link que vem no email
@auth_bp.route("/reset_password/<token>", methods=['GET', 'POST'])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('index'))
        
    s = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    try:
        email = s.loads(token, salt='recover-key', max_age=3600) 
    except:
        flash('O token é inválido ou expirou.', 'warning')
        return redirect(url_for('auth.reset_request'))
        
    if request.method == "POST":
        user = Usuario.query.filter_by(email=email).first()
        nova_senha = request.form.get('senha')
        user.senha_hash = generate_password_hash(nova_senha)
        db.session.commit()
        flash('Sua senha foi atualizada! Você pode fazer login agora.', 'success')
        return redirect(url_for('auth.login'))
        
    return render_template('auth/reset_token.html')

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        senha = request.form.get("senha")

        usuario = Usuario.query.filter_by(email=email).first()

        if usuario and check_password_hash(usuario.senha_hash, senha):
            login_user(usuario)
            return redirect(url_for('index'))
        else:
            flash("Email ou senha incorretos.")

    return render_template("auth/login.html")


@auth_bp.route("/registro", methods=["GET", "POST"])
def registro():
    if request.method == "POST":
        email = request.form.get("email")
        nome = request.form.get("nome")
        senha = request.form.get("senha")
        tipo = request.form.get("tipo_usuario") 
        
        if Usuario.query.filter_by(email=email).first():
            flash("Email já cadastrado.")
            return redirect(url_for('auth.registro'))
        
        novo_usuario = Usuario(
            email=email,
            senha_hash=generate_password_hash(senha),
            tipo_usuario=tipo 
        )
        db.session.add(novo_usuario)
        db.session.commit()
        
        if tipo == 'produtor':
            novo_produtor = Produtor(usuario_id=novo_usuario.id, nome=nome)
            db.session.add(novo_produtor)
        else:
            novo_cliente = Cliente(usuario_id=novo_usuario.id, nome=nome)
            db.session.add(novo_cliente)
            
        db.session.commit()
        
        login_user(novo_usuario)
        flash(f"Bem-vindo! Conta de {tipo} criada com sucesso.")
        
        if tipo == 'produtor':
            return redirect(url_for('produtor.painel'))
        return redirect(url_for('produtos.listar_produtos'))
        
    return render_template("auth/registro.html")


@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))
