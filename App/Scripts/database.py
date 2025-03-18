# filepath: /home/wagner/Documentos/projetos/PlanCad/App/scripts/database.py
import sqlite3

conn = sqlite3.connect('Cadastros.db')
cursor = conn.cursor()

# Criação de tabela caso não exista
cursor.execute("""
CREATE TABLE IF NOT EXISTS cadastros (
    id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    data TEXT NOT NULL,
    hora TEXT NOT NULL,
    nome TEXT NOT NULL,
    idade INTEGER NOT NULL,
    email TEXT NOT NULL,
    data_retorno TEXT NOT NULL,
    hora_retorno TEXT NOT NULL
);
""")
conn.commit()

def inserir(data, hora, nome, idade, email, data_retorno, hora_retorno):
    cursor.execute("""
    INSERT INTO cadastros (data, hora, nome, idade, email, data_retorno, hora_retorno) VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (data, hora, nome, idade, email, data_retorno, hora_retorno))
    conn.commit()

def listar():
    cursor.execute("SELECT * FROM cadastros")
    return cursor.fetchall()