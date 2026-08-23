from config.database import db

class Seat(db.Model):

    __tablename__ = "seats"

    id = db.Column(db.Integer,primary_key=True)
    
    venue_id = db.Column(db.Integer,db.ForeignKey("venues.id"),nullable=False)
    
    seat_number = db.Column(db.String(20),nullable=False)
    
    row_name = db.Column(db.String(10),nullable=False)
    
    category = db.Column(
        db.Enum(
            "VIP",
            "PREMIUM",
            "REGULAR"),
        nullable=False)
    
    base_price = db.Column(db.Numeric(10, 2),nullable=False)
    
    is_active = db.Column(db.Boolean,default=True)
    
    
    venue = db.relationship("Venue",back_populates="seats")
    
    booking_items = db.relationship("BookingItem",back_populates="seat",lazy=True)
    
    __table_args__ = (db.UniqueConstraint(
            "venue_id",
            "seat_number",
            name="uq_venue_seat"
        ),)

    def __repr__(self):
        return f"<Seat {self.seat_number}>"

    def to_dict(self):
        return {
            "id": self.id, 
            "venue_id": self.venue_id,
            "seat_number": self.seat_number, 
            "row_name": self.row_name,
            "category": self.category, 
            "base_price": float(self.base_price),
            "is_active": self.is_active,
        }
