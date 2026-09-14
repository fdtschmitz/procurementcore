import requests
from flask import current_app

def obter_produtos_paginados(offset=0, page_size=100, data_alteracao=None):
    base_url = current_app.config['TOTVS_BASE_URL']
    # Se houver data, podemos usar uma sentença SQL específica para o Delta, ou a mesma com parâmetro
    cod_sentenca = 'COMPRAS.PROD.DELTA' if data_alteracao else current_app.config['TOTVS_SQL_COD_SENTENCA']
    cod_coligada = current_app.config['TOTVS_SQL_COD_COLIGADA']
    cod_sistema = current_app.config['TOTVS_SQL_COD_SISTEMA']
    
    usuario = current_app.config['TOTVS_SERVICE_USER']
    senha = current_app.config['TOTVS_SERVICE_PASS']
    
    url = f"{base_url}/api/framework/v1/consultaSQLServer/RealizaConsulta/{cod_sentenca}/{cod_coligada}/{cod_sistema}"
    
    # Monta os parâmetros. O formato do RM para múltiplos parâmetros na string costuma ser separado por ponto e vírgula
    parametros_str = f"offset={offset};pageSize={page_size}"
    
    # Se a consulta SQL no RM tiver o parâmetro :DATA_ALTERACAO
    if data_alteracao:
        parametros_str += f";DATA_ALTERACAO={data_alteracao}"
    
    headers = {
        'accept': 'application/json;odata.metadata=minimal;odata.streaming=true'
    }
    
    try:
        response = requests.get(
            url, 
            params={'parameters': parametros_str}, 
            headers=headers, 
            auth=(usuario, senha)
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Erro na requisição de produtos: {e}")
        return []