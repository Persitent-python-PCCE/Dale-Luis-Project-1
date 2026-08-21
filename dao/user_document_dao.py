from models.user_document import UserDocument
from config.database import db
from datetime import datetime


class UserDocumentDAO:

    def get_all(self):
        return UserDocument.query.all()

    def get_by_id(self, document_id):
        return UserDocument.query.get(document_id)

    def get_by_user(self, user_id):
        return UserDocument.query.filter_by(
            user_id=user_id
        ).all()

    def get_pending(self):
        return UserDocument.query.filter_by(
            verification_status="PENDING"
        ).all()

    def save(self, document):
        db.session.add(document)
        db.session.commit()
        return document

    def update(self, document):
        db.session.commit()
        return document

    def verify(self, document, admin_id):

        document.verification_status = "VERIFIED"
        document.verified_by = admin_id
        document.verified_at = datetime.utcnow()

        db.session.commit()

        return document

    def reject(self, document, admin_id, reason):

        document.verification_status = "REJECTED"
        document.verified_by = admin_id
        document.verified_at = datetime.utcnow()
        document.rejection_reason = reason

        db.session.commit()

        return document

    def delete(self, document):
        db.session.delete(document)
        db.session.commit()
