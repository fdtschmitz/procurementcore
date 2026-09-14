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