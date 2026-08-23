from config.database import db
from datetime import datetime

class Venue(db.Model):
    __tablename__ = "venues"
    
    id = db.Column(db.Integer, primary_key=True)
    
    name = db.Column(db.String(150), nullable=False)
    
    address = db.Column(db.Text, nullable=False)
    
    city = db.Column(db.String(100), nullable=False)
    
    state = db.Column(db.String(100))
    
    pincode = db.Column(db.String(10))
    
    capacity = db.Column(db.Integer, nullable=False)
    
    description = db.Column(db.Text)
    
    is_active = db.Column(db.Boolean,default=True)
    
    created_by = db.Column(db.Integer,db.ForeignKey("users.id"),nullable=False)
    
    created_at = db.Column(db.DateTime,default=datetime.utcnow)
    
    updated_at = db.Column(db.DateTime,default=datetime.utcnow,onupdate=datetime.utcnow)
    
    creator = db.relationship("User",
        foreign_keys=[created_by],
        back_populates="created_venues")

    seats = db.relationship("Seat",
        back_populates="venue",
        lazy=True,
        cascade="all, delete-orphan")

    events = db.relationship("Event",back_populates="venue",lazy=True)

    def __repr__(self):
        return f"<Venue {self.name}>"

    def to_dict(self):
        return {
            "id": self.id, 
            "name": self.name, 
            "address": self.address,
            "city": self.city, 
            "state": self.state, 
            "pincode": self.pincode,
            "capacity": self.capacity, 
            "description": self.description,
            "is_active": self.is_active, 
            "created_by": self.created_by,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
