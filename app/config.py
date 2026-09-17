import os
import json

class Config:
    # Configurações Básicas do Flask
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-key-super-secreta')
    
    # Configuração do Banco de Dados (SQLite inicial, facilmente migrável para PostgreSQL)
    BASE_DIR = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///' + os.path.join(BASE_DIR, 'procurement.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Configuração do Celery/Redis para escalabilidade e background jobs
    CELERY_BROKER_URL = os.environ.get('CELERY_BROKER_URL', 'redis://localhost:6379/0')
    CELERY_RESULT_BACKEND = os.environ.get('CELERY_RESULT_BACKEND', 'redis://localhost:6379/0')

# Parâmetros da Consulta SQL
    TOTVS_SQL_COD_PRODUTOS = None
    TOTVS_SQL_COD_COLIGADA = None
    TOTVS_SQL_COD_SISTEMA = None
    TOTVS_SQL_REQ_CABECALHO = None
    TOTVS_SQL_REQ_ITENS = None
    DATA_ALTERACAO = None

    try:
        with open(os.path.join(BASE_DIR, 'secrets.json'), 'r') as f:
            secrets = json.load(f)
            TOTVS_BASE_URL = secrets.get('base_url')
            TOTVS_SERVICE_USER = secrets.get('service_username')
            TOTVS_SERVICE_PASS = secrets.get('service_password')
            TOTVS_SQL_COD_PRODUTOS = secrets.get('sql_cod_produtos')
            TOTVS_SQL_COD_COLIGADA = secrets.get('sql_cod_coligada')
            TOTVS_SQL_COD_SISTEMA = secrets.get('sql_cod_sistema')
            TOTVS_SQL_REQ_CABECALHO = secrets.get('sql_cod_req_cabecalho')
            TOTVS_SQL_REQ_ITENS = secrets.get('sql_cod_req_itens')
            DATA_ALTERACAO = secrets.get('data_alteracao')
    except FileNotFoundError:
        pass