# Importações necessárias para o funcionamento do Flask e manipulação do banco de dados
from flask import jsonify, request, render_template, redirect, url_for
from main import app
import sqlite3
import os
import pandas as pd

# Caminho para o banco de dados
DB_PATH = os.path.join(os.path.dirname(__file__), "../database/cadastros.db")

# ===========================
# Funções auxiliares
# ===========================

# Inicializa o banco de dados ao iniciar o app
def init_db():
    """
    Cria a tabela 'cadastros' no banco de dados se ela não existir.
    Essa tabela é usada para armazenar os dados básicos de cadastro.
    """
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

init_db()  # Chama a função para garantir que o banco está configurado

# ===========================
# Rotas principais
# ===========================

@app.route("/")
def homepage():
    """
    Renderiza a página inicial do projeto.
    """
    return render_template("index.html")

@app.route("/app")
def app_page():
    """
    Renderiza a página principal da aplicação.
    """
    return render_template("app.html")

# ===========================
# Gerenciamento de cadastros
# ===========================

@app.route("/cadastros", methods=["GET", "POST"])
def gerenciar_cadastros():
    """
    Gerencia os cadastros:
    - Exibe os cadastros existentes.
    - Permite adicionar novos cadastros.
    - Suporta a criação de colunas dinâmicas.
    """
    if request.method == "POST":
        # Obtém os dados do formulário
        nome = request.form.get("nome")
        last_name = request.form.get("last_name")
        age = request.form.get("age")
        email = request.form.get("email")

        # Obtém as novas colunas dinâmicas
        novas_colunas_nomes = request.form.getlist("nova_coluna_nome[]")
        novas_colunas_tipos = request.form.getlist("nova_coluna_tipo[]")

        # Valida os campos obrigatórios
        if not nome or not last_name or not age or not email:
            return render_template("cadastros.html", erro="Todos os campos fixos são obrigatórios!")

        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()

            # Cria novas colunas dinamicamente, se necessário
            for nome_coluna, tipo_coluna in zip(novas_colunas_nomes, novas_colunas_tipos):
                try:
                    cursor.execute(f"ALTER TABLE cadastros ADD COLUMN {nome_coluna} {tipo_coluna}")
                except sqlite3.OperationalError:
                    pass  # Ignora erros se a coluna já existir

            # Insere os valores no banco de dados
            colunas = ["nome", "last_name", "age", "email"] + novas_colunas_nomes
            valores = [nome, last_name, age, email] + [None] * len(novas_colunas_nomes)
            placeholders = ", ".join(["?"] * len(colunas))

            cursor.execute(f"INSERT INTO cadastros ({', '.join(colunas)}) VALUES ({placeholders})", valores)
            conn.commit()

        return redirect(url_for("gerenciar_cadastros"))

    # Exibe os cadastros e as colunas dinâmicas
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("PRAGMA table_info(cadastros)")
        colunas = [info[1] for info in cursor.fetchall() if info[1] not in ["id", "nome", "last_name", "age", "email"]]

        cursor.execute("SELECT * FROM cadastros")
        cadastros = [dict(zip([column[0] for column in cursor.description], row)) for row in cursor.fetchall()]

    return render_template("cadastros.html", cadastros=cadastros, colunas=colunas)

@app.route("/cadastros/<int:id>", methods=["GET"])
def buscar_cadastro(id):
    """
    Busca um cadastro específico pelo ID.
    Retorna os dados do cadastro em formato JSON.
    """
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

@app.route("/cadastros/<int:id>", methods=["DELETE"])
def remover_cadastro(id):
    """
    Remove um cadastro específico pelo ID.
    Retorna uma mensagem de sucesso ou erro.
    """
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM cadastros WHERE id = ?", (id,))
        conn.commit()

    if cursor.rowcount > 0:
        return jsonify({"mensagem": f"Cadastro com ID {id} removido com sucesso!"})
    return jsonify({"erro": "Cadastro não encontrado"}), 404

# ===========================
# Gerenciamento de tabelas
# ===========================

@app.route("/gerenciar_tabelas")
def gerenciar_tabelas():
    """
    Exibe todas as tabelas existentes no banco de dados.
    """
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tabelas = [row[0] for row in cursor.fetchall()]
    return render_template("cadastros.html", tabelas=tabelas)

@app.route("/criar_tabela", methods=["POST"])
def criar_tabela():
    """
    Cria uma nova tabela no banco de dados.
    """
    nome_tabela = request.form.get("nome_tabela")
    colunas = request.form.get("colunas")

    if not nome_tabela or not colunas:
        return render_template("cadastros.html", erro="Nome da tabela e colunas são obrigatórios!")

    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        try:
            cursor.execute(f"CREATE TABLE {nome_tabela} ({colunas})")
            conn.commit()
        except sqlite3.Error as e:
            return render_template("cadastros.html", erro=f"Erro ao criar tabela: {e}")
    return redirect(url_for("gerenciar_tabelas"))

@app.route("/apagar_tabelas", methods=["POST"])
def apagar_tabelas():
    """
    Apaga tabelas selecionadas do banco de dados.
    """
    tabelas_selecionadas = request.form.getlist("tabelas_selecionadas")

    if not tabelas_selecionadas:
        return render_template("cadastros.html", erro="Nenhuma tabela foi selecionada para apagar.")

    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        for tabela in tabelas_selecionadas:
            try:
                cursor.execute(f"DROP TABLE IF EXISTS {tabela}")
            except sqlite3.Error as e:
                print(f"Erro ao apagar a tabela {tabela}: {e}")
                return render_template("cadastros.html", erro=f"Erro ao apagar a tabela {tabela}.")
        conn.commit()

    return redirect(url_for("gerenciar_tabelas"))

@app.route("/apagar_colunas", methods=["POST"])
def apagar_colunas():
    """
    Apaga colunas selecionadas de uma tabela.
    """
    data = request.get_json()
    nome_tabela = data.get("nomeTabela")
    colunas = data.get("colunas")

    if not nome_tabela or not colunas:
        return jsonify({"error": "Nome da tabela e colunas são obrigatórios."}), 400

    try:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            for coluna in colunas:
                cursor.execute(f"ALTER TABLE {nome_tabela} DROP COLUMN {coluna}")
            conn.commit()
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ===========================
# Execução de queries
# ===========================

@app.route("/executar_query", methods=["POST"])
def executar_query():
    """
    Executa uma query SQL enviada pelo usuário.
    Diferencia queries de leitura (SELECT) e escrita (INSERT, UPDATE, DELETE).
    """
    query = request.form.get("query")

    if not query:
        return render_template("cadastros.html", erro="A query não pode estar vazia!")

    with sqlite3.connect(DB_PATH) as conn:
        try:
            # Verifica se a query é uma consulta (SELECT)
            if query.strip().lower().startswith("select"):
                # Usa pandas para executar a query e retornar os resultados
                df = pd.read_sql_query(query, conn)
                return render_template("cadastros.html", tabelas=[], resultado=df.to_html(classes="table"))
            else:
                # Para outras queries (INSERT, UPDATE, DELETE), usa o cursor do SQLite
                cursor = conn.cursor()
                cursor.execute(query)
                conn.commit()
                return render_template("cadastros.html", tabelas=[], resultado="Query executada com sucesso!")
        except sqlite3.Error as e:
            # Captura erros do SQLite e exibe para o usuário
            return render_template("cadastros.html", erro=f"Erro ao executar query: {e}")
        except pd.errors.DatabaseError as e:
            # Captura erros do pandas e exibe para o usuário
            return render_template("cadastros.html", erro=f"Erro ao executar query com pandas: {e}")

@app.route("/colunas/<nome_tabela>", methods=["GET"])
def listar_colunas(nome_tabela):
    """
    Retorna as colunas de uma tabela específica.
    """
    try:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute(f"PRAGMA table_info({nome_tabela})")
            colunas = [row[1] for row in cursor.fetchall()]  # O nome da coluna está no índice 1
        return jsonify({"colunas": colunas})
    except Exception as e:
        return jsonify({"error": str(e)}), 500