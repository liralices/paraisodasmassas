from flask import Flask
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
from sqlalchemy.dialects import sqlite


db = SQLAlchemy()
login_manager = LoginManager()


def _migrar_vendas_antigas():
    """Converte o antigo formato de venda (1 produto por venda) para o novo
    formato de carrinho (uma venda com vários itens em ItemVenda)."""
    inspector = db.inspect(db.engine)
    tabelas = set(inspector.get_table_names())
    if "venda" not in tabelas or "item_venda" in tabelas:
        return

    colunas_venda = {column["name"] for column in inspector.get_columns("venda")}
    if "produto_id" not in colunas_venda:
        return

    from app.models import Venda, ItemVenda

    db.session.execute(text("ALTER TABLE venda RENAME TO venda_legado"))
    db.session.commit()

    Venda.__table__.create(db.engine)
    ItemVenda.__table__.create(db.engine)

    vendas_antigas = db.session.execute(
        text("SELECT id, produto_id, quantidade, data_hora FROM venda_legado")
    ).fetchall()
    for venda in vendas_antigas:
        produto = db.session.execute(
            text("SELECT preco FROM produto WHERE id = :id"), {"id": venda.produto_id}
        ).fetchone()
        preco = produto.preco if produto else 0
        db.session.execute(
            text("INSERT INTO venda (id, cliente_id, data_hora) VALUES (:id, NULL, :data_hora)"),
            {"id": venda.id, "data_hora": venda.data_hora},
        )
        db.session.execute(
            text(
                "INSERT INTO item_venda (venda_id, produto_id, quantidade, preco_unitario) "
                "VALUES (:venda_id, :produto_id, :quantidade, :preco)"
            ),
            {"venda_id": venda.id, "produto_id": venda.produto_id, "quantidade": venda.quantidade, "preco": preco},
        )
    db.session.commit()

    db.session.execute(text("DROP TABLE venda_legado"))
    db.session.commit()


def ensure_schema(app):
    with app.app_context():
        from app.models import Fornecedor, Produto, Insumo, Usuario, Cliente, Venda, ItemVenda, FichaTecnica, FechamentoCaixa

        _migrar_vendas_antigas()

        inspector = db.inspect(db.engine)
        tables = set(inspector.get_table_names())

        models = [Fornecedor, Produto, Insumo, Usuario, Cliente, Venda, ItemVenda, FichaTecnica, FechamentoCaixa]

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
