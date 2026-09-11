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

    # Carregamento de credenciais da API 
    TOTVS_BASE_URL = None
    TOTVS_SERVICE_USER = None
    TOTVS_SERVICE_PASS = None

    try:
        with open(os.path.join(BASE_DIR, 'secrets.json'), 'r') as f:
            secrets = json.load(f)
            TOTVS_BASE_URL = secrets.get('base_url')
            TOTVS_SERVICE_USER = secrets.get('service_username')
            TOTVS_SERVICE_PASS = secrets.get('service_password')
    except FileNotFoundError:
        pass