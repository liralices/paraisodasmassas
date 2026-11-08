from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required
from app import db
from app.models import Cliente

clientes_bp = Blueprint("clientes", __name__)


@clientes_bp.route("/clientes")
@login_required
def listar_clientes():
    busca = request.args.get("busca", "").strip()
    query = Cliente.query
    if busca:
        query = query.filter(Cliente.nome.ilike(f"%{busca}%"))
    clientes = query.order_by(Cliente.nome).all()
    return render_template("clientes.html", clientes=clientes, busca=busca)


@clientes_bp.route("/clientes/novo", methods=["GET", "POST"])
@login_required
def novo_cliente():
    if request.method == "POST":
        cliente = Cliente(
            nome=request.form["nome"],
            telefone=request.form.get("telefone"),
            localidade=request.form.get("localidade"),
            cpf_cnpj=request.form.get("cpf_cnpj"),
        )
        db.session.add(cliente)
        db.session.commit()
        flash("Cliente cadastrado com sucesso.")
        return redirect(url_for("clientes.listar_clientes"))
    return render_template("cliente_form.html")


@clientes_bp.route("/clientes/<int:cliente_id>/editar", methods=["GET", "POST"])
@login_required
def editar_cliente(cliente_id):
    cliente = Cliente.query.get_or_404(cliente_id)
    if request.method == "POST":
        cliente.nome = request.form.get("nome", cliente.nome).strip() or cliente.nome
        cliente.telefone = request.form.get("telefone")
        cliente.localidade = request.form.get("localidade")
        cliente.cpf_cnpj = request.form.get("cpf_cnpj")
        db.session.commit()
        flash("Cliente atualizado com sucesso.")
        return redirect(url_for("clientes.listar_clientes"))
    return render_template("cliente_form.html", cliente=cliente, editando=True)


@clientes_bp.route("/clientes/<int:cliente_id>/excluir", methods=["POST"])
@login_required
def excluir_cliente(cliente_id):
    cliente = Cliente.query.get_or_404(cliente_id)
    db.session.delete(cliente)
    db.session.commit()
    flash("Cliente removido com sucesso.")
    return redirect(url_for("clientes.listar_clientes"))
