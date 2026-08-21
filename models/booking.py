from config.database import db
from datetime import datetime


class Booking(db.Model):

    __tablename__ = "bookings"

    id = db.Column(db.Integer,primary_key=True)

    booking_reference = db.Column(db.String(30),unique=True,nullable=False)

    user_id = db.Column(db.Integer,db.ForeignKey("users.id"),nullable=False)

    event_id = db.Column(db.Integer,db.ForeignKey("events.id"),nullable=False)

    total_amount = db.Column(db.Numeric(10, 2),nullable=False)

    discount_amount = db.Column(db.Numeric(10, 2),default=0)

    final_amount = db.Column(db.Numeric(10, 2),nullable=False)

    coupon_id = db.Column(db.Integer,db.ForeignKey("coupons.id"),nullable=True)

    status = db.Column(db.Enum(
            "PENDING",
            "CONFIRMED",
            "CANCELLED"
        ),
        default="PENDING",
        nullable=False)

    booking_date = db.Column(db.DateTime,default=datetime.utcnow)

    cancelled_at = db.Column(db.DateTime,nullable=True)

    cancellation_reason = db.Column(db.Text,nullable=True)



    user = db.relationship("User",back_populates="bookings")

    event = db.relationship("Event",back_populates="bookings")

    booking_items = db.relationship("BookingItem",
                                    back_populates="booking",
                                    cascade="all, delete-orphan",
                                    lazy=True)

    payment = db.relationship("Payment",
                              back_populates="booking",
                              uselist=False)

    coupon = db.relationship("Coupon",back_populates="bookings")

    reviews = db.relationship("Review",
                              back_populates="booking",
                              lazy=True)

    def __repr__(self):
        return f"<Booking {self.booking_reference}>"