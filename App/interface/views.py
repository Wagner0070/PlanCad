# Esse arquivo será para definir as rotas e deixar tudo organizadinho
# Importando o Flask, SQLite3 e o app principal
from flask import jsonify, request, render_template, redirect, url_for
from main import app
import sqlite3
import os
import pandas as pd

# Caminho para o banco de dados
DB_PATH = os.path.join(os.path.dirname(__file__), "../database/cadastros.db")

# Função para inicializar o banco de dados
def init_db():
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS cadastros (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                last_name TEXT NOT NULL,
                age INTEGER NOT NULL,
                email TEXT NOT NULL
            )
        """)
        conn.commit()

# Inicializa o banco de dados ao iniciar o app
init_db()

# Página inicial para apresentação do projeto
@app.route("/")
def homepage():
    return render_template("index.html")

# Página principal para o uso da aplicação
@app.route("/app")
def app_page():
    return render_template("app.html")

# Página para gerenciar cadastros
@app.route("/cadastros", methods=["GET", "POST"])
def gerenciar_cadastros():
    if request.method == "POST":
        nome = request.form.get("nome")
        last_name = request.form.get("last_name")
        age = request.form.get("age")
        email = request.form.get("email")

        novas_colunas_nomes = request.form.getlist("nova_coluna_nome[]")
        novas_colunas_tipos = request.form.getlist("nova_coluna_tipo[]")

        if not nome or not last_name or not age or not email:
            return render_template("cadastros.html", erro="Todos os campos fixos são obrigatórios!")

        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()

            # Criar novas colunas dinamicamente
            for nome_coluna, tipo_coluna in zip(novas_colunas_nomes, novas_colunas_tipos):
                try:
                    cursor.execute(f"ALTER TABLE cadastros ADD COLUMN {nome_coluna} {tipo_coluna}")
                except sqlite3.OperationalError:
                    pass

            # Inserir os valores no banco de dados
            colunas = ["nome", "last_name", "age", "email"] + novas_colunas_nomes
            valores = [nome, last_name, age, email] + [None] * len(novas_colunas_nomes)
            placeholders = ", ".join(["?"] * len(colunas))

            cursor.execute(f"INSERT INTO cadastros ({', '.join(colunas)}) VALUES ({placeholders})", valores)
            conn.commit()

        return redirect(url_for("gerenciar_cadastros"))

    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("PRAGMA table_info(cadastros)")
        colunas = [info[1] for info in cursor.fetchall() if info[1] not in ["id", "nome", "last_name", "age", "email"]]

        cursor.execute("SELECT * FROM cadastros")
        cadastros = [dict(zip([column[0] for column in cursor.description], row)) for row in cursor.fetchall()]

    return render_template("cadastros.html", cadastros=cadastros, colunas=colunas)

# Rota para buscar um cadastro por ID
@app.route("/cadastros/<int:id>", methods=["GET"])
def buscar_cadastro(id):
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, nome, last_name, age, email FROM cadastros WHERE id = ?", (id,))
        cadastro = cursor.fetchone()

    if cadastro:
        return jsonify({
            "mensagem": "Cadastro encontrado",
            "cadastro": {"id": cadastro[0], "nome": cadastro[1], "sobrenome": cadastro[2], "idade": cadastro[3], "email": cadastro[4]}
        })
    return jsonify({"erro": "Cadastro não encontrado"}), 404

# Rota para remover um cadastro por ID
@app.route("/cadastros/<int:id>", methods=["DELETE"])
def remover_cadastro(id):
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM cadastros WHERE id = ?", (id,))
        conn.commit()

    if cursor.rowcount > 0:
        return jsonify({"mensagem": f"Cadastro com ID {id} removido com sucesso!"})
    return jsonify({"erro": "Cadastro não encontrado"}), 404

@app.route("/cadastros/adicionar_classe", methods=["POST"])
def adicionar_classe():
    nome_classe = request.form.get("nome_classe")
    tipo_classe = request.form.get("tipo_classe")

    if not nome_classe or not tipo_classe:
        return render_template("cadastros.html", erro="O nome e o tipo da classe são obrigatórios!")

    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        try:
            # Adiciona uma nova coluna à tabela cadastros com o tipo especificado
            cursor.execute(f"ALTER TABLE cadastros ADD COLUMN {nome_classe} {tipo_classe}")
            conn.commit()
        except sqlite3.OperationalError:
            return render_template("cadastros.html", erro="Essa classe já existe ou o nome é inválido!")

    return redirect(url_for("gerenciar_cadastros"))

@app.route("/importar", methods=["GET", "POST"])
def importar_arquivo():
    tabela = None
    if request.method == "POST":
        arquivo = request.files.get("arquivo")
        if arquivo and arquivo.filename.endswith(".db"):
            caminho = os.path.join("uploads", arquivo.filename)
            arquivo.save(caminho)

            # Ler o banco de dados usando pandas
            with sqlite3.connect(caminho) as conn:
                query = "SELECT name FROM sqlite_master WHERE type='table';"
                tabelas = pd.read_sql(query, conn)
                if not tabelas.empty:
                    tabela_nome = tabelas.iloc[0, 0]
                    tabela = pd.read_sql(f"SELECT * FROM {tabela_nome}", conn)

    return render_template("importar.html", tabela=tabela)