from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from app.models.document import DocumentStatus


class AuditFlagResponse(BaseModel):
    code: str
    description: str
    severity: str
    supporting_tax_authority: str


class AuditResultResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, use_enum_values=True)

    id: UUID
    risk_level: str
    flags: list[AuditFlagResponse]
    created_at: datetime


class DocumentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, use_enum_values=True)

    id: UUID
    filename: str
    file_type: str
    status: DocumentStatus
    processed_at: datetime | None
    created_at: datetime


class DocumentUploadResponse(BaseModel):
    document: DocumentResponse
    audit: AuditResultResponse


class DocumentStatusResponse(BaseModel):
    document: DocumentResponse
    audit: AuditResultResponse | None = None
