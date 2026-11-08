from decimal import Decimal
from datetime import datetime, timedelta

from app import create_app, db
from app.models import (
    Usuario,
    Fornecedor,
    Produto,
    Insumo,
    Cliente,
    FichaTecnica,
    Venda,
    ItemVenda,
)


app = create_app({'SQLALCHEMY_DATABASE_URI': 'sqlite:///padoc.db'})

with app.app_context():
    db.session.query(ItemVenda).delete()
    db.session.query(Venda).delete()
    db.session.query(FichaTecnica).delete()
    db.session.query(Produto).delete()
    db.session.query(Insumo).delete()
    db.session.query(Cliente).delete()
    db.session.query(Fornecedor).delete()
    db.session.query(Usuario).delete()

    admin = Usuario(
        nome='Administrador PADOC',
        email='admin@padoc.com',
        cargo='Administrador',
        senha='123456',
    )
    atendente = Usuario(
        nome='Ana Atendente',
        email='atendente@padoc.com',
        cargo='Atendente',
        senha='123456',
    )
    db.session.add_all([admin, atendente])

    forn1 = Fornecedor(
        nome='Distribuidora Norte',
        contato='Marina Costa',
        telefone='(11) 3333-1010',
        email='marina@north.com',
        cnpj='12.345.678/0001-11',
    )
    forn2 = Fornecedor(
        nome='Matriz Alimentos',
        contato='Rafael Siqueira',
        telefone='(19) 99888-7788',
        email='rafael@matriz.com',
        cnpj='54.123.432/0001-98',
    )
    forn3 = Fornecedor(
        nome='Bebidas & Cia',
        contato='Patricia Lima',
        telefone='(21) 4002-2020',
        email='contato@bebidascia.com',
        cnpj='90.345.111/0001-22',
    )
    forn4 = Fornecedor(
        nome='Sabor & Forno',
        contato='Cristiano Nunes',
        telefone='(11) 98877-3311',
        email='cristiano@saborforno.com',
        cnpj='22.334.556/0001-05',
    )
    db.session.add_all([forn1, forn2, forn3, forn4])
    db.session.commit()

    farinha = Insumo(
        nome='Farinha de trigo',
        unidade='kg',
        quantidade_atual=Decimal('7.5'),
        quantidade_minima=Decimal('10'),
        fornecedor_id=forn4.id,
    )
    ovos = Insumo(
        nome='Ovos',
        unidade='un',
        quantidade_atual=Decimal('28'),
        quantidade_minima=Decimal('50'),
        fornecedor_id=forn1.id,
    )
    leite = Insumo(
        nome='Leite integral',
        unidade='l',
        quantidade_atual=Decimal('12'),
        quantidade_minima=Decimal('18'),
        fornecedor_id=forn2.id,
    )
    fermento = Insumo(
        nome='Fermento biológico',
        unidade='kg',
        quantidade_atual=Decimal('1.2'),
        quantidade_minima=Decimal('3'),
        fornecedor_id=forn1.id,
    )
    manteiga = Insumo(
        nome='Manteiga',
        unidade='kg',
        quantidade_atual=Decimal('4.8'),
        quantidade_minima=Decimal('6.5'),
        fornecedor_id=forn2.id,
    )
    acucar = Insumo(
        nome='Açúcar',
        unidade='kg',
        quantidade_atual=Decimal('5'),
        quantidade_minima=Decimal('8'),
        fornecedor_id=forn4.id,
    )
    queijo = Insumo(
        nome='Queijo muçarela',
        unidade='kg',
        quantidade_atual=Decimal('9'),
        quantidade_minima=Decimal('12'),
        fornecedor_id=forn2.id,
    )
    cafe = Insumo(
        nome='Café moído',
        unidade='kg',
        quantidade_atual=Decimal('2.1'),
        quantidade_minima=Decimal('4'),
        fornecedor_id=forn1.id,
    )
    db.session.add_all([farinha, ovos, leite, fermento, manteiga, acucar, queijo, cafe])
    db.session.commit()

    p1 = Produto(
        nome='Pão francês', categoria='pao', preco=Decimal('0.90'), codigo_barras='7890123456781',
        tipo_estoque='producao', unidade='un', estoque_atual=Decimal('120'), estoque_minimo=Decimal('40'),
        fornecedor_id=forn4.id,
    )
    p2 = Produto(
        nome='Sonho', categoria='doce', preco=Decimal('7.50'), codigo_barras='7890123456782',
        tipo_estoque='producao', unidade='un', estoque_atual=Decimal('80'), estoque_minimo=Decimal('30'),
        fornecedor_id=forn4.id,
    )
    p3 = Produto(
        nome='Croissant', categoria='doce', preco=Decimal('8.90'), codigo_barras='7890123456783',
        tipo_estoque='producao', unidade='un', estoque_atual=Decimal('60'), estoque_minimo=Decimal('25'),
        fornecedor_id=forn4.id,
    )
    p4 = Produto(
        nome='Coxinha', categoria='salgado', preco=Decimal('12.00'), codigo_barras='7890123456784',
        tipo_estoque='producao', unidade='un', estoque_atual=Decimal('90'), estoque_minimo=Decimal('35'),
        fornecedor_id=forn4.id,
    )
    p5 = Produto(
        nome='Torta de queijo', categoria='doce', preco=Decimal('18.00'), codigo_barras='7890123456785',
        tipo_estoque='producao', unidade='un', estoque_atual=Decimal('35'), estoque_minimo=Decimal('20'),
        fornecedor_id=forn4.id,
    )
    p6 = Produto(
        nome='Refrigerante 600ml', categoria='bebida', preco=Decimal('7.00'), codigo_barras=None,
        tipo_estoque='venda_direta', unidade='un', estoque_atual=Decimal('8'), estoque_minimo=Decimal('20'),
        fornecedor_id=forn3.id,
    )
    p7 = Produto(
        nome='Leite UHT 1L', categoria='bebida', preco=Decimal('5.90'), codigo_barras='7890456789012',
        tipo_estoque='venda_direta', unidade='un', estoque_atual=Decimal('12'), estoque_minimo=Decimal('18'),
        fornecedor_id=forn2.id,
    )
    p8 = Produto(
        nome='Bala de coco', categoria='doces', preco=Decimal('3.50'), codigo_barras=None,
        tipo_estoque='venda_direta', unidade='cx', estoque_atual=Decimal('5'), estoque_minimo=Decimal('15'),
        fornecedor_id=None,
    )
    p9 = Produto(
        nome='Água mineral 500ml', categoria='bebida', preco=Decimal('4.00'), codigo_barras='7890556789123',
        tipo_estoque='venda_direta', unidade='un', estoque_atual=Decimal('6'), estoque_minimo=Decimal('12'),
        fornecedor_id=forn3.id,
    )
    p10 = Produto(
        nome='Bolacha recheada', categoria='doce', preco=Decimal('6.20'), codigo_barras=None,
        tipo_estoque='venda_direta', unidade='cx', estoque_atual=Decimal('4'), estoque_minimo=Decimal('10'),
        fornecedor_id=forn1.id,
    )

    db.session.add_all([p1, p2, p3, p4, p5, p6, p7, p8, p9, p10])
    db.session.commit()

    db.session.add_all([
        FichaTecnica(produto_id=p1.id, insumo_id=farinha.id, quantidade_utilizada=Decimal('0.080')),
        FichaTecnica(produto_id=p1.id, insumo_id=fermento.id, quantidade_utilizada=Decimal('0.005')),
        FichaTecnica(produto_id=p2.id, insumo_id=farinha.id, quantidade_utilizada=Decimal('0.120')),
        FichaTecnica(produto_id=p2.id, insumo_id=ovos.id, quantidade_utilizada=Decimal('2')),
        FichaTecnica(produto_id=p2.id, insumo_id=acucar.id, quantidade_utilizada=Decimal('0.060')),
        FichaTecnica(produto_id=p3.id, insumo_id=farinha.id, quantidade_utilizada=Decimal('0.140')),
        FichaTecnica(produto_id=p3.id, insumo_id=manteiga.id, quantidade_utilizada=Decimal('0.070')),
        FichaTecnica(produto_id=p4.id, insumo_id=farinha.id, quantidade_utilizada=Decimal('0.110')),
        FichaTecnica(produto_id=p4.id, insumo_id=leite.id, quantidade_utilizada=Decimal('0.100')),
        FichaTecnica(produto_id=p5.id, insumo_id=farinha.id, quantidade_utilizada=Decimal('0.180')),
        FichaTecnica(produto_id=p5.id, insumo_id=ovos.id, quantidade_utilizada=Decimal('3')),
        FichaTecnica(produto_id=p5.id, insumo_id=queijo.id, quantidade_utilizada=Decimal('0.250')),
        FichaTecnica(produto_id=p5.id, insumo_id=leite.id, quantidade_utilizada=Decimal('0.150')),
        FichaTecnica(produto_id=p1.id, insumo_id=leite.id, quantidade_utilizada=Decimal('0.020')),
    ])
    db.session.commit()

    clientes = [
        Cliente(nome='João Pereira', telefone='(11) 98888-1234', localidade='São Paulo - SP', cpf_cnpj='123.456.789-00'),
        Cliente(nome='Maria Santos', telefone='(11) 97777-4444', localidade='Campinas - SP', cpf_cnpj='987.654.321-00'),
        Cliente(nome='Carlos Nunes', telefone='(19) 96555-0001', localidade='Jundiaí - SP', cpf_cnpj='111.222.333-44'),
        Cliente(nome='Lucia Mendes', telefone='(11) 95522-7788', localidade='Osasco - SP', cpf_cnpj='555.666.777-88'),
    ]
    db.session.add_all(clientes)
    db.session.commit()

    v1 = Venda(cliente_id=clientes[0].id, data_hora=datetime.utcnow() - timedelta(days=1))
    v2 = Venda(cliente_id=clientes[1].id, data_hora=datetime.utcnow() - timedelta(hours=6))
    v3 = Venda(cliente_id=clientes[2].id, data_hora=datetime.utcnow() - timedelta(hours=2))
    db.session.add_all([v1, v2, v3])
    db.session.flush()

    v1.itens.append(ItemVenda(produto_id=p1.id, quantidade=12, preco_unitario=p1.preco))
    v1.itens.append(ItemVenda(produto_id=p2.id, quantidade=8, preco_unitario=p2.preco))
    v1.itens.append(ItemVenda(produto_id=p6.id, quantidade=4, preco_unitario=p6.preco))

    v2.itens.append(ItemVenda(produto_id=p3.id, quantidade=6, preco_unitario=p3.preco))
    v2.itens.append(ItemVenda(produto_id=p7.id, quantidade=3, preco_unitario=p7.preco))

    v3.itens.append(ItemVenda(produto_id=p5.id, quantidade=5, preco_unitario=p5.preco))
    v3.itens.append(ItemVenda(produto_id=p9.id, quantidade=7, preco_unitario=p9.preco))

    db.session.commit()

    print(
        'DEMO_PADOC_OK',
        'Usuarios:', Usuario.query.count(),
        'Fornecedores:', Fornecedor.query.count(),
        'Insumos:', Insumo.query.count(),
        'Produtos:', Produto.query.count(),
        'Fichas:', FichaTecnica.query.count(),
        'Vendas:', Venda.query.count(),
    )
