from app.extensions import db
from datetime import datetime

class RequestDraft(db.Model):
    """Armazena o cabeçalho do carrinho de compras do usuário"""
    __tablename__ = 'request_drafts'

    id = db.Column(db.Integer, primary_key=True)
    user_username = db.Column(db.String(100), nullable=False, index=True)
    cost_center = db.Column(db.String(50))
    observation = db.Column(db.Text)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relação 1:N com os itens do carrinho
    itens = db.relationship('RequestDraftItem', backref='draft', lazy=True, cascade="all, delete-orphan")


class RequestDraftItem(db.Model):
    """Armazena os produtos adicionados ao carrinho"""
    __tablename__ = 'request_draft_items'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    draft_id = db.Column(db.Integer, db.ForeignKey('request_drafts.id'), nullable=False)
    
    # Salvamos o ID do produto e a quantidade desejada
    product_id = db.Column(db.Integer, nullable=False)
    quantity = db.Column(db.Float, default=1)


class PurchaseRequest(db.Model):
    __tablename__ = 'purchase_requests'

    id = db.Column(db.Integer, primary_key=True) # IDMOV
    coligada = db.Column(db.Integer)             # CODCOLIGADA
    numero = db.Column(db.String(50), nullable=False, index=True) # NUMEROMOV
    tipo_mov = db.Column(db.String(20))          # CODTMV
    solicitante = db.Column(db.String(100))      # USUARIOCRIACAO
    data_emissao = db.Column(db.Date)            # DATAEMISSAO
    centro_custo = db.Column(db.String(50))      # CODCCUSTO
    status = db.Column(db.String(50))            # STATUS
    status_compras = db.Column(db.String(50))    # STATUS_COMPRAS
    status_concluido = db.Column(db.String(10))  # STSCONCLUIDO
    data_modificacao = db.Column(db.DateTime)    # RECMODIFIEDON
    descricao = db.Column(db.Text)               # DESCRICAO

    itens = db.relationship('PurchaseRequestItem', backref='request', lazy=True, cascade="all, delete-orphan")

    def to_dict(self):
        return {
            "id": self.id,
            "coligada": self.coligada,
            "numero": self.numero,
            "solicitante": self.solicitante,
            "data_emissao": self.data_emissao.isoformat() if self.data_emissao else None,
            "centro_custo": self.centro_custo,
            "status": self.status,
            "status_compras": self.status_compras,
            "descricao": self.descricao,
            "itens": [item.to_dict() for item in self.itens]
        }


class PurchaseRequestItem(db.Model):
    __tablename__ = 'purchase_request_items'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    request_id = db.Column(db.Integer, db.ForeignKey('purchase_requests.id'), nullable=False, index=True)
    
    coligada = db.Column(db.Integer)             
    nseqitmmov = db.Column(db.Integer)           
    nseq = db.Column(db.Integer)                 
    codigo_item = db.Column(db.String(50), nullable=False) 
    descricao_item = db.Column(db.String(255), nullable=False) 
    quantidade = db.Column(db.Float, nullable=False)
    unidade = db.Column(db.String(10))           
    nat_op = db.Column(db.String(50))            
    centro_custo = db.Column(db.String(50))      

    def to_dict(self):
        return {
            "id": self.id,
            "nseq": self.nseq,
            "codigo": self.codigo_item,
            "nome": self.descricao_item,
            "quantidade": self.quantidade,
            "unidade": self.unidade,
            "nat_op": self.nat_op,
            "centro_custo": self.centro_custo
        }