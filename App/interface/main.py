# Começo do código, irei criar a página inicial do meu webapp em Flask
# Importando as bibliotecas necessárias
from flask import Flask
import os
import logging

# Configurando o app Flask
app = Flask(__name__)

# Importando as rotas e funcionalidades do views.py
try:
    from views import *
except ImportError as e:
    raise ImportError(f"Erro ao importar 'views': {e}")

# Configuração de logs para depuração
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Função principal para executar o servidor
if __name__ == "__main__":
    try:
        # Configurações dinâmicas de depuração e porta
        debug_mode = os.getenv("FLASK_DEBUG", "True").lower() == "true"
        port = int(os.getenv("FLASK_RUN_PORT", 5000))

        logger.info("Iniciando o servidor Flask...")
        logger.info(f"Modo de depuração: {'Ativado' if debug_mode else 'Desativado'}")
        logger.info(f"Servidor rodando na porta: {port}")

        # Executa o servidor
        app.run(debug=debug_mode, port=port)
    except Exception as e:
        logger.error(f"Erro ao iniciar o servidor: {e}")