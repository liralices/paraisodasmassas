from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required
from app import db
from app.models import Produto, Venda, ItemVenda, Insumo, FechamentoCaixa, Fornecedor, Cliente

vendas_bp = Blueprint("vendas", __name__)


@vendas_bp.route("/")
@login_required
def index():
    produtos = Produto.query.order_by(Produto.nome).all()
    caixa_aberto = FechamentoCaixa.query.filter_by(data_fechamento=None).first()
    insumos_em_alerta = sum(1 for i in Insumo.query.all() if i.estoque_baixo)
    produtos_venda_direta_em_alerta = sum(
        1 for p in Produto.query.filter_by(tipo_estoque="venda_direta").all() if p.estoque_baixo
    )
    total_alertas = insumos_em_alerta + produtos_venda_direta_em_alerta
    return render_template(
        "index.html",
        produtos=produtos,
        caixa_aberto=caixa_aberto,
        insumos_em_alerta=total_alertas,
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
        codigo_barras = (request.form.get("codigo_barras") or "").strip()
        if not codigo_barras:
            codigo_barras = Produto.gerar_codigo_barras()

        produto = Produto(
            nome=request.form["nome"],
            categoria=request.form.get("categoria"),
            preco=request.form["preco"],
            codigo_barras=codigo_barras,
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


@vendas_bp.route("/produtos/<int:produto_id>/editar", methods=["GET", "POST"])
@login_required
def editar_produto(produto_id):
    produto = Produto.query.get_or_404(produto_id)
    fornecedores = Fornecedor.query.order_by(Fornecedor.nome).all()
    if request.method == "POST":
        codigo_barras = (request.form.get("codigo_barras") or "").strip()
        if not codigo_barras:
            codigo_barras = Produto.gerar_codigo_barras()

        produto.nome = request.form.get("nome", produto.nome)
        produto.categoria = request.form.get("categoria")
        produto.preco = request.form["preco"]
        produto.codigo_barras = codigo_barras
        produto.tipo_estoque = request.form.get("tipo_estoque", produto.tipo_estoque or "producao")
        produto.unidade = request.form.get("unidade", produto.unidade or "un")
        produto.estoque_atual = request.form.get("estoque_atual", produto.estoque_atual or 0)
        produto.estoque_minimo = request.form.get("estoque_minimo", produto.estoque_minimo or 0)
        produto.fornecedor_id = request.form.get("fornecedor_id") or None
        db.session.commit()
        flash("Produto atualizado com sucesso.")
        return redirect(url_for("vendas.listar_produtos"))
    return render_template("produto_form.html", produto=produto, fornecedores=fornecedores, tipo_estoque=produto.tipo_estoque or "producao", editando=True)


@vendas_bp.route("/produtos/<int:produto_id>/excluir", methods=["POST"])
@login_required
def excluir_produto(produto_id):
    produto = Produto.query.get_or_404(produto_id)
    db.session.delete(produto)
    db.session.commit()
    flash("Produto removido com sucesso.")
    return redirect(url_for("vendas.listar_produtos"))


@vendas_bp.route("/vendas", methods=["GET", "POST"])
@login_required
def registrar_venda():
    if request.method == "POST":
        produto_ids = request.form.getlist("produto_id[]")
        quantidades = request.form.getlist("quantidade[]")
        cliente_id = request.form.get("cliente_id") or None
        forma_pagamento = request.form.get("forma_pagamento") or "Dinheiro"
        valor_recebido = request.form.get("valor_recebido") or "0"
        troco = request.form.get("troco") or "0"

        try:
            valor_recebido = float(valor_recebido)
        except (TypeError, ValueError):
            valor_recebido = 0.0

        try:
            troco = float(troco)
        except (TypeError, ValueError):
            troco = 0.0

        itens_validos = []
        for produto_id, quantidade in zip(produto_ids, quantidades):
            if not produto_id or not quantidade:
                continue
            quantidade = int(quantidade)
            if quantidade <= 0:
                continue
            itens_validos.append((int(produto_id), quantidade))

        if not itens_validos:
            flash("Adicione ao menos um item à venda.")
            return redirect(url_for("vendas.registrar_venda"))

        produtos_map = {
            p.id: p
            for p in Produto.query.filter(Produto.id.in_([pid for pid, _ in itens_validos])).all()
        }

        venda = Venda(
            cliente_id=int(cliente_id) if cliente_id else None,
            forma_pagamento=forma_pagamento,
            valor_recebido=valor_recebido,
            troco=troco,
        )
        for produto_id, quantidade in itens_validos:
            produto = produtos_map.get(produto_id)
            if not produto:
                continue
            venda.itens.append(
                ItemVenda(produto_id=produto_id, quantidade=quantidade, preco_unitario=produto.preco)
            )

        if not venda.itens:
            flash("Adicione ao menos um item válido à venda.")
            return redirect(url_for("vendas.registrar_venda"))

        if forma_pagamento == "Dinheiro" and valor_recebido < venda.total:
            flash("Valor recebido em dinheiro deve ser maior ou igual ao total da venda.")
            return redirect(url_for("vendas.registrar_venda"))

        if forma_pagamento != "Dinheiro":
            venda.valor_recebido = venda.total
            venda.troco = 0.0

        db.session.add(venda)
        db.session.commit()
        flash(f"Venda de R$ {venda.total:.2f} registrada com sucesso ({forma_pagamento}).")
        return redirect(url_for("vendas.registrar_venda"))

    produtos = Produto.query.order_by(Produto.nome).all()
    clientes = Cliente.query.order_by(Cliente.nome).all()
    vendas_recentes = Venda.query.order_by(Venda.data_hora.desc()).limit(20).all()
    return render_template("vendas.html", produtos=produtos, clientes=clientes, vendas=vendas_recentes)


@vendas_bp.route("/vendas/<int:venda_id>/editar", methods=["GET", "POST"])
@login_required
def editar_venda(venda_id):
    venda = Venda.query.get_or_404(venda_id)
    clientes = Cliente.query.order_by(Cliente.nome).all()
    if request.method == "POST":
        forma_pagamento = request.form.get("forma_pagamento") or "Dinheiro"
        valor_recebido = request.form.get("valor_recebido") or "0"
        troco = request.form.get("troco") or "0"

        try:
            valor_recebido = float(valor_recebido)
        except (TypeError, ValueError):
            valor_recebido = 0.0

        try:
            troco = float(troco)
        except (TypeError, ValueError):
            troco = 0.0

        venda.cliente_id = request.form.get("cliente_id") or None
        venda.forma_pagamento = forma_pagamento
        venda.valor_recebido = valor_recebido if forma_pagamento == "Dinheiro" else venda.total
        venda.troco = troco if forma_pagamento == "Dinheiro" else 0.0

        quantidade_map = request.form.getlist("quantidade")
        for item, quantidade in zip(venda.itens, quantidade_map):
            novo_valor = int(quantidade or 0)
            if novo_valor > 0:
                item.quantidade = novo_valor
        db.session.commit()
        flash("Venda atualizada com sucesso.")
        return redirect(url_for("vendas.registrar_venda"))
    return render_template("venda_editar.html", venda=venda, clientes=clientes)


@vendas_bp.route("/vendas/<int:venda_id>/excluir", methods=["POST"])
@login_required
def excluir_venda(venda_id):
    venda = Venda.query.get_or_404(venda_id)
    db.session.delete(venda)
    db.session.commit()
    flash("Venda removida com sucesso.")
    return redirect(url_for("vendas.registrar_venda"))
