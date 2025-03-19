#criação do back end que faá a mágica de criar o banco de dados que terá seus valores setados pelo App/Interface/html/main.html
import sqlite3
import os

def create_database():
    #cria o banco de dados
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    #cria a tabela
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
        date TEXT NOT NULL,
        date_time TEXT NOT NULL,
        name TEXT NOT NULL,
        age INTEGER NOT NULL,
        email TEXT NOT NULL,
        date_return TEXT NOT NULL,
        datetime_return TEXT NOT NULL,
    );
    """)

    #salva as alterações
    conn.commit()
    conn.close()