from uuid import UUID

from sqlalchemy.orm import Session

from app.models.audit import AuditResult


class AuditRepository:
    def __init__(self, db: Session):
        self.db = db

    def add(self, audit_result: AuditResult) -> AuditResult:
        self.db.add(audit_result)
        return audit_result

    def get_for_document(self, document_id: UUID, user_id: UUID) -> AuditResult | None:
        return (
            self.db.query(AuditResult)
            .filter(AuditResult.document_id == document_id, AuditResult.user_id == user_id)
            .order_by(AuditResult.created_at.desc())
            .first()
        )
