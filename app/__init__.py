from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = "auth.login" 
login_manager.login_message = "Faça login para acessar."

def create_app():
    app = Flask(__name__)
    app.config.from_object("config.Config")

    db.init_app(app)
    login_manager.init_app(app)

    from .models.models import Usuario

    @login_manager.user_loader
    def load_user(user_id):
        return Usuario.query.get(int(user_id))

    from .blueprints.auth.routes import auth_bp
    from .blueprints.produtos.routes import produtos_bp
    from .blueprints.admin.routes import admin_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(produtos_bp)
    app.register_blueprint(admin_bp)

    from flask import render_template
    @app.route("/")
    def index():
        return render_template("base.html")

    return app