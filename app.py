import yfinance as yf
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, login_required, current_user, logout_user
from models import User, Investimento
from werkzeug.security import check_password_hash
from datetime import datetime
import os
import plotly.express as px

# IMPORTAÇÃO CORRETA: Traz a função da Perplexity AI
from perplexity_ia import gerar_relatorio_carteira 

# importa o db de extensions, não de models
from extensions import db

app = Flask(__name__)

# Tenta carregar a URL do BD da variável de ambiente (DATABASE_URL) que o Render irá fornecer.
# Se a variável não existir (rodando localmente), usa sua config local de fallback.
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get(
    'DATABASE_URL', 
    'postgresql://postgres:postgres@localhost:5432/flaskdb'
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app) # inicializa SQLAlchemy com app

# CORREÇÃO CRÍTICA PARA O RENDER FREE:
# Este bloco cria as tabelas no BD remoto na primeira vez que o servidor inicia (via Gunicorn).
with app.app_context():
    db.create_all()
# -----------------------------------------------------------------

app.secret_key = 'univesppi2'

def get_cotacao_atual(ticker):
    try:
        tk = yf.Ticker(ticker)
        # Pega histórico diário mais recente
        hist = tk.history(period="1d")
        if not hist.empty:
            # Último preço de fechamento
            return float(hist['Close'][-1])
        else:
            return 0
    except Exception as e:
        print(f"Erro ao pegar cotação: {e}")
        return 0

# --------------------LOGIN---------------------

login_manager = LoginManager(app)
login_manager.login_view = "login"

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# -------------------- ROTAS --------------------

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        usuario = request.form["usuario"]
        email = request.form["email"]
        senha = request.form["senha"]
        confirm_senha = request.form["confirm_senha"]

        if senha != confirm_senha:
            return render_template("register.html", erro="As senhas não conferem!")

        existing_user = User.query.filter_by(username=usuario).first()
        if existing_user:
            return render_template("register.html", erro="Usuário já existe!")

        novo_user = User(username=usuario, email=email)
        novo_user.set_password(senha)
        db.session.add(novo_user)
        db.session.commit()

        return redirect(url_for("login"))

    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["usuario"]
        password = request.form["senha"]
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for("dashboard"))
        else:
            flash("Usuário ou senha inválidos")
    return render_template("login.html")

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("login"))

@app.route("/dashboard", methods=["GET", "POST"])
@login_required

def dashboard():

    data_atual = datetime.now()

    if request.method == "POST":
        nome = request.form["nome"]
        ticker = request.form["codigo_BVMF"].upper() + ".SA"
        quantidade = float(request.form["cotas"])
        valor_pago = float(request.form["valor_pago"])

        cotacao = get_cotacao_atual(ticker)

        saldo = cotacao * quantidade
        lucro_prejuizo = saldo - valor_pago

        novo = Investimento(
            ticker=ticker,
            nome=ticker,
            quantidade=quantidade,
            valor_pago=valor_pago,
            cotacao_atual=cotacao,
            saldo=saldo,
            lucro_prejuizo=lucro_prejuizo,
            user_id=current_user.id
        )

        db.session.add(novo)
        db.session.commit()
        return redirect(url_for("dashboard"))

    # listar os investimentos do usuário
    investimentos = Investimento.query.filter_by(user_id=current_user.id).all()

    # gráfico
    nomes = [i.ticker for i in investimentos]
    lucros = [i.lucro_prejuizo for i in investimentos]
    if nomes and lucros:
        fig = px.bar(x=nomes, y=lucros, title="Lucro/Prejuízo por investimento")
        grafico_html = fig.to_html(full_html=False)
    else:
        grafico_html = "<p>Nenhum investimento cadastrado ainda.</p>"

    return render_template(
        "dashboardv2.html",
        grafico_html=grafico_html,
        investimentos=investimentos,
        data_atual=data_atual
    )

@app.route("/investimento/remover/<int:investimento_id>")
@login_required
def remover_investimento(investimento_id):
    investimento = Investimento.query.get_or_404(investimento_id)

    # só permite remover se for do usuário logado
    if investimento.user_id != current_user.id:
        flash("Você não tem permissão para remover este investimento.", "danger")
        return redirect(url_for("dashboard"))

    db.session.delete(investimento)
    db.session.commit()
    flash("Investimento removido com sucesso!", "success")
    return redirect(url_for("dashboard"))

@app.route("/investimento/editar/<int:investimento_id>", methods=["GET", "POST"])
@login_required
def editar_investimento(investimento_id):
    investimento = Investimento.query.get_or_404(investimento_id)

    if investimento.user_id != current_user.id:
        flash("Você não tem permissão para editar este investimento.", "danger")
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        # Pega a nova quantidade e valor total pago do formulário
        quantidade = float(request.form["cotas"]) # Campo esperado no formulário de edição
        valor_pago = float(request.form["valor_pago"]) # Campo esperado no formulário de edição
        
        # O nome do ativo pode ser atualizado
        investimento.nome = request.form["nome"]
        investimento.quantidade = quantidade
        investimento.valor_pago = valor_pago
        
        # Recalcula com a cotação atualizada ou a última conhecida
        investimento.cotacao_atual = get_cotacao_atual(investimento.ticker)

        investimento.saldo = investimento.cotacao_atual * investimento.quantidade
        investimento.lucro_prejuizo = investimento.saldo - investimento.valor_pago

        db.session.commit()
        flash("Investimento atualizado com sucesso!", "success")
        return redirect(url_for("dashboard"))

    return render_template("editar_investimento.html", investimento=investimento)


@app.route("/relatorio", methods=["GET"])
@login_required
def relatorio():
    investimentos = Investimento.query.filter_by(user_id=current_user.id).all()
    try:
        # Converta os investimentos para dicionários para passar para a função de IA
        ativos = [
            {c.name: getattr(inv, c.name) for c in inv.table.columns}
            for inv in investimentos
        ]
        # Chama a função que usa a API da Perplexity
        relatorio_texto = gerar_relatorio_carteira(ativos, current_user.username)
    except Exception as e:
        # Tratamento de erro detalhado
        print(f"Erro ao gerar relatório com IA: {str(e)}")
        if "Chave de API da Perplexity não configurada" in str(e) or "401 Client Error" in str(e):
             relatorio_texto = "Erro: A **Chave de API da Perplexity (PERPLEXITY_API_KEY)** não está configurada ou é inválida. Por favor, verifique suas variáveis de ambiente."
        else:
             relatorio_texto = f"Erro ao gerar relatório com IA: {str(e)}"
             
    return render_template("relatorio.html", relatorio=relatorio_texto)

