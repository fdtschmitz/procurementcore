from app.extensions import db

class Product(db.Model):
    __tablename__ = 'products'

    company_id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, primary_key=True)
    
    code = db.Column(db.String(50), nullable=False, index=True)
    short_code = db.Column(db.String(50))
    description = db.Column(db.String(255), nullable=False)
    material_type = db.Column(db.String(100))
    operational_nature = db.Column(db.String(100))

    def to_dict(self):
        return {
            "productCompanyId": self.company_id,
            "productId": self.product_id,
            "code": self.code,
            "shortCode": self.short_code,
            "description": self.description,
            "materialType": self.material_type,
            "operationalNature": self.operational_nature
        }