from config.database import db
from datetime import datetime


class BookingItem(db.Model):

    __tablename__ = "booking_items"

    id = db.Column(db.Integer,primary_key=True)

    booking_id = db.Column(db.Integer,db.ForeignKey("bookings.id"),nullable=False)

    event_id = db.Column(db.Integer,db.ForeignKey("events.id"),nullable=False)

    seat_id = db.Column(db.Integer,db.ForeignKey("seats.id"),nullable=False)

    seat_number = db.Column(db.String(20),nullable=False)

    seat_category = db.Column(db.String(30),nullable=False)

    unit_price = db.Column(db.Numeric(10, 2),nullable=False)

    ticket_status = db.Column(
        db.Enum(
            "VALID",
            "USED",
            "CANCELLED",
            "EXPIRED"
        ),
        default="VALID",
        nullable=False)

    qr_token = db.Column(db.String(255),unique=True,nullable=False)

    created_at = db.Column(db.DateTime,default=datetime.utcnow)


    booking = db.relationship("Booking",back_populates="booking_items")

    event = db.relationship("Event", back_populates="booking_items")
    
    seat = db.relationship("Seat",back_populates="booking_items")
    
    def __repr__(self):
        return f"<BookingItem {self.seat_number}>"

    def to_dict(self):
        return {
            "id": self.id, 
            "booking_id": self.booking_id, 
            "event_id": self.event_id,
            "seat_id": self.seat_id, 
            "seat_number": self.seat_number,
            "seat_category": self.seat_category, 
            "unit_price": float(self.unit_price),
            "ticket_status": self.ticket_status,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
