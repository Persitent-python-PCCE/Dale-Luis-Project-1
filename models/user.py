from config.database import db
from datetime import datetime

class User(db.Model):
    
    __tablename__ = "users"
    
    id = db.Column(db.Integer, primary_key=True)
    
    name = db.Column(db.String(100), nullable=False)
    
    email = db.Column(db.String(200), unique=True, nullable=False)
    
    pass_hash = db.Column(db.String(255), nullable=False)
    
    phone = db.Column(db.String(20))
    
    role = db.Column(db.Enum("CUSTOMER",
                             "ADMIN",
                             "EVENT_MANAGER"),
                            nullable=False
                    ) 
    
    is_active = db.Column(db.Boolean,default=True,nullable=False)
    
    remember_token_hash = db.Column(db.String(255), nullable=True)
    
    remember_token_expiry = db.Column(db.DateTime, nullable=True)
    
    last_login_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    updated_at = db.Column(db.DateTime, default=datetime.utcnow)
    

    bookings = db.relationship("Booking", back_populates="user", lazy = True)
    
    reviews = db.relationship("Review", back_populates="user", lazy = True)
    
    preferences = db.relationship("UserEventPreference", 
                                    back_populates="user", 
                                    lazy = True, 
                                    cascade="all,delete-orphan")
    
    documents = db.relationship("UserDocument", 
                                    foreign_keys="UserDocument.user_id", 
                                    back_populates="user", lazy = True, 
                                    cascade ="all, delete-orphan")
    
    created_events = db.relationship("Event", 
                                    foreign_keys="Event.created_by", 
                                    back_populates="creator", lazy = True)
    
    approved_events = db.relationship("Event", 
                                    foreign_keys="Event.approved_by", 
                                    back_populates="approver", lazy = True)
    
    created_venues = db.relationship("Venue", 
                                    foreign_keys="Venue.created_by", 
                                    back_populates="creator", lazy = True)
    
    created_coupons = db.relationship("Coupon", 
                                    foreign_keys="Coupon.created_by", 
                                    back_populates="creator", lazy=True)
    
    verified_documents = db.relationship("UserDocument",
                                    foreign_keys="UserDocument.verified_by",
                                    back_populates="verifier",lazy=True)
    
    def __repr__(self):
        return f"<User {self.email}>"

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "phone": self.phone,
            "role": self.role,
            "is_active": self.is_active,
            "last_login_at": self.last_login_at.isoformat() if self.last_login_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
