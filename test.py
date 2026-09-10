import json
import requests
from flask import Flask, jsonify

app = Flask(__name__)

def load_secrets():
    with open('secrets.json', 'r') as file:
        return json.load(file)

@app.route('/api/criar-solicitacao', methods=['POST'])
def criar_solicitacao_compra():
    secrets = load_secrets()
    
    url = secrets.get('url')
    
    headers = {
        'accept': 'application/json;odata.metadata=minimal;odata.streaming=true',
        'Content-Type': 'application/json'
    }
    
    # Payload limpo sem arrays de rateio vazios para evitar erro de Identificador
    payload = {
        "CompanyId": 1,
        "BranchId": 1,
        "MovementTypeCode": "1.1.04",
        "Type": "A",
        "Series": "SC",
        "WarehouseCode": "01.01",
        "CostCenterCode": "2.09.002",
        "UserCode": "fernando.schmitz",
        "Observation": "Teste de inclusão via framework Flask",
        "MovementItems": [
            {
                "CompanyId": 1,         # Chave composta: Coligada
                "SequentialId": 1,      # Chave composta: Identificador sequencial interno (NSeqItMMov)
                "SequentialNumber": 1,  # Número de exibição na interface (NumSeq)
                "ProductId": 68650, 
                "Quantity": 1,
                "MeasureUnitCode": "UN",
                "CostCenterCode": "2.09.002"
            }
        ]
    }

    try:
        response = requests.post(
            url, 
            json=payload, 
            headers=headers,
            auth=(secrets.get('username'), secrets.get('password'))
        )
        response.raise_for_status() 
        return jsonify({
            "status": "success",
            "message": "Solicitação de compra criada com sucesso.",
            "data": response.json()
        }), 201
        
    except requests.exceptions.RequestException as e:
        error_data = e.response.json() if e.response is not None else str(e)
        return jsonify({
            "status": "error",
            "message": "Falha ao criar a solicitação no TOTVS RM.",
            "details": error_data
        }), e.response.status_code if e.response is not None else 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)