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