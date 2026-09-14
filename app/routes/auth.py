from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from app.services.totvs_auth import login_rm

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        resultado = login_rm(username, password)
        
        if resultado.get("success"):
            session['username'] = username
            session['access_token'] = resultado['access_token']
            session['refresh_token'] = resultado['refresh_token']
            session['access_expires_at'] = resultado['access_expires_at']
            session['refresh_expires_at'] = resultado['refresh_expires_at']
            
            # Recupera a rota pretendida ou redireciona para a loja
            next_page = request.args.get('next')
            return redirect(next_page or url_for('store.index'))
        else:
            flash(resultado.get("message"), "error")
            
    return render_template('login.html')

@auth_bp.route('/logout')
def logout():
    session.clear()
    flash("Logout realizado com sucesso.", "success")
    return redirect(url_for('auth.login'))