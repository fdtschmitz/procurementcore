from app.extensions import db
from datetime import datetime

class RequestDraft(db.Model):
    """Armazena o andamento local das solicitações do usuário antes de enviar ao RM"""
    __tablename__ = 'request_drafts'

    id = db.Column(db.Integer, primary_key=True)
    user_username = db.Column(db.String(100), nullable=False, index=True)
    product_id = db.Column(db.Integer, nullable=False)
    quantity = db.Column(db.Integer, default=1)
    cost_center = db.Column(db.String(50))
    observation = db.Column(db.Text)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "productId": self.product_id,
            "quantity": self.quantity,
            "costCenter": self.cost_center,
            "observation": self.observation,
            "updatedAt": self.updated_at.isoformat()
        }


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
    
    coligada = db.Column(db.Integer)             # CODCOLIGADA
    nseqitmmov = db.Column(db.Integer)           # NSQITMMOV
    nseq = db.Column(db.Integer)                 # NSEQ
    codigo_item = db.Column(db.String(50), nullable=False) # COD_PRODUTO
    descricao_item = db.Column(db.String(255), nullable=False) # PRODUTO
    quantidade = db.Column(db.Float, nullable=False) # QTD_ORIGINAL
    nat_op = db.Column(db.String(50))            # NAT_OP
    centro_custo = db.Column(db.String(50))      # CODCCUSTO

    def to_dict(self):
        return {
            "id": self.id,
            "nseq": self.nseq,
            "codigo": self.codigo_item,
            "nome": self.descricao_item,
            "quantidade": self.quantidade,
            "nat_op": self.nat_op,
            "centro_custo": self.centro_custo
        }