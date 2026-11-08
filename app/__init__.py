from flask import Flask
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()
login_manager = LoginManager()


@login_manager.user_loader
def load_user(user_id):
    from app.models import Usuario

    return db.session.get(Usuario, int(user_id))


def create_app(config=None):
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///padoc.db"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["SECRET_KEY"] = "dev"  # trocar antes de ir para produção

    if config:
        app.config.update(config)

    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = "auth.login"

    from app.routes.vendas import vendas_bp
    from app.routes.estoque import estoque_bp
    from app.routes.api import api_bp
    from app.routes.clientes import clientes_bp
    from app.routes.ficha_tecnica import ficha_bp
    from app.routes.caixa import caixa_bp
    from app.routes.auth import auth_bp
    from app.routes.usuarios import usuarios_bp

    app.register_blueprint(vendas_bp)
    app.register_blueprint(estoque_bp)
    app.register_blueprint(api_bp)
    app.register_blueprint(clientes_bp)
    app.register_blueprint(ficha_bp)
    app.register_blueprint(caixa_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(usuarios_bp)

    with app.app_context():
        db.create_all()

    return app
