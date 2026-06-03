import re
import uuid
from datetime import datetime
from uuid import UUID

from fastapi import UploadFile
from sqlalchemy.orm import Session

from app.models.audit import AuditResult
from app.models.document import Document, DocumentStatus
from app.models.usage import UsageType
from app.repositories.audit_repository import AuditRepository
from app.repositories.document_repository import DocumentRepository
from app.schemas.document import DocumentStatusResponse, DocumentUploadResponse
from app.services.audit_rule_engine import AuditRuleEngine
from app.services.subscription_service import QuotaExceededError, SubscriptionService


class DocumentProcessingError(Exception):
    pass


class UnsupportedDocumentTypeError(DocumentProcessingError):
    pass


class DocumentService:
    MAX_UPLOAD_BYTES = 5 * 1024 * 1024
    SUPPORTED_CONTENT_TYPES = {
        "text/plain": "txt",
        "text/csv": "csv",
        "application/json": "json",
    }

    def __init__(self, db: Session):
        self.db = db
        self.documents = DocumentRepository(db)
        self.audits = AuditRepository(db)
        self.subscriptions = SubscriptionService(db)
        self.audit_engine = AuditRuleEngine()

    async def upload_and_analyze(self, user_id: UUID, upload: UploadFile) -> DocumentUploadResponse:
        file_type = self._resolve_file_type(upload)
        self.subscriptions.ensure_quota_available(user_id, UsageType.UPLOAD)
        content = await upload.read()
        try:
            if len(content) > self.MAX_UPLOAD_BYTES:
                raise DocumentProcessingError("Upload exceeds 5 MB limit")
            text = self._extract_text(content, file_type)
            risk_level, flags = self.audit_engine.evaluate(text)
            self.subscriptions.enforce_and_increment(user_id, UsageType.UPLOAD)

            document = Document(
                user_id=user_id,
                filename=self._safe_stored_filename(file_type),
                file_type=file_type,
                status=DocumentStatus.COMPLETED,
                processed_at=datetime.utcnow(),
            )
            self.documents.add(document)
            self.db.flush()

            audit_result = AuditResult(
                user_id=user_id,
                document_id=document.id,
                risk_level=risk_level,
                flags=flags,
            )
            self.audits.add(audit_result)
            self.db.commit()
            self.db.refresh(document)
            self.db.refresh(audit_result)
            return DocumentUploadResponse(document=document, audit=audit_result)
        finally:
            content = b""
            text = ""

    def list_documents(self, user_id: UUID) -> list[Document]:
        return self.documents.list_for_user(user_id)

    def get_status(self, user_id: UUID, document_id: UUID) -> DocumentStatusResponse:
        document = self.documents.get_for_user(document_id, user_id)
        if not document:
            raise DocumentProcessingError("Document not found")
        audit = self.audits.get_for_document(document_id, user_id)
        return DocumentStatusResponse(document=document, audit=audit)

    def _resolve_file_type(self, upload: UploadFile) -> str:
        content_type = (upload.content_type or "").lower()
        if content_type in self.SUPPORTED_CONTENT_TYPES:
            return self.SUPPORTED_CONTENT_TYPES[content_type]
        filename = (upload.filename or "").lower()
        if filename.endswith(".txt"):
            return "txt"
        if filename.endswith(".csv"):
            return "csv"
        if filename.endswith(".json"):
            return "json"
        if filename.endswith(".pdf"):
            raise UnsupportedDocumentTypeError("PDF extraction dependency is not installed yet")
        if filename.endswith(".docx"):
            raise UnsupportedDocumentTypeError("DOCX extraction dependency is not installed yet")
        raise UnsupportedDocumentTypeError("Unsupported document type")

    @staticmethod
    def _extract_text(content: bytes, file_type: str) -> str:
        if file_type not in {"txt", "csv", "json"}:
            raise UnsupportedDocumentTypeError("Unsupported document type")
        text = content.decode("utf-8", errors="ignore")
        if not text.strip():
            raise DocumentProcessingError("Uploaded document contains no readable text")
        return re.sub(r"\s+", " ", text).strip()

    @staticmethod
    def _safe_stored_filename(file_type: str) -> str:
        return f"tax-document-{uuid.uuid4()}.{file_type}"
