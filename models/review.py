from config.database import db
from datetime import datetime


class Review(db.Model):

    __tablename__ = "reviews"

    id = db.Column(db.Integer,primary_key=True)

    user_id = db.Column(db.Integer,db.ForeignKey("users.id"),nullable=False)

    event_id = db.Column(db.Integer,db.ForeignKey("events.id"),nullable=False)

    booking_id = db.Column(db.Integer,db.ForeignKey("bookings.id"),nullable=False)

    rating = db.Column(db.Integer,nullable=False)

    review_text = db.Column(db.Text)

    created_at = db.Column(db.DateTime,default=datetime.utcnow)

    updated_at = db.Column(db.DateTime,default=datetime.utcnow,onupdate=datetime.utcnow)
    

    user = db.relationship("User",back_populates="reviews")

    event = db.relationship("Event",back_populates="reviews")

    booking = db.relationship("Booking",back_populates="reviews")

    __table_args__ = (
        db.CheckConstraint("rating >= 1 AND rating <= 5",
                           name="check_rating"),
        db.UniqueConstraint("user_id","event_id",
                            name="uq_user_event_review"),
        )