import requests
from flask import current_app

def obter_produtos_paginados(offset=0, page_size=100, data_alteracao=None):

    if not data_alteracao:
        data_alteracao = "2020-01-01"

    base_url = current_app.config['TOTVS_BASE_URL']
    cod_sentenca = current_app.config['TOTVS_SQL_COD_PRODUTOS']
    cod_coligada = current_app.config['TOTVS_SQL_COD_COLIGADA']
    cod_sistema = current_app.config['TOTVS_SQL_COD_SISTEMA']
    
    usuario = current_app.config['TOTVS_SERVICE_USER']
    senha = current_app.config['TOTVS_SERVICE_PASS']
    
    url = f"{base_url}/api/framework/v1/consultaSQLServer/RealizaConsulta/{cod_sentenca}/{cod_coligada}/{cod_sistema}"
    
    # Monta os parâmetros. O formato do RM para múltiplos parâmetros na string costuma ser separado por ponto e vírgula
    parametros_str = f"DATA_ULTIMA_SYNC={data_alteracao};offset={offset};pageSize={page_size}"
        
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


def executar_consulta_sql_rm(cod_sentenca, offset=0, page_size=100, data_alteracao=None):
    """
    Executa uma consulta SQL genérica no TOTVS RM via endpoint RealizaConsulta.
    """
    base_url = current_app.config['TOTVS_BASE_URL']
    cod_coligada = current_app.config['TOTVS_SQL_COD_COLIGADA']
    cod_sistema = current_app.config['TOTVS_SQL_COD_SISTEMA']
    
    usuario = current_app.config['TOTVS_SERVICE_USER']
    senha = current_app.config['TOTVS_SERVICE_PASS']
    
    url = f"{base_url}/api/framework/v1/consultaSQLServer/RealizaConsulta/{cod_sentenca}/{cod_coligada}/{cod_sistema}"
    
    parametros_str = f"offset={offset};pageSize={page_size}"
    if data_alteracao:
        parametros_str += f";DATA_ULTIMA_SYNC={data_alteracao}"
    
    # Adicionamos o Content-Type para garantir a compatibilidade do POST
    headers = {
        'accept': 'application/json;odata.metadata=minimal;odata.streaming=true',
        'Content-Type': 'application/json'
    }
    
    try:
        response = requests.get(
            url, 
            params={'parameters': parametros_str}, # O RM aceita os parâmetros na query string mesmo no POST
            headers=headers, 
            auth=(usuario, senha)
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Erro na execução da sentença {cod_sentenca}: {e}")
        # Caso o erro seja do ERP (ex: 400 ou 500), podemos capturar a mensagem detalhada
        if e.response is not None:
            print("Detalhes do RM:", e.response.text)
        return []