from flask import Flask
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


def create_app(config=None):
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///giro.db"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["SECRET_KEY"] = "dev"  # trocar antes de ir para produção

    if config:
        app.config.update(config)

    db.init_app(app)

    from app.routes.vendas import vendas_bp
    from app.routes.estoque import estoque_bp
    from app.routes.api import api_bp
    from app.routes.clientes import clientes_bp
    from app.routes.ficha_tecnica import ficha_bp
    from app.routes.caixa import caixa_bp

    app.register_blueprint(vendas_bp)
    app.register_blueprint(estoque_bp)
    app.register_blueprint(api_bp)
    app.register_blueprint(clientes_bp)
    app.register_blueprint(ficha_bp)
    app.register_blueprint(caixa_bp)

    with app.app_context():
        db.create_all()

    return app
