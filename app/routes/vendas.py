from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required
from app import db
from app.models import Produto, Venda, Insumo, FechamentoCaixa, Fornecedor

vendas_bp = Blueprint("vendas", __name__)


@vendas_bp.route("/")
@login_required
def index():
    produtos = Produto.query.order_by(Produto.nome).all()
    caixa_aberto = FechamentoCaixa.query.filter_by(data_fechamento=None).first()
    insumos_em_alerta = sum(1 for i in Insumo.query.all() if i.estoque_baixo)
    return render_template(
        "index.html",
        produtos=produtos,
        caixa_aberto=caixa_aberto,
        insumos_em_alerta=insumos_em_alerta,
    )


@vendas_bp.route("/produtos")
@login_required
def listar_produtos():
    produtos = Produto.query.order_by(Produto.nome).all()
    return render_template("produtos.html", produtos=produtos)


@vendas_bp.route("/produtos/novo", methods=["GET", "POST"])
@login_required
def novo_produto():
    fornecedores = Fornecedor.query.order_by(Fornecedor.nome).all()
    if request.method == "POST":
        produto = Produto(
            nome=request.form["nome"],
            categoria=request.form.get("categoria"),
            preco=request.form["preco"],
            codigo_barras=request.form.get("codigo_barras") or None,
            tipo_estoque=request.form.get("tipo_estoque", "producao"),
            unidade=request.form.get("unidade", "un"),
            estoque_atual=request.form.get("estoque_atual", 0),
            estoque_minimo=request.form.get("estoque_minimo", 0),
            fornecedor_id=request.form.get("fornecedor_id") or None,
        )
        db.session.add(produto)
        db.session.commit()
        flash("Produto cadastrado com sucesso.")
        return redirect(url_for("vendas.listar_produtos"))
    return render_template("produto_form.html", fornecedores=fornecedores, tipo_estoque="producao")


@vendas_bp.route("/vendas", methods=["GET", "POST"])
@login_required
def registrar_venda():
    if request.method == "POST":
        venda = Venda(
            produto_id=request.form["produto_id"],
            quantidade=int(request.form["quantidade"]),
        )
        db.session.add(venda)
        db.session.commit()
        flash("Venda registrada com sucesso.")
        return redirect(url_for("vendas.registrar_venda"))

    produtos = Produto.query.order_by(Produto.nome).all()
    vendas_hoje = (
        Venda.query.order_by(Venda.data_hora.desc()).limit(20).all()
    )
    return render_template("vendas.html", produtos=produtos, vendas=vendas_hoje)
