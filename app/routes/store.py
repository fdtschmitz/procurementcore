from flask import Blueprint, render_template, session
from app.utils.auth import login_required

store_bp = Blueprint('store', __name__)

@store_bp.route('/')
@login_required
def index():
    # Passamos o username salvo na sessão para personalizar a tela
    return render_template('dashboard_temp.html', username=session.get('username'))