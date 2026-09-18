from flask import Blueprint, render_template, session, request, redirect, url_for, jsonify
from app.utils.auth import login_required
from app.extensions import db
from app.models.request import PurchaseRequest, RequestDraft, RequestDraftItem
from app.models.product import Product
from app.models.costcenter import CostCenter

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
            
        req_dict['status_texto'] = f"{req.status_compras}" if req.status_compras else req.status
        
        recent_requests.append(req_dict)

    return render_template(
        'dashboard_temp.html', 
        username=session.get('username'),
        recent_requests=recent_requests
    )

@store_bp.route('/nova-solicitacao', methods=['GET', 'POST'])
@login_required
def nova_solicitacao():
    if request.method == 'POST':
        cc = request.form.get('cost_center')
        obs = request.form.get('observation')
        
        draft = RequestDraft.query.filter_by(user_username=session['username']).first()
        if not draft:
            draft = RequestDraft(user_username=session['username'])
            db.session.add(draft)
            
        draft.cost_center = cc
        draft.observation = obs
        
        # Limpa o carrinho caso o usuário esteja iniciando um pedido do zero
        for item in draft.itens:
            db.session.delete(item)
            
        db.session.commit()
        return redirect(url_for('store.loja'))
        
    cost_centers = CostCenter.query.order_by(CostCenter.descricao).all()
    return render_template('nova_solicitacao.html', cost_centers=cost_centers)

@store_bp.route('/loja')
@login_required
def loja():
    tipo_filtro = request.args.get('tipo')
    
    # Busca os tipos únicos para popular o menu lateral de filtros
    tipos_brutos = db.session.query(Product.material_type).distinct().all()
    tipos_disponiveis = [t[0] for t in tipos_brutos if t[0]]
    
    query = Product.query
    if tipo_filtro:
        query = query.filter_by(material_type=tipo_filtro)
        
    # Usando paginação para não travar o navegador com os 3400 produtos de uma vez
    page = request.args.get('page', 1, type=int)
    produtos_paginados = query.paginate(page=page, per_page=24)
    
    return render_template(
        'loja.html', 
        produtos=produtos_paginados, 
        tipos=tipos_disponiveis,
        tipo_atual=tipo_filtro
    )

@store_bp.route('/carrinho')
@login_required
def carrinho():
    # Busca o rascunho atual do usuário
    draft = RequestDraft.query.filter_by(user_username=session['username']).first()
    itens_carrinho = []
    
    if draft:
        # Relaciona os itens do rascunho com os dados reais do produto
        for item in draft.itens:
            produto = Product.query.filter_by(product_id=item.product_id).first()
            if produto:
                itens_carrinho.append({
                    "item_id": item.id,
                    "codigo": produto.code,
                    "descricao": produto.description,
                    "quantidade": item.quantity
                })
                
    return render_template('carrinho.html', draft=draft, itens=itens_carrinho)

@store_bp.route('/api/carrinho/update', methods=['POST'])
@login_required
def update_cart_item():
    data = request.json
    item_id = data.get('item_id')
    nova_qtd = float(data.get('quantidade', 1))
    
    item = RequestDraftItem.query.get(item_id)
    # Valida se o item existe e pertence ao usuário logado
    if item and item.draft.user_username == session['username']:
        if nova_qtd > 0:
            item.quantity = nova_qtd
            db.session.commit()
            return jsonify({"success": True})
            
    return jsonify({"success": False, "error": "Operação inválida"}), 400

@store_bp.route('/api/carrinho/remove', methods=['POST'])
@login_required
def remove_cart_item():
    data = request.json
    item_id = data.get('item_id')
    
    item = RequestDraftItem.query.get(item_id)
    if item and item.draft.user_username == session['username']:
        db.session.delete(item)
        db.session.commit()
        return jsonify({"success": True})
        
    return jsonify({"success": False, "error": "Operação inválida"}), 400

@store_bp.route('/api/carrinho/add', methods=['POST'])
@login_required
def add_to_cart():
    data = request.json
    produto_id = data.get('product_id')
    qtd = float(data.get('quantidade', 1))
    
    draft = RequestDraft.query.filter_by(user_username=session['username']).first()
    if not draft:
        return jsonify({"error": "Inicie uma solicitação primeiro"}), 400
        
    from app.models.request import RequestDraftItem
    
    # Verifica se o item já está no carrinho. Se sim, soma a quantidade.
    item = RequestDraftItem.query.filter_by(draft_id=draft.id, product_id=produto_id).first()
    if item:
        item.quantity += qtd
    else:
        item = RequestDraftItem(draft_id=draft.id, product_id=produto_id, quantity=qtd)
        db.session.add(item)
        
    db.session.commit()
    
    # Retorna o total de itens únicos no carrinho para atualizar a bolinha na tela
    total_items = RequestDraftItem.query.filter_by(draft_id=draft.id).count()
    return jsonify({"success": True, "total_items": total_items})

@store_bp.route('/api/carrinho/count', methods=['GET'])
@login_required
def get_cart_count():
    draft = RequestDraft.query.filter_by(user_username=session['username']).first()
    total_items = len(draft.itens) if draft else 0
    return jsonify({"total_items": total_items})


