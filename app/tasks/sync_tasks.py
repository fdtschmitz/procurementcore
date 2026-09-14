from datetime import datetime
from app.extensions import db
from app.models.product import Product
from app.services.totvs_api import obter_produtos_paginados

def carga_inicial_produtos():
    offset = 0
    page_size = 100
    total_processado = 0
    
    while True:
        dados_rm = obter_produtos_paginados(offset=offset, page_size=page_size)
        
        # Interrompe se a lista vier vazia
        if not dados_rm:
            break
            
        for row in dados_rm:
            company_id = row.get('PRODUCTCOMPANYID')
            product_id = row.get('PRODUCTID')
            
            if company_id is None or product_id is None:
                continue
                
            produto = Product.query.filter_by(company_id=company_id, product_id=product_id).first()
            
            if not produto:
                produto = Product(company_id=company_id, product_id=product_id)
                db.session.add(produto)
                
            produto.code = row.get('CODE')
            produto.short_code = row.get('SHORTCODE')
            produto.description = row.get('DESCRIPTION')
            produto.material_type = row.get('MATERIALTYPE')
            produto.operational_nature = row.get('OPERATIONALNATURE')
            
        # Realiza o commit a cada bloco (página) para evitar sobrecarga de memória
        db.session.commit()
        
        total_processado += len(dados_rm)
        
        # Se a quantidade de registros retornados for menor que o page_size, chegamos ao fim
        if len(dados_rm) < page_size:
            break
            
        offset += page_size
        
    print(f"Carga inicial concluída: {total_processado} produtos sincronizados.")

def atualizar_produtos_delta(data_ultima_sync):
    """
    Busca apenas os produtos alterados/criados após a data especificada.
    Formato esperado de data_ultima_sync: 'YYYY-MM-DD HH:MM:SS'
    """
    offset = 0
    page_size = 100
    total_atualizados = 0
    total_novos = 0
    
    while True:
        dados_rm = obter_produtos_paginados(
            offset=offset, 
            page_size=page_size, 
            data_alteracao=data_ultima_sync
        )
        
        if not dados_rm:
            break
            
        for row in dados_rm:
            company_id = row.get('PRODUCTCOMPANYID')
            product_id = row.get('PRODUCTID')
            
            if company_id is None or product_id is None:
                continue
                
            produto = Product.query.filter_by(company_id=company_id, product_id=product_id).first()
            
            if not produto:
                produto = Product(company_id=company_id, product_id=product_id)
                db.session.add(produto)
                total_novos += 1
            else:
                total_atualizados += 1
                
            # Atualiza os dados independentemente de ser novo ou existente
            produto.code = row.get('CODE')
            produto.short_code = row.get('SHORTCODE')
            produto.description = row.get('DESCRIPTION')
            produto.material_type = row.get('MATERIALTYPE')
            produto.operational_nature = row.get('OPERATIONALNATURE')
            
        db.session.commit()
        
        if len(dados_rm) < page_size:
            break
            
        offset += page_size
        
    return {"novos": total_novos, "atualizados": total_atualizados}