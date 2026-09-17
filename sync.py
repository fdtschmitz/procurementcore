from app import create_app
from app.extensions import db
from app.tasks.sync_tasks import carga_inicial_produtos, sincronizar_solicitacoes_rm

# 1. Cria a instância da aplicação para carregar as configurações
app = create_app()

# 2. Entra no contexto da aplicação
with app.app_context():
    print("Verificando/Criando tabelas no banco de dados...")
    db.create_all()  # Cria o arquivo procurement.db e a tabela products, se não existirem
    
    print("Iniciando a carga de produtos do TOTVS RM...")
    carga_inicial_produtos()

    print("Iniciando a carga de solicitações e itens do TOTVS RM...")
    sincronizar_solicitacoes_rm()
    
    print("Processo finalizado com sucesso!")