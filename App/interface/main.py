#Começo do código, irei criar a página inicial do meu webapp em flask
#importando ás bibliotecas, sim, eu irei comentar tudo
from flask import Flask
app = Flask(__name__)

#Importando ás parafernalhas do views.py
from views import *

#Eu irei rodar isso em modo de depuração, quero caçar erros aqui
if __name__ == "__main__":
    app.run(debug = True)