from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required
from app import db
from app.models import Insumo, Produto, Fornecedor

estoque_bp = Blueprint("estoque", __name__)


@estoque_bp.route("/estoque")
@login_required
def listar_estoque():
    insumos = Insumo.query.order_by(Insumo.nome).all()
    produtos_venda_direta = Produto.query.filter_by(tipo_estoque="venda_direta").order_by(Produto.nome).all()
    fornecedores = Fornecedor.query.order_by(Fornecedor.nome).all()
    return render_template(
        "estoque.html",
        insumos=insumos,
        produtos_venda_direta=produtos_venda_direta,
        fornecedores=fornecedores,
    )


@estoque_bp.route("/estoque/novo", methods=["GET", "POST"])
@login_required
def novo_insumo():
    fornecedores = Fornecedor.query.order_by(Fornecedor.nome).all()
    if request.method == "POST":
        insumo = Insumo(
            nome=request.form["nome"],
            unidade=request.form.get("unidade", "kg"),
            quantidade_atual=request.form["quantidade_atual"],
            quantidade_minima=request.form["quantidade_minima"],
            fornecedor_id=request.form.get("fornecedor_id") or None,
        )
        db.session.add(insumo)
        db.session.commit()
        flash("Insumo cadastrado com sucesso.")
        return redirect(url_for("estoque.listar_estoque"))
    return render_template("insumo_form.html", fornecedores=fornecedores)


@estoque_bp.route("/estoque/produto-direto/novo", methods=["GET", "POST"])
@login_required
def novo_produto_direto():
    fornecedores = Fornecedor.query.order_by(Fornecedor.nome).all()
    if request.method == "POST":
        codigo_barras = (request.form.get("codigo_barras") or "").strip()
        if not codigo_barras:
            codigo_barras = Produto.gerar_codigo_barras()

        produto = Produto(
            nome=request.form["nome"],
            categoria=request.form.get("categoria"),
            preco=request.form["preco"],
            codigo_barras=codigo_barras,
            tipo_estoque="venda_direta",
            unidade=request.form.get("unidade", "un"),
            estoque_atual=request.form.get("estoque_atual", 0),
            estoque_minimo=request.form.get("estoque_minimo", 0),
            fornecedor_id=request.form.get("fornecedor_id") or None,
        )
        db.session.add(produto)
        db.session.commit()
        flash("Produto de venda direta cadastrado com sucesso.")
        return redirect(url_for("estoque.listar_estoque"))
    return render_template("produto_form.html", fornecedores=fornecedores, tipo_estoque="venda_direta")


@estoque_bp.route("/estoque/fornecedores")
@login_required
def listar_fornecedores():
    fornecedores = Fornecedor.query.order_by(Fornecedor.nome).all()
    return render_template("fornecedores.html", fornecedores=fornecedores)


@estoque_bp.route("/estoque/fornecedores/novo", methods=["GET", "POST"])
@login_required
def novo_fornecedor():
    if request.method == "POST":
        fornecedor = Fornecedor(
            nome=request.form["nome"],
            contato=request.form["contato"],
            telefone=request.form.get("telefone"),
            email=request.form.get("email"),
            cnpj=request.form.get("cnpj"),
            observacao=request.form.get("observacao"),
        )
        db.session.add(fornecedor)
        db.session.commit()
        flash("Fornecedor cadastrado com sucesso.")
        return redirect(url_for("estoque.listar_fornecedores"))
    return render_template("fornecedor_form.html")


@estoque_bp.route("/estoque/fornecedores/<int:fornecedor_id>")
@login_required
def detalhe_fornecedor(fornecedor_id):
    fornecedor = Fornecedor.query.get_or_404(fornecedor_id)
    return render_template("fornecedor_detalhes.html", fornecedor=fornecedor)


@estoque_bp.route("/estoque/<int:insumo_id>/ajustar", methods=["POST"])
@login_required
def ajustar_estoque(insumo_id):
    insumo = Insumo.query.get_or_404(insumo_id)
    insumo.quantidade_atual = request.form["quantidade_atual"]
    db.session.commit()
    flash(f"Estoque de {insumo.nome} atualizado.")
    return redirect(url_for("estoque.listar_estoque"))


@estoque_bp.route("/estoque/produtos/<int:produto_id>/ajustar", methods=["POST"])
@login_required
def ajustar_estoque_produto(produto_id):
    produto = Produto.query.get_or_404(produto_id)
    produto.estoque_atual = request.form["estoque_atual"]
    db.session.commit()
    flash(f"Estoque de {produto.nome} atualizado.")
    return redirect(url_for("estoque.listar_estoque"))
