from models.user_document import UserDocument

class UserDocumentService:
    def __init__(self, document_dao):
        self.document_dao = document_dao

    def get_document(self, document_id):
        document = self.document_dao.get_by_id(document_id)

        if document is None:
            raise ValueError("Document not found")

        return document

    def get_user_documents(self, user_id):
        return self.document_dao.get_by_user(user_id)

    def get_pending_documents(self):
        return self.document_dao.get_pending()

    def upload_document(self, user_id, document_type, file_path, file_name, file_type=None, file_size=None):

        if not document_type:
            raise ValueError("Document type is required")

        if not file_path or not file_name:
            raise ValueError("File path and file name are required")

        document = UserDocument(
            user_id=user_id,
            document_type=document_type,
            file_path=file_path,
            file_name=file_name,
            file_type=file_type,
            file_size=file_size,
            verification_status="PENDING"
        )

        return self.document_dao.save(document)

    def verify_document(self,document_id,admin_id):
        document = self.get_document(document_id)

        if document.verification_status != "PENDING":
            raise ValueError("Document is not pending")

        return self.document_dao.verify(document,admin_id)

    def reject_document(self,document_id,admin_id,reason):
        document = self.get_document(document_id)

        if document.verification_status != "PENDING":
            raise ValueError("Document is not pending")

        return self.document_dao.reject(document,admin_id,reason)

    def delete_document(self,document_id,user_id):
        document = self.get_document(document_id)

        if document.user_id != user_id:
            raise ValueError("You cannot delete this document")

        self.document_dao.delete(document)
