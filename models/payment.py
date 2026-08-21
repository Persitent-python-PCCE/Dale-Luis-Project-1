from config.database import db
from datetime import datetime

class Payment(db.Model):

    __tablename__ = "payments"

    id = db.Column(db.Integer,primary_key=True)

    booking_id = db.Column(db.Integer,db.ForeignKey("bookings.id"),nullable=False,unique=True)

    transaction_id = db.Column(db.String(100),unique=True,nullable=False)

    payment_method = db.Column(
        db.Enum(
            "MOCK",
            "UPI",
            "CARD",
            "NET_BANKING"
        ),
        default="MOCK")

    amount = db.Column(db.Numeric(10, 2),nullable=False)

    status = db.Column(
        db.Enum(
            "PENDING",
            "SUCCESS",
            "FAILED"
        ),
        default="PENDING",
        nullable=False)

    gateway_response = db.Column(db.JSON,nullable=True)

    paid_at = db.Column(db.DateTime,nullable=True)

    refund_status = db.Column(
        db.Enum(
            "NOT_REQUESTED",
            "REQUESTED",
            "PROCESSING",
            "COMPLETED",
            "FAILED"
        ),
        default="NOT_REQUESTED")

    refund_amount = db.Column(db.Numeric(10, 2),nullable=True)

    refunded_at = db.Column(db.DateTime,nullable=True)

    created_at = db.Column(db.DateTime,default=datetime.utcnow)


    booking = db.relationship(
        "Booking",
        back_populates="payment"
    )

    def __repr__(self):
        return f"<Payment {self.transaction_id}>"