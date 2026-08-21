from config.database import db

class EventCategory(db.Model):
    
    __tablename__ = "event_categories"
    
    id = db.Column(db.Integer, primary_key=True)
    
    name = db.Column(db.String(100), unique=True, nullable=False)
    
    description = db.Column(db.String(255))
    
    is_active = db.Column(db.Boolean, default=True)
    
    
    events = db.relationship("Event",back_populates="category",lazy=True)
    
    preferences = db.relationship("UserEventPreference",
                                  back_populates="category",
                                  lazy=True)

    def __repr__(self):
        return f"<EventCategory {self.name}>"