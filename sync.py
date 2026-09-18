from app import create_app
from app.extensions import db

# Importe a nova rotina aqui
from app.tasks.sync_tasks import (
    carga_inicial_produtos, 
    sincronizar_solicitacoes_rm, 
    sincronizar_centros_custo_rm
)

app = create_app()

with app.app_context():
    print("Verificando/Criando tabelas no banco de dados...")
    db.create_all()
    
    # 1. Carrega Produtos
    print("Iniciando a carga de produtos do TOTVS RM...")
    carga_inicial_produtos()
    
    # 2. Carrega Centros de Custo
    print("Iniciando a carga de Centros de Custo do TOTVS RM...")
    sincronizar_centros_custo_rm()
    
    # 3. Carrega Solicitações de Compra
    print("Iniciando a carga de solicitações e itens do TOTVS RM...")
    sincronizar_solicitacoes_rm()
    
    print("Processos de sincronização finalizados com sucesso!")