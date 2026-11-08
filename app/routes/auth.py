from functools import wraps
from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required, login_user, logout_user
from app import db
from app.models import Usuario

auth_bp = Blueprint("auth", __name__)


def admin_required(f):
    @wraps(f)
    @login_required
    def decorated_function(*args, **kwargs):
        if not current_user.is_admin:
            flash("Você não tem permissão para acessar esta área.")
            return redirect(url_for("vendas.index"))
        return f(*args, **kwargs)
    return decorated_function


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        senha = request.form.get("senha", "")
        usuario = Usuario.query.filter_by(email=email).first()

        if usuario and usuario.check_senha(senha):
            login_user(usuario)
            flash("Login realizado com sucesso.")
            return redirect(request.args.get("next") or url_for("vendas.index"))

        flash("Email ou senha inválidos.")
        return render_template("login.html")

    return render_template("login.html")


@auth_bp.route("/cadastro", methods=["GET", "POST"])
def cadastro():
    if request.method == "POST":
        nome = request.form.get("nome", "").strip()
        email = request.form.get("email", "").strip().lower()
        senha = request.form.get("senha", "")
        cargo = request.form.get("cargo", "Atendente").strip() or "Atendente"

        if not nome or not email or not senha:
            flash("Preencha nome, email e senha.")
            return render_template("cadastro.html")

        if Usuario.query.filter_by(email=email).first():
            flash("Já existe um usuário cadastrado com esse email.")
            return render_template("cadastro.html")

        usuario = Usuario(nome=nome, email=email, cargo=cargo)
        usuario.set_senha(senha)
        db.session.add(usuario)
        db.session.commit()

        flash("Cadastro realizado com sucesso. Faça login para acessar o PADOC.")
        return redirect(url_for("auth.login"))

    return render_template("cadastro.html")


@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Você saiu do sistema.")
    return redirect(url_for("auth.login"))
