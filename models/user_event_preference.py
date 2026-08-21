from config.database import db
from datetime import datetime


class UserEventPreference(db.Model):

    __tablename__ = "user_event_preferences"

    id = db.Column(db.Integer,primary_key=True)

    user_id = db.Column(db.Integer,db.ForeignKey("users.id"),nullable=False)

    category_id = db.Column(db.Integer,db.ForeignKey("event_categories.id"),nullable=False)

    created_at = db.Column(db.DateTime,default=datetime.utcnow)
    

    user = db.relationship("User",back_populates="preferences")

    category = db.relationship("EventCategory",back_populates="preferences")

    __table_args__ = (
        db.UniqueConstraint("user_id","category_id",
            name="uq_user_category_preference"),
        )