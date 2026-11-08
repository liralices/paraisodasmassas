from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app import db


class Usuario(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    senha_hash = db.Column(db.String(255), nullable=False)
    cargo = db.Column(db.String(80), default="Atendente")

    @property
    def is_super_admin(self):
        cargo = str(self.cargo or "").strip().lower()
        return cargo in {"super administrador", "super-administrador", "super admin", "super-admin", "superadmin"}

    @property
    def is_admin(self):
        cargo = str(self.cargo or "").strip().lower()
        return self.is_super_admin or cargo in {"administrador", "admin"}

    def __init__(self, **kwargs):
        senha = kwargs.pop("senha", None)
        super().__init__(**kwargs)
        if senha is not None:
            self.set_senha(senha)

    def set_senha(self, senha):
        self.senha_hash = generate_password_hash(senha)

    def check_senha(self, senha):
        return check_password_hash(self.senha_hash, senha)

    def to_dict(self):
        return {
            "id": self.id,
            "nome": self.nome,
            "email": self.email,
            "cargo": self.cargo,
        }


class Fornecedor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(120), nullable=False)
    contato = db.Column(db.String(120), nullable=False)
    telefone = db.Column(db.String(30))
    email = db.Column(db.String(120))
    cnpj = db.Column(db.String(30))
    observacao = db.Column(db.Text)

    produtos = db.relationship("Produto", backref="fornecedor", lazy=True)
    insumos = db.relationship("Insumo", backref="fornecedor", lazy=True)

    @property
    def itens_baixos(self):
        itens = []
        for insumo in self.insumos:
            if insumo.estoque_baixo:
                itens.append({"tipo": "Matéria-prima", "nome": insumo.nome, "quantidade": insumo.quantidade_atual, "minimo": insumo.quantidade_minima, "unidade": insumo.unidade})
        for produto in self.produtos:
            if produto.tipo_estoque == "venda_direta" and produto.estoque_baixo:
                itens.append({"tipo": "Venda direta", "nome": produto.nome, "quantidade": produto.estoque_atual, "minimo": produto.estoque_minimo, "unidade": produto.unidade})
        return itens

    def to_dict(self):
        return {
            "id": self.id,
            "nome": self.nome,
            "contato": self.contato,
            "telefone": self.telefone,
            "email": self.email,
            "cnpj": self.cnpj,
            "observacao": self.observacao,
            "itens_baixos": self.itens_baixos,
        }


class Produto(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    categoria = db.Column(db.String(50))  # pão, doce, salgado, bebida...
    preco = db.Column(db.Numeric(10, 2), nullable=False)
    codigo_barras = db.Column(db.String(80), unique=True, nullable=True)
    tipo_estoque = db.Column(db.String(30), default="producao")
    unidade = db.Column(db.String(20), default="un")
    estoque_atual = db.Column(db.Numeric(10, 2), default=0)
    estoque_minimo = db.Column(db.Numeric(10, 2), default=0)
    fornecedor_id = db.Column(db.Integer, db.ForeignKey("fornecedor.id"))

    vendas = db.relationship("Venda", backref="produto", lazy=True)

    @property
    def estoque_baixo(self):
        if self.tipo_estoque != "venda_direta":
            return False
        return float(self.estoque_atual or 0) <= float(self.estoque_minimo or 0)

    def to_dict(self):
        return {
            "id": self.id,
            "nome": self.nome,
            "categoria": self.categoria,
            "preco": float(self.preco),
            "codigo_barras": self.codigo_barras,
            "tipo_estoque": self.tipo_estoque,
            "unidade": self.unidade,
            "estoque_atual": float(self.estoque_atual or 0),
            "estoque_minimo": float(self.estoque_minimo or 0),
            "fornecedor_id": self.fornecedor_id,
        }


class Venda(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    produto_id = db.Column(db.Integer, db.ForeignKey("produto.id"), nullable=False)
    quantidade = db.Column(db.Integer, nullable=False)
    data_hora = db.Column(db.DateTime, default=datetime.utcnow)

    @property
    def total(self):
        return float(self.produto.preco) * self.quantidade

    def to_dict(self):
        return {
            "id": self.id,
            "produto": self.produto.nome,
            "quantidade": self.quantidade,
            "total": self.total,
            "data_hora": self.data_hora.isoformat(),
        }


class Cliente(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(150), nullable=False)
    telefone = db.Column(db.String(20))
    localidade = db.Column(db.String(100))
    cpf_cnpj = db.Column(db.String(20))

    def to_dict(self):
        return {
            "id": self.id,
            "nome": self.nome,
            "telefone": self.telefone,
            "localidade": self.localidade,
            "cpf_cnpj": self.cpf_cnpj,
        }


class Insumo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)  # farinha, ovos, leite...
    unidade = db.Column(db.String(20), default="kg")
    quantidade_atual = db.Column(db.Numeric(10, 2), nullable=False, default=0)
    quantidade_minima = db.Column(db.Numeric(10, 2), nullable=False, default=0)
    fornecedor_id = db.Column(db.Integer, db.ForeignKey("fornecedor.id"))

    @property
    def estoque_baixo(self):
        return float(self.quantidade_atual or 0) <= float(self.quantidade_minima or 0)

    def to_dict(self):
        return {
            "id": self.id,
            "nome": self.nome,
            "unidade": self.unidade,
            "quantidade_atual": float(self.quantidade_atual),
            "quantidade_minima": float(self.quantidade_minima),
            "estoque_baixo": self.estoque_baixo,
            "fornecedor_id": self.fornecedor_id,
        }


class FichaTecnica(db.Model):
    """Quanto de cada insumo um produto consome — base da produção própria."""
    id = db.Column(db.Integer, primary_key=True)
    produto_id = db.Column(db.Integer, db.ForeignKey("produto.id"), nullable=False)
    insumo_id = db.Column(db.Integer, db.ForeignKey("insumo.id"), nullable=False)
    quantidade_utilizada = db.Column(db.Numeric(10, 3), nullable=False)

    produto = db.relationship("Produto", backref="ficha_tecnica")
    insumo = db.relationship("Insumo")


class FechamentoCaixa(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    data_abertura = db.Column(db.DateTime, default=datetime.utcnow)
    valor_abertura = db.Column(db.Numeric(10, 2), nullable=False, default=0)
    data_fechamento = db.Column(db.DateTime)
    valor_contado = db.Column(db.Numeric(10, 2))
    observacao = db.Column(db.String(255))

    @property
    def aberto(self):
        return self.data_fechamento is None

    def total_vendas_periodo(self):
        fim = self.data_fechamento or datetime.utcnow()
        vendas = Venda.query.filter(
            Venda.data_hora >= self.data_abertura, Venda.data_hora <= fim
        ).all()
        return sum(v.total for v in vendas)

    @property
    def valor_esperado(self):
        return float(self.valor_abertura) + self.total_vendas_periodo()

    @property
    def diferenca(self):
        if self.valor_contado is None:
            return None
        return float(self.valor_contado) - self.valor_esperado
