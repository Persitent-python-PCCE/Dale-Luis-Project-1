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