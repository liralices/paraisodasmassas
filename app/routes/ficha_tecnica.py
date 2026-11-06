from flask import Blueprint, render_template, request, redirect, url_for, flash
from app import db
from app.models import Produto, Insumo, FichaTecnica

ficha_bp = Blueprint("ficha", __name__)


@ficha_bp.route("/ficha-tecnica")
def listar_fichas():
    produtos = Produto.query.order_by(Produto.nome).all()
    insumos = Insumo.query.order_by(Insumo.nome).all()
    return render_template("ficha_tecnica.html", produtos=produtos, insumos=insumos)


@ficha_bp.route("/ficha-tecnica/<int:produto_id>/adicionar", methods=["POST"])
def adicionar_item(produto_id):
    item = FichaTecnica(
        produto_id=produto_id,
        insumo_id=request.form["insumo_id"],
        quantidade_utilizada=request.form["quantidade_utilizada"],
    )
    db.session.add(item)
    db.session.commit()
    flash("Item adicionado à ficha técnica.")
    return redirect(url_for("ficha.listar_fichas"))


@ficha_bp.route("/ficha-tecnica/item/<int:item_id>/remover", methods=["POST"])
def remover_item(item_id):
    item = FichaTecnica.query.get_or_404(item_id)
    db.session.delete(item)
    db.session.commit()
    flash("Item removido da ficha técnica.")
    return redirect(url_for("ficha.listar_fichas"))
