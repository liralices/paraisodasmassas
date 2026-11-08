from datetime import date
from flask import Blueprint, jsonify
from flask_login import login_required
from app import db
from app.models import Venda, ItemVenda, Insumo, Produto
from sqlalchemy import func

api_bp = Blueprint("api", __name__, url_prefix="/api")


@api_bp.route("/vendas-hoje")
@login_required
def vendas_hoje():
    """Todas as vendas registradas hoje, usadas pelo dashboard."""
    hoje = date.today()
    vendas = Venda.query.filter(func.date(Venda.data_hora) == hoje).all()
    return jsonify([v.to_dict() for v in vendas])


@api_bp.route("/produto-mais-vendido")
@login_required
def produto_mais_vendido():
    """Ranking de produtos por quantidade vendida (histórico completo)."""
    resultado = (
        db.session.query(
            Produto.nome, func.sum(ItemVenda.quantidade).label("total")
        )
        .join(ItemVenda, ItemVenda.produto_id == Produto.id)
        .group_by(Produto.nome)
        .order_by(func.sum(ItemVenda.quantidade).desc())
        .limit(5)
        .all()
    )
    return jsonify([{"produto": r.nome, "quantidade": r.total} for r in resultado])


@api_bp.route("/faturamento-por-dia")
@login_required
def faturamento_por_dia():
    """Faturamento agregado por dia, para o gráfico de tendência."""
    vendas = Venda.query.all()
    por_dia = {}
    for v in vendas:
        dia = v.data_hora.date().isoformat()
        por_dia[dia] = por_dia.get(dia, 0) + v.total
    dados = [{"dia": dia, "faturamento": total} for dia, total in sorted(por_dia.items())]
    return jsonify(dados)


@api_bp.route("/estoque-baixo")
@login_required
def estoque_baixo():
    """Lista consolidada de alertas de estoque para matérias-primas e itens de venda direta."""
    alertas = []

    for insumo in Insumo.query.order_by(Insumo.nome).all():
        if insumo.estoque_baixo:
            alertas.append({
                "id": insumo.id,
                "tipo": "Matéria-prima",
                "nome": insumo.nome,
                "quantidade_atual": float(insumo.quantidade_atual),
                "quantidade_minima": float(insumo.quantidade_minima),
                "unidade": insumo.unidade,
                "estoque_baixo": True,
                "fornecedor": insumo.fornecedor.nome if insumo.fornecedor else "Fornecedor não informado",
                "observacao": "Pedido de reposição pendente" if not insumo.fornecedor else "Contato disponível para compra",
                "dado_faltante": not bool(insumo.fornecedor),
            })

    for produto in Produto.query.filter_by(tipo_estoque="venda_direta").order_by(Produto.nome).all():
        if produto.estoque_baixo:
            alertas.append({
                "id": produto.id,
                "tipo": "Venda direta",
                "nome": produto.nome,
                "quantidade_atual": float(produto.estoque_atual or 0),
                "quantidade_minima": float(produto.estoque_minimo or 0),
                "unidade": produto.unidade,
                "estoque_baixo": True,
                "fornecedor": produto.fornecedor.nome if produto.fornecedor else "Fornecedor não informado",
                "observacao": "Código de barras ausente" if not produto.codigo_barras else "Revisar pedido do distribuidor",
                "dado_faltante": not bool(produto.codigo_barras) or not bool(produto.fornecedor),
            })

    return jsonify(alertas)
