from flask import Flask
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
from sqlalchemy.dialects import sqlite


db = SQLAlchemy()
login_manager = LoginManager()


def ensure_schema(app):
    with app.app_context():
        inspector = db.inspect(db.engine)
        tables = set(inspector.get_table_names())

        from app.models import Fornecedor, Produto, Insumo, Usuario, Cliente, Venda, FichaTecnica, FechamentoCaixa

        models = [Fornecedor, Produto, Insumo, Usuario, Cliente, Venda, FichaTecnica, FechamentoCaixa]

        for model in models:
            table_name = model.__table__.name
            if table_name not in tables:
                db.create_all()
                return

            existing_columns = {column["name"] for column in inspector.get_columns(table_name)}
            for column in model.__table__.columns:
                if column.name not in existing_columns:
                    column_sql = column.type.compile(dialect=sqlite.dialect())
                    nullable_sql = " NOT NULL" if not column.nullable and not column.default and not column.primary_key else ""
                    default_sql = ""
                    if column.default is not None and not callable(column.default.arg):
                        default_sql = f" DEFAULT {column.default.arg}"
                    db.session.execute(text(f'ALTER TABLE "{table_name}" ADD COLUMN "{column.name}" {column_sql}{nullable_sql}{default_sql}'))
            db.session.commit()


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
        ensure_schema(app)

    return app
