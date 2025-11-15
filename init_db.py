# init_db.py

from app import app
from extensions import db # Se o seu objeto 'db' estiver em 'extensions.py'
from models import User, Investimento # Garante que os modelos sejam importados e reconhecidos pelo db

import sys
import os

# Função principal para criar as tabelas
def create_tables():
    # Deve rodar dentro do contexto da aplicação para acessar a DATABASE_URL
    with app.app_context():
        try:
            print("--- Iniciando criação de tabelas no Render... ---")
            
            # Chama a função do SQLAlchemy para criar todas as tabelas
            db.create_all()
            
            print("--- Tabelas criadas com sucesso ou já existentes. ---")
            
        except Exception as e:
            # Captura qualquer erro de conexão ou SQL e imprime
            print(f"ERRO CRÍTICO ao criar tabelas no banco de dados: {e}")
            print("Verifique se a DATABASE_URL está correta e ativa.")
            # Força a saída do processo com erro se houver falha na criação do DB
            sys.exit(1)

if __name__ == '__main__':
    create_tables()