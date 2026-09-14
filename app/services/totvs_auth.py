import requests
import time
from flask import current_app

def login_rm(username, password):
    url = f"{current_app.config['TOTVS_BASE_URL']}/api/connect/token"
    payload = {
        "UserName": username,
        "Password": password
    }
    headers = {"Content-Type": "application/json"}
    
    response = requests.post(url, json=payload, headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        now = int(time.time())
        return {
            "success": True,
            "access_token": data.get("access_token"),
            "refresh_token": data.get("refresh_token"),
            "access_expires_at": now + data.get("expires_in", 300),
            "refresh_expires_at": now + (16 * 3600)  # 16 horas de duração
        }
    
    # Tratamento específico para o erro 400 retornado pelo ERP
    if response.status_code == 400:
        erro_json = response.json()
        return {"success": False, "message": erro_json.get("message", "Usuário ou Senha inválidos.")}
        
    return {"success": False, "message": f"Erro de comunicação: {response.status_code}"}

def refresh_rm_token(refresh_token):
    url = f"{current_app.config['TOTVS_BASE_URL']}/api/connect/token"
    payload = {
        "refresh_token": refresh_token,
        "grant_type": "refresh_token"
    }
    headers = {"Content-Type": "application/json"}
    
    response = requests.post(url, json=payload, headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        now = int(time.time())
        return {
            "success": True,
            "access_token": data.get("access_token"),
            "refresh_token": data.get("refresh_token"),
            "access_expires_at": now + data.get("expires_in", 300)
        }
        
    return {"success": False}