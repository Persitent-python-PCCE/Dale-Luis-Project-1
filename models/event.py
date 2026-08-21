from config.database import db
from datetime import datetime


class Event(db.Model):

    __tablename__ = "events"

    id = db.Column(db.Integer,primary_key=True)
    
    name = db.Column(db.String(200),nullable=False)
    
    category_id = db.Column(db.Integer,db.ForeignKey("event_categories.id"),nullable=False)
    
    venue_id = db.Column(db.Integer,db.ForeignKey("venues.id"),nullable=False)
    
    description = db.Column(db.Text,nullable=False)
    
    poster_path = db.Column(db.String(500),nullable=True)
    
    start_date = db.Column(db.Date,nullable=False)
    
    end_date = db.Column(db.Date,nullable=False)
    
    start_time = db.Column(db.Time,nullable=False)
    
    end_time = db.Column(db.Time,nullable=False)
    
    maximum_capacity = db.Column(db.Integer,nullable=False)

    vip_price = db.Column(db.Numeric(10, 2),nullable=False)

    premium_price = db.Column(db.Numeric(10, 2),nullable=False)

    regular_price = db.Column(db.Numeric(10, 2),nullable=False)

    status = db.Column(
        db.Enum(
            "UPCOMING",
            "ONGOING",
            "COMPLETED",
            "CANCELLED"
        ),default="UPCOMING",
        nullable=False)

    approval_status = db.Column(
        db.Enum(
            "PENDING",
            "APPROVED",
            "REJECTED"
        ),default="PENDING",
        nullable=False)

    created_by = db.Column(db.Integer,db.ForeignKey("users.id"),nullable=False)

    approved_by = db.Column(db.Integer,db.ForeignKey("users.id"),nullable=True)

    approved_at = db.Column(db.DateTime,nullable=True)

    rejection_reason = db.Column(db.Text,nullable=True)

    created_at = db.Column(db.DateTime,default=datetime.utcnow)

    updated_at = db.Column(db.DateTime,default=datetime.utcnow,onupdate=datetime.utcnow)


    category = db.relationship("EventCategory",back_populates="events")

    venue = db.relationship("Venue",back_populates="events")

    creator = db.relationship("User",
                              foreign_keys=[created_by],
                              back_populates="created_events"
                              )

    approver = db.relationship("User",
                               foreign_keys=[approved_by],
                               back_populates="approved_events"
                               )

    bookings = db.relationship("Booking",back_populates="event",lazy=True)
    
    booking_items = db.relationship("BookingItem",back_populates="event",lazy=True)

    reviews = db.relationship("Review",back_populates="event",lazy=True)

    def __repr__(self):
        return f"<Event {self.name}>"
