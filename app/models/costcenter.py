from app.extensions import db

class CostCenter(db.Model):
    __tablename__ = 'cost_centers'
    
    # O código do centro de custo costuma ser a chave primária (ex: "2.09.002")
    codigo = db.Column(db.String(50), primary_key=True)
    descricao = db.Column(db.String(255), nullable=False)

    def to_dict(self):
        return {
            "codigo": self.codigo,
            "descricao": self.descricao
        }