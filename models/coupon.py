from config.database import db
from datetime import datetime


class Coupon(db.Model):

    __tablename__ = "coupons"

    id = db.Column(db.Integer,primary_key=True)

    code = db.Column(db.String(50),unique=True,nullable=False)

    description = db.Column(db.String(255))

    discount_type = db.Column(
        db.Enum(
            "PERCENTAGE",
            "FIXED"
        ),
        nullable=False)

    discount_value = db.Column(db.Numeric(10, 2),nullable=False)

    minimum_amount = db.Column(db.Numeric(10, 2),default=0)

    maximum_discount = db.Column(db.Numeric(10, 2),nullable=True)

    usage_limit = db.Column(db.Integer,nullable=False)

    used_count = db.Column(db.Integer,default=0,nullable=False)

    valid_from = db.Column(db.DateTime,nullable=False)

    valid_until = db.Column(db.DateTime,nullable=False)

    is_active = db.Column(db.Boolean,default=True)

    created_by = db.Column(db.Integer,db.ForeignKey("users.id"),nullable=False)

    created_at = db.Column(db.DateTime,default=datetime.utcnow)
    

    creator = db.relationship("User",
        foreign_keys=[created_by],
        back_populates="created_coupons")

    bookings = db.relationship("Booking",back_populates="coupon",lazy=True)

    def __repr__(self):
        
        return f"<Coupon {self.code}>"

    def to_dict(self):
        return {
            "id": self.id, "code": self.code, 
            "description": self.description,
            "discount_type": self.discount_type,
            "discount_value": float(self.discount_value),
            "minimum_amount": float(self.minimum_amount or 0),
            "maximum_discount": float(self.maximum_discount) if self.maximum_discount is not None else None,
            "usage_limit": self.usage_limit, 
            "used_count": self.used_count,
            "valid_from": self.valid_from.isoformat() if self.valid_from else None,
            "valid_until": self.valid_until.isoformat() if self.valid_until else None,
            "is_active": self.is_active, 
            "created_by": self.created_by,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
