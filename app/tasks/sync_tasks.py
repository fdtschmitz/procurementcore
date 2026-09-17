from datetime import datetime
from app.extensions import db
from app.models.product import Product
from app.models.request import PurchaseRequest, PurchaseRequestItem
from app.services.totvs_api import obter_produtos_paginados, executar_consulta_sql_rm
from flask import current_app

def carga_inicial_produtos():
    offset = 0
    page_size = 100
    total_processado = 0
    data_alteracao=current_app.config['DATA_ALTERACAO']
    
    while True:
        dados_rm = obter_produtos_paginados(offset=offset, page_size=page_size, data_alteracao=data_alteracao)
        
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

def sincronizar_solicitacoes_rm(data_ultima_sync=None):
    """
    Sincroniza cabeçalhos e itens das solicitações de compra do TOTVS RM.
    """
    sentenca_cabecalho = current_app.config['TOTVS_SQL_REQ_CABECALHO']
    sentenca_itens = current_app.config['TOTVS_SQL_REQ_ITENS']
    
    page_size = 100
    
    # ---------------------------------------------------------
    # 1. PROCESSAR CABEÇALHOS (INTER.001.2)
    # ---------------------------------------------------------
    offset = 0
    while True:
        dados_cabecalho = executar_consulta_sql_rm(
            cod_sentenca=sentenca_cabecalho, 
            offset=offset, 
            page_size=page_size, 
            data_alteracao=data_ultima_sync
        )
        
        if not dados_cabecalho:
            break
            
        for row in dados_cabecalho:
            id_mov = row.get('ID')
            if not id_mov:
                continue
                
            req = PurchaseRequest.query.get(id_mov)
            if not req:
                req = PurchaseRequest(id=id_mov)
                db.session.add(req)
            
            # Use 'NUMERO' caso adicione TMOV.NUMEROMOV na query. 
            # Fallback para string vazia para evitar erro de NOT NULL.
            req.numero = row.get('NUMERO', f"SC-{id_mov}") 
            
            # Conversão de string de data do RM para objeto datetime (Date) do Python
            raw_date = row.get('DATA_EMISSAO')
            if raw_date:
                try:
                    # RM costuma devolver formato ISO "YYYY-MM-DDTHH:MM:SS"
                    req.data_emissao = datetime.fromisoformat(raw_date.split('T')[0]).date()
                except ValueError:
                    pass

            raw_date2 = row.get('DATA_ATUALIZACAO')
            if raw_date2:
                try:
                    # RM costuma devolver formato ISO "YYYY-MM-DDTHH:MM:SS"
                    req.data_modificacao = datetime.fromisoformat(raw_date.split('T')[0]).date()
                except ValueError:
                    pass

            req.centro_custo = row.get('CENTRO_CUSTO')
            req.status = row.get('STATUS')
            req.status_compras = row.get('STATUS_COMPRAS')
            req.descricao = row.get('DESCRICAO')
            req.coligada = row.get('COLIGADA')
            req.tipo_mov = row.get('TIPO_MOV')
            req.solicitante = row.get('SOLICITANTE')
            req.status_concluido = row.get('STATUS_CONCLUIDO')
            
        db.session.commit()
        
        if len(dados_cabecalho) < page_size:
            break
        offset += page_size

    # ---------------------------------------------------------
    # 2. PROCESSAR ITENS (INTER.001.3)
    # ---------------------------------------------------------
    offset = 0
    while True:
        dados_itens = executar_consulta_sql_rm(
            cod_sentenca=sentenca_itens, 
            offset=offset, 
            page_size=page_size, 
            data_alteracao=data_ultima_sync
        )
        
        if not dados_itens:
            break
            
        for row in dados_itens:
            id_mov = row.get('ID')
            nseqitmmov = row.get('NSQITMMOV')
            
            # Pula se não houver referência de movimento
            if not id_mov or not nseqitmmov:
                continue
                
            # Verifica se o item já existe para evitar duplicação em atualizações delta
            # Aqui estamos usando a combinação ID do Movimento + Sequencial do RM
            item = PurchaseRequestItem.query.filter_by(
                request_id=id_mov, 
                codigo_item=row.get('COD_PRODUTO') # Como não mapeamos NSeqItmMov no BD, filtramos pelo Request e Produto
            ).first()
            
            if not item:
                item = PurchaseRequestItem(request_id=id_mov)
                db.session.add(item)
                
            item.codigo_item = row.get('COD_PRODUTO')
            item.descricao_item = row.get('PRODUTO')
            item.quantidade = row.get('QTD_ORIGINAL', 0)
            item.coligada = row.get('COLIGADA')
            item.nseqitmmov = nseqitmmov
            item.nseq = row.get('NSEQ')
            item.nat_op = row.get('NAT_OP')
            item.centro_custo = row.get('CENTRO_CUSTO')
            
        db.session.commit()
        
        if len(dados_itens) < page_size:
            break
        offset += page_size

    print("Sincronização de solicitações e itens concluída com sucesso!")