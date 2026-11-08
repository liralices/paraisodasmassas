from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required
from app import db
from app.models import Insumo

estoque_bp = Blueprint("estoque", __name__)


@estoque_bp.route("/estoque")
@login_required
def listar_estoque():
    insumos = Insumo.query.order_by(Insumo.nome).all()
    return render_template("estoque.html", insumos=insumos)


@estoque_bp.route("/estoque/novo", methods=["GET", "POST"])
@login_required
def novo_insumo():
    if request.method == "POST":
        insumo = Insumo(
            nome=request.form["nome"],
            unidade=request.form.get("unidade", "kg"),
            quantidade_atual=request.form["quantidade_atual"],
            quantidade_minima=request.form["quantidade_minima"],
        )
        db.session.add(insumo)
        db.session.commit()
        flash("Insumo cadastrado com sucesso.")
        return redirect(url_for("estoque.listar_estoque"))
    return render_template("insumo_form.html")


@estoque_bp.route("/estoque/<int:insumo_id>/ajustar", methods=["POST"])
@login_required
def ajustar_estoque(insumo_id):
    insumo = Insumo.query.get_or_404(insumo_id)
    insumo.quantidade_atual = request.form["quantidade_atual"]
    db.session.commit()
    flash(f"Estoque de {insumo.nome} atualizado.")
    return redirect(url_for("estoque.listar_estoque"))
