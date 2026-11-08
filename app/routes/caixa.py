from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required
from app import db
from app.models import FechamentoCaixa

caixa_bp = Blueprint("caixa", __name__)


@caixa_bp.route("/caixa")
@login_required
def ver_caixa():
    caixa_aberto = FechamentoCaixa.query.filter_by(data_fechamento=None).first()
    historico = (
        FechamentoCaixa.query.filter(FechamentoCaixa.data_fechamento.isnot(None))
        .order_by(FechamentoCaixa.data_fechamento.desc())
        .limit(10)
        .all()
    )
    return render_template("caixa.html", caixa=caixa_aberto, historico=historico)


@caixa_bp.route("/caixa/abrir", methods=["POST"])
@login_required
def abrir_caixa():
    if FechamentoCaixa.query.filter_by(data_fechamento=None).first():
        flash("Já existe um caixa aberto.")
        return redirect(url_for("caixa.ver_caixa"))

    caixa = FechamentoCaixa(valor_abertura=request.form["valor_abertura"])
    db.session.add(caixa)
    db.session.commit()
    flash("Caixa aberto com sucesso.")
    return redirect(url_for("caixa.ver_caixa"))


@caixa_bp.route("/caixa/<int:caixa_id>/fechar", methods=["POST"])
@login_required
def fechar_caixa(caixa_id):
    caixa = FechamentoCaixa.query.get_or_404(caixa_id)
    caixa.data_fechamento = datetime.utcnow()
    caixa.valor_contado = request.form["valor_contado"]
    caixa.observacao = request.form.get("observacao")
    db.session.commit()
    flash("Caixa fechado com sucesso.")
    return redirect(url_for("caixa.ver_caixa"))


@caixa_bp.route("/caixa/<int:caixa_id>/editar", methods=["GET", "POST"])
@login_required
def editar_caixa(caixa_id):
    caixa = FechamentoCaixa.query.get_or_404(caixa_id)
    if request.method == "POST":
        caixa.valor_contado = request.form.get("valor_contado")
        caixa.observacao = request.form.get("observacao")
        db.session.commit()
        flash("Caixa atualizado com sucesso.")
        return redirect(url_for("caixa.ver_caixa"))
    return render_template("caixa_editar.html", caixa=caixa)


@caixa_bp.route("/caixa/<int:caixa_id>/excluir", methods=["POST"])
@login_required
def excluir_caixa(caixa_id):
    caixa = FechamentoCaixa.query.get_or_404(caixa_id)
    db.session.delete(caixa)
    db.session.commit()
    flash("Fechamento removido com sucesso.")
    return redirect(url_for("caixa.ver_caixa"))
