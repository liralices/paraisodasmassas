from datetime import date
from flask import Blueprint, jsonify
from app import db
from app.models import Venda, Insumo, Produto
from sqlalchemy import func

api_bp = Blueprint("api", __name__, url_prefix="/api")


@api_bp.route("/vendas-hoje")
def vendas_hoje():
    """Todas as vendas registradas hoje, usadas pelo dashboard."""
    hoje = date.today()
    vendas = Venda.query.filter(func.date(Venda.data_hora) == hoje).all()
    return jsonify([v.to_dict() for v in vendas])


@api_bp.route("/produto-mais-vendido")
def produto_mais_vendido():
    """Ranking de produtos por quantidade vendida (histórico completo)."""
    resultado = (
        db.session.query(
            Produto.nome, func.sum(Venda.quantidade).label("total")
        )
        .join(Venda, Venda.produto_id == Produto.id)
        .group_by(Produto.nome)
        .order_by(func.sum(Venda.quantidade).desc())
        .limit(5)
        .all()
    )
    return jsonify([{"produto": r.nome, "quantidade": r.total} for r in resultado])


@api_bp.route("/faturamento-por-dia")
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
def estoque_baixo():
    """Insumos com quantidade igual ou abaixo do mínimo — usado para alertas em JS."""
    insumos = Insumo.query.all()
    return jsonify([i.to_dict() for i in insumos])
