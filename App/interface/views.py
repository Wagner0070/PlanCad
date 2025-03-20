# Esse arquivo será para definir as rotas e deixar tudo organizadinho
# Importando o Flask, SQLite3 e o app principal
from flask import jsonify, request
from main import app
import sqlite3
import os

# Caminho para o banco de dados
DB_PATH = os.path.join(os.path.dirname(__file__), "../database/cadastros.db")

# Função para inicializar o banco de dados
def init_db():
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS cadastros (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                date_time TEXT NOT NULL,
                nome TEXT NOT NULL,
                last_name TEXT NOT NULL,
                age INTEGER NOT NULL,
                email TEXT NOT NULL,
                return_date TEXT NOT NULL,
                return_date_time TEXT NOT NULL
            )
        """)
        conn.commit()

# Inicializa o banco de dados ao iniciar o app
init_db()

# Página inicial para apresentação do projeto
@app.route("/")
def homepage():
    return jsonify({
        "mensagem": "Bem-vindo ao projeto PlanCad!",
        "descricao": "Aqui você pode gerenciar cadastros de forma simples.",
        "rotas": {
            "/cadastros": "Listar todos os cadastros (GET)",
            "/cadastros": "Adicionar um novo cadastro (POST)",
            "/cadastros/<id>": "Buscar um cadastro por ID (GET)"
        }
    })

# Página principal para o uso da aplicação
@app.route("/app")
def app_page():
    return jsonify({
        "mensagem": "Bem vindo à aplicação PlanCad.",
        "descricao": "Aqui você pode começar a gerenciar os seus cadastros.",
        "instrucoes": [
            "Use a rota /cadastros para listar todos os cadastros.",
            "Use a rota /cadastros (POST) para adicionar novos cadastros.",
            "use a rota /cadastros/<id> para buscar um cadastro específico."
        ]
    })

# Rota para listar todos os cadastros
@app.route("/cadastros", methods=["GET"])
def listar_cadastros():
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM cadastros")
        cadastros = cursor.fetchall()
        return jsonify([{"id": row[0], "nome": row[1], "email": row[2]} for row in cadastros])

# Rota para adicionar um novo cadastro
@app.route("/cadastros", methods=["POST"])
def adicionar_cadastro():
    novo_cadastro = request.json
    nome = novo_cadastro.get("nome")
    email = novo_cadastro.get("email")

    if not nome or not email:
        return jsonify({"erro": "Nome e email são obrigatórios"}), 400

    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO cadastros (nome, email) VALUES (?, ?)", (nome, email))
        conn.commit()
        cadastro_id = cursor.lastrowid

    return jsonify({"mensagem": "Cadastro adicionado com sucesso!", "id": cadastro_id, "nome": nome, "email": email}), 201

# Rota para buscar um cadastro por ID
@app.route("/cadastros/<int:id>", methods=["GET"])
def buscar_cadastro(id):
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM cadastros WHERE id = ?", (id,))
        cadastro = cursor.fetchone()

    if cadastro:
        return jsonify({"id": cadastro[0], "nome": cadastro[1], "email": cadastro[2]})
    return jsonify({"erro": "Cadastro não encontrado"}), 404