import pytest
from app import create_app, db
from app.models import Produto, Venda, Insumo, Cliente, FechamentoCaixa, FichaTecnica, Usuario


@pytest.fixture
def app():
    app = create_app({"SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:", "TESTING": True})
    with app.app_context():
        yield app


def test_insumo_estoque_baixo(app):
    insumo = Insumo(nome="Farinha", quantidade_atual=2, quantidade_minima=5)
    assert insumo.estoque_baixo is True


def test_insumo_estoque_ok(app):
    insumo = Insumo(nome="Farinha", quantidade_atual=10, quantidade_minima=5)
    assert insumo.estoque_baixo is False


def test_venda_calcula_total(app):
    produto = Produto(nome="Pão francês", categoria="pao", preco=0.75)
    db.session.add(produto)
    db.session.commit()

    venda = Venda(produto_id=produto.id, quantidade=10)
    db.session.add(venda)
    db.session.commit()

    assert venda.total == 7.5


def test_produto_to_dict(app):
    produto = Produto(nome="Sonho", categoria="doce", preco=5.5)
    dados = produto.to_dict()
    assert dados["nome"] == "Sonho"
    assert dados["preco"] == 5.5


def test_cliente_to_dict(app):
    cliente = Cliente(nome="Eliana", telefone="(11) 90000-0000", localidade="São Paulo - SP")
    dados = cliente.to_dict()
    assert dados["nome"] == "Eliana"
    assert dados["localidade"] == "São Paulo - SP"


def test_fechamento_caixa_sem_venda(app):
    caixa = FechamentoCaixa(valor_abertura=100)
    db.session.add(caixa)
    db.session.commit()
    assert caixa.aberto is True
    assert caixa.valor_esperado == 100.0


def test_fechamento_caixa_com_venda(app):
    produto = Produto(nome="Croissant", categoria="doce", preco=6.0)
    db.session.add(produto)
    db.session.commit()

    caixa = FechamentoCaixa(valor_abertura=50)
    db.session.add(caixa)
    db.session.commit()

    venda = Venda(produto_id=produto.id, quantidade=3)
    db.session.add(venda)
    db.session.commit()

    assert caixa.valor_esperado == 50 + 18.0  # 50 abertura + 3 * 6.00

    caixa.valor_contado = 68.0
    assert caixa.diferenca == 0.0


def test_ficha_tecnica_vincula_insumo_a_produto(app):
    produto = Produto(nome="Pão francês", categoria="pao", preco=0.75)
    insumo = Insumo(nome="Farinha", quantidade_atual=20, quantidade_minima=5)
    db.session.add_all([produto, insumo])
    db.session.commit()

    item = FichaTecnica(produto_id=produto.id, insumo_id=insumo.id, quantidade_utilizada=0.1)
    db.session.add(item)
    db.session.commit()

    assert produto.ficha_tecnica[0].insumo.nome == "Farinha"


def test_usuario_cria_hash_e_valida_senha(app):
    usuario = Usuario(nome="Maria", email="maria@padoc.com", senha="padoc123")

    assert usuario.email == "maria@padoc.com"
    assert usuario.senha_hash != "padoc123"
    assert usuario.check_senha("padoc123") is True
    assert usuario.check_senha("errada") is False
