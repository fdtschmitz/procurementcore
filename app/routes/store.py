from flask import Blueprint, render_template, session
from app.utils.auth import login_required
from app.models.request import PurchaseRequest

store_bp = Blueprint('store', __name__)

@store_bp.route('/')
@login_required
def index():
    # Busca as últimas 5 solicitações ordenadas pela data de emissão ou ID
    ultimas_solicitacoes = PurchaseRequest.query.order_by(
        PurchaseRequest.id.desc()
    ).limit(5).all()
    
    # Transforma os objetos do SQLAlchemy em dicionários para renderizar no template
    recent_requests = []
    for req in ultimas_solicitacoes:
        req_dict = req.to_dict()
        
        # Mapeando classes de cor para o status no template
        status_norm = (req.status or '').lower()
        if 'pendente' in status_norm or 'em fila' in (req.status_compras or '').lower():
            req_dict['status_classe'] = 'pendente'
        elif 'aprovado' in status_norm or 'cotado' in (req.status_compras or '').lower():
            req_dict['status_classe'] = 'aprovado'
        else:
            req_dict['status_classe'] = 'default'
            
        req_dict['status_texto'] = f"{req.status} ({req.status_compras})" if req.status_compras else req.status
        
        recent_requests.append(req_dict)

    return render_template(
        'dashboard_temp.html', 
        username=session.get('username'),
        recent_requests=recent_requests
    )