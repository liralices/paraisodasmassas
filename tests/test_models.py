import pytest
from app import create_app, db
from app.models import Produto, Venda, ItemVenda, Insumo, Cliente, FechamentoCaixa, FichaTecnica, Usuario, Fornecedor


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

    venda = Venda()
    venda.itens.append(ItemVenda(produto_id=produto.id, quantidade=10, preco_unitario=produto.preco))
    db.session.add(venda)
    db.session.commit()

    assert venda.total == 7.5


def test_venda_guarda_forma_pagamento_e_troco(app):
    produto = Produto(nome="Pão francês", categoria="pao", preco=0.75)
    db.session.add(produto)
    db.session.commit()

    venda = Venda(forma_pagamento="Dinheiro", valor_recebido=20.0, troco=5.0)
    venda.itens.append(ItemVenda(produto_id=produto.id, quantidade=10, preco_unitario=produto.preco))
    db.session.add(venda)
    db.session.commit()

    assert venda.forma_pagamento == "Dinheiro"
    assert venda.valor_recebido == 20.0
    assert venda.troco == 5.0


def test_venda_com_varios_itens_e_cliente(app):
    pao = Produto(nome="Pão francês", categoria="pao", preco=0.75)
    sonho = Produto(nome="Sonho", categoria="doce", preco=5.5)
    cliente = Cliente(nome="Eliana")
    db.session.add_all([pao, sonho, cliente])
    db.session.commit()

    venda = Venda(cliente_id=cliente.id)
    venda.itens.append(ItemVenda(produto_id=pao.id, quantidade=4, preco_unitario=pao.preco))
    venda.itens.append(ItemVenda(produto_id=sonho.id, quantidade=2, preco_unitario=sonho.preco))
    db.session.add(venda)
    db.session.commit()

    assert venda.total == 14.0
    assert venda.cliente.nome == "Eliana"


def test_produto_gera_codigo_de_barras_automaticamente(app):
    produto = Produto(nome="Pão francês", categoria="pao", preco=0.75)

    assert produto.codigo_barras is not None
    assert produto.codigo_barras.isdigit() is True
    assert len(produto.codigo_barras) == 13


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


def test_editar_cliente_e_produto_por_rotas(app):
    usuario = Usuario(nome="Admin", email="admin@teste.com", cargo="Administrador", senha="123456")
    cliente = Cliente(nome="Cliente antigo", telefone="(11) 1111-1111", localidade="São Paulo")
    produto = Produto(nome="Pão antigo", categoria="pao", preco=1.0, codigo_barras="7891111111111")
    db.session.add_all([usuario, cliente, produto])
    db.session.commit()

    cliente_app = app.test_client()
    login_response = cliente_app.post("/login", data={"email": "admin@teste.com", "senha": "123456"}, follow_redirects=True)
    assert login_response.status_code == 200

    response_cliente = cliente_app.post(
        f"/clientes/{cliente.id}/editar",
        data={"nome": "Cliente novo", "telefone": "(11) 2222-2222", "localidade": "Campinas", "cpf_cnpj": "123"},
        follow_redirects=True,
    )
    response_produto = cliente_app.post(
        f"/produtos/{produto.id}/editar",
        data={"nome": "Pão novo", "categoria": "pao", "preco": "7.50", "codigo_barras": "7892222222222", "tipo_estoque": "producao", "unidade": "un", "estoque_atual": "10", "estoque_minimo": "2", "fornecedor_id": ""},
        follow_redirects=True,
    )

    assert response_cliente.status_code == 200
    assert response_produto.status_code == 200
    assert Cliente.query.get(cliente.id).nome == "Cliente novo"
    assert Produto.query.get(produto.id).nome == "Pão novo"
    assert Produto.query.get(produto.id).preco == 7.5


def test_excluir_cliente_e_produto_por_rotas(app):
    usuario = Usuario(nome="Admin", email="admin@delete.com", cargo="Administrador", senha="123456")
    cliente = Cliente(nome="Cliente para remover", telefone="(11) 1234-5678", localidade="São Paulo")
    produto = Produto(nome="Produto para remover", categoria="doce", preco=3.5, codigo_barras="7893333333333")
    db.session.add_all([usuario, cliente, produto])
    db.session.commit()

    cliente_app = app.test_client()
    login_response = cliente_app.post("/login", data={"email": "admin@delete.com", "senha": "123456"}, follow_redirects=True)
    assert login_response.status_code == 200

    response_cliente = cliente_app.post(f"/clientes/{cliente.id}/excluir", follow_redirects=True)
    response_produto = cliente_app.post(f"/produtos/{produto.id}/excluir", follow_redirects=True)

    assert response_cliente.status_code == 200
    assert response_produto.status_code == 200
    assert Cliente.query.filter_by(id=cliente.id).first() is None
    assert Produto.query.filter_by(id=produto.id).first() is None


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

    venda = Venda()
    venda.itens.append(ItemVenda(produto_id=produto.id, quantidade=3, preco_unitario=produto.preco))
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


def test_usuario_super_admin_e_reconhecido_como_admin(app):
    usuario = Usuario(nome="Ana", email="ana@padoc.com", cargo="Super administrador", senha="padoc123")

    assert usuario.is_admin is True
    assert usuario.is_super_admin is True


def test_produto_com_codigo_de_barras_e_fornecedor(app):
    fornecedor = Fornecedor(nome="Distribuidora Nova", contato="Carlos", telefone="(11) 3333-4444", email="carlos@nova.com")
    produto = Produto(nome="Refrigerante 600ml", categoria="bebida", preco=7.5, codigo_barras="7891234567890", tipo_estoque="venda_direta", fornecedor=fornecedor, estoque_atual=30, estoque_minimo=10)

    assert produto.codigo_barras == "7891234567890"
    assert produto.tipo_estoque == "venda_direta"
    assert produto.estoque_baixo is False
    assert produto.fornecedor.nome == "Distribuidora Nova"


def test_fornecedor_exibe_contatos_e_itens_baixos(app):
    fornecedor = Fornecedor(nome="Matriz Alimentos", contato="Laura", telefone="(19) 99888-7766", email="laura@matriz.com")
    insumo = Insumo(nome="Leite", unidade="l", quantidade_atual=4, quantidade_minima=8, fornecedor=fornecedor)

    assert insumo.fornecedor.nome == "Matriz Alimentos"
    assert insumo.estoque_baixo is True
    assert "Laura" in fornecedor.contato
