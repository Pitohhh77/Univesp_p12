from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import os

app = Flask(__name__)


# Tenta carregar a URL do BD da variável de ambiente (DATABASE_URL) que o Render ou Heroku irá fornecer.
# Se a variável não existir (rodando localmente), usa sua config local de fallback.
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get(
    'DATABASE_URL', 
    'postgresql://devuser:devsenha@localhost:5432/flaskdb'
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Modelo de usuário
class User(db.Model):
    __tablename__ = 'usuarios'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.Text, unique=True, nullable=False)
    password_hash = db.Column(db.Text, nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
with app.app_context():
    db.create_all()

@app.route("/")
def home():
    # renderiza a página HTML que está dentro da pasta templates
    return render_template("home.html")

#Tela de cadastro
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        usuario = request.form["usuario"]
        senha = request.form["senha"]

        # Verifica se já existe
        existing_user = User.query.filter_by(username=usuario).first()
        if existing_user:
            return render_template("register.html", erro="Usuário já existe!")

        novo_user = User(username=usuario)
        novo_user.set_password(senha)
        db.session.add(novo_user)
        db.session.commit()

        return redirect(url_for("login"))

    return render_template("register.html")

# Tela de login
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        usuario = request.form["usuario"]
        senha = request.form["senha"]

        user = User.query.filter_by(username=usuario).first()

        if user and user.check_password(senha):
            return redirect(url_for("dashboard"))
        else:
            return render_template("login.html", erro="Usuário ou senha incorretos")
    return render_template("login.html")


# Página inicial do dashboard
@app.route("/dashboard")
def dashboard():
    # Dados fictícios de ações do usuário
    acoes_usuario = [
        {"ticker": "AAPL", "preco": 182.30, "variacao": "+1.25%"},
        {"ticker": "TSLA", "preco": 230.15, "variacao": "-0.85%"},
        {"ticker": "AMZN", "preco": 145.90, "variacao": "+0.40%"},
    ]
    return render_template("dashboard.html", acoes=acoes_usuario)


if __name__ == "__main__":
    # Cria as tabelas no banco se não existirem
    with app.app_context():
        db.create_all()
    app.run(debug=True)
