import time
from functools import wraps
from flask import session, redirect, url_for, flash, request
from app.services.totvs_auth import refresh_rm_token

def ensure_valid_token():
    """Garante que o token da sessão está válido, renovando se necessário."""
    if 'access_token' not in session:
        return False
        
    now = int(time.time())
    
    # Adicionamos uma margem de segurança de 10 segundos
    if now > (session.get('access_expires_at', 0) - 10):
        
        # Verifica se o refresh token (16h) também expirou
        if now > session.get('refresh_expires_at', 0):
            return False
            
        # Tenta renovar o token
        new_tokens = refresh_rm_token(session.get('refresh_token'))
        if new_tokens.get("success"):
            session['access_token'] = new_tokens['access_token']
            session['refresh_token'] = new_tokens['refresh_token']
            session['access_expires_at'] = new_tokens['access_expires_at']
            return True
        else:
            return False
            
    return True

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not ensure_valid_token():
            # Salva o estado do formulário caso o usuário caia por inatividade > 16h enquanto preenchia
            if request.method == 'POST':
                session['draft_form_data'] = request.form.to_dict()
                
            flash("Sua sessão expirou por inatividade. Por favor, faça login novamente para continuar.", "warning")
            session.clear()
            return redirect(url_for('auth.login', next=request.url))
            
        return f(*args, **kwargs)
    return decorated_function