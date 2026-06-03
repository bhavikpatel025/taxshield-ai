from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.core.database import get_db
from app.models.user import User
from app.schemas.document import AuditResultResponse
from app.services.document_service import DocumentProcessingError, DocumentService

router = APIRouter(prefix="/audit", tags=["Audit"])


@router.get("/documents/{document_id}", response_model=AuditResultResponse)
def get_document_audit(
    document_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> AuditResultResponse:
    try:
        status_response = DocumentService(db).get_status(current_user.id, document_id)
    except DocumentProcessingError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
    if not status_response.audit:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Audit result not found")
    return status_response.audit
