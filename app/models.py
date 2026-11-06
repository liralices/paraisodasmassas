from datetime import datetime
from app import db


class Produto(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    categoria = db.Column(db.String(50))  # pão, doce, salgado, bebida...
    preco = db.Column(db.Numeric(10, 2), nullable=False)

    vendas = db.relationship("Venda", backref="produto", lazy=True)

    def to_dict(self):
        return {
            "id": self.id,
            "nome": self.nome,
            "categoria": self.categoria,
            "preco": float(self.preco),
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

    @property
    def estoque_baixo(self):
        return self.quantidade_atual <= self.quantidade_minima

    def to_dict(self):
        return {
            "id": self.id,
            "nome": self.nome,
            "unidade": self.unidade,
            "quantidade_atual": float(self.quantidade_atual),
            "quantidade_minima": float(self.quantidade_minima),
            "estoque_baixo": self.estoque_baixo,
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
