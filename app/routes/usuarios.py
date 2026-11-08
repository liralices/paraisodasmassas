from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required
from app import db
from app.models import Usuario
from app.routes.auth import admin_required

usuarios_bp = Blueprint("usuarios", __name__)


@usuarios_bp.route("/usuarios")
@login_required
@admin_required
def listar_usuarios():
    usuarios = Usuario.query.order_by(Usuario.nome).all()
    return render_template("usuarios.html", usuarios=usuarios)


@usuarios_bp.route("/usuarios/permissoes")
@login_required
@admin_required
def permissoes():
    usuarios = Usuario.query.order_by(Usuario.nome).all()
    return render_template("permissoes.html", usuarios=usuarios)


@usuarios_bp.route("/usuarios/<int:usuario_id>/permissao", methods=["POST"])
@login_required
@admin_required
def atualizar_permissao(usuario_id):
    usuario = Usuario.query.get_or_404(usuario_id)

    if usuario.id == current_user.id:
        flash("Você não pode alterar seu próprio cargo.")
        return redirect(url_for("usuarios.permissoes"))

    cargo = request.form.get("cargo", "Atendente").strip() or "Atendente"
    usuario.cargo = cargo
    db.session.commit()
    flash(f"Permissão de {usuario.nome} atualizada para {usuario.cargo}.")
    return redirect(url_for("usuarios.permissoes"))


@usuarios_bp.route("/usuarios/novo", methods=["GET", "POST"])
@login_required
@admin_required
def novo_usuario():
    if request.method == "POST":
        nome = request.form.get("nome", "").strip()
        email = request.form.get("email", "").strip().lower()
        cargo = request.form.get("cargo", "Atendente").strip() or "Atendente"
        senha = request.form.get("senha", "")

        if not nome or not email or not senha:
            flash("Preencha nome, email e senha.")
            return render_template("usuario_form.html")

        if Usuario.query.filter_by(email=email).first():
            flash("Já existe um usuário com esse email.")
            return render_template("usuario_form.html")

        usuario = Usuario(nome=nome, email=email, cargo=cargo, senha=senha)
        db.session.add(usuario)
        db.session.commit()
        flash("Funcionário cadastrado com sucesso.")
        return redirect(url_for("usuarios.listar_usuarios"))

    return render_template("usuario_form.html")


@usuarios_bp.route("/usuarios/<int:usuario_id>/remover", methods=["POST"])
@login_required
@admin_required
def remover_usuario(usuario_id):
    usuario = Usuario.query.get_or_404(usuario_id)

    if usuario.id == current_user.id:
        flash("Você não pode remover seu próprio acesso.")
        return redirect(url_for("usuarios.listar_usuarios"))

    db.session.delete(usuario)
    db.session.commit()
    flash("Funcionário removido com sucesso.")
    return redirect(url_for("usuarios.listar_usuarios"))
