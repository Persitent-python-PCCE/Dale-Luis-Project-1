from config.database import db
from datetime import datetime


class UserDocument(db.Model):

    __tablename__ = "user_documents"

    id = db.Column(db.Integer,primary_key=True)

    user_id = db.Column(db.Integer,db.ForeignKey("users.id"),nullable=False)

    document_type = db.Column(db.String(50),nullable=False)

    file_path = db.Column(db.String(500),nullable=False)

    file_name = db.Column(db.String(255),nullable=False)

    file_type = db.Column(db.String(50))

    file_size = db.Column(db.Integer)

    verification_status = db.Column(
        db.Enum(
            "PENDING",
            "VERIFIED",
            "REJECTED"
        ),
        default="PENDING")

    verified_by = db.Column(db.Integer,db.ForeignKey("users.id"),nullable=True)

    verified_at = db.Column(db.DateTime,nullable=True)

    rejection_reason = db.Column(db.Text,nullable=True)

    uploaded_at = db.Column(db.DateTime,default=datetime.utcnow)
    

    user = db.relationship("User",
        foreign_keys=[user_id],
        back_populates="documents")

    verifier = db.relationship("User",
        foreign_keys=[verified_by],
        back_populates="verified_documents")

    def __repr__(self):
        return f"<UserDocument {self.file_name}>"

    def to_dict(self):
        return {
            "id": self.id, 
            "user_id": self.user_id,
            "document_type": self.document_type, 
            "file_name": self.file_name,
            "file_type": self.file_type, 
            "file_size": self.file_size,
            "verification_status": self.verification_status,
            "verified_by": self.verified_by,
            "verified_at": self.verified_at.isoformat() if self.verified_at else None,
            "rejection_reason": self.rejection_reason,
            "uploaded_at": self.uploaded_at.isoformat() if self.uploaded_at else None,
        }
