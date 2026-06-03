from uuid import UUID

from sqlalchemy.orm import Session

from app.models.document import Document


class DocumentRepository:
    def __init__(self, db: Session):
        self.db = db

    def add(self, document: Document) -> Document:
        self.db.add(document)
        return document

    def get_for_user(self, document_id: UUID, user_id: UUID) -> Document | None:
        return (
            self.db.query(Document)
            .filter(Document.id == document_id, Document.user_id == user_id)
            .first()
        )

    def list_for_user(self, user_id: UUID, limit: int = 50) -> list[Document]:
        return (
            self.db.query(Document)
            .filter(Document.user_id == user_id)
            .order_by(Document.created_at.desc())
            .limit(limit)
            .all()
        )
