from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.models.question import QuestionStatus


class AskQuestionRequest(BaseModel):
    question: str = Field(min_length=5, max_length=2000)


class CitationResponse(BaseModel):
    source_id: str
    source_title: str
    section: str
    source_url: str | None = None
    validated: bool


class AskQuestionResponse(BaseModel):
    question_id: UUID
    status: QuestionStatus
    answer: str
    confidence: float
    citations: list[CitationResponse]


class QuestionHistoryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, use_enum_values=True)

    id: UUID
    status: QuestionStatus
    confidence: float
    retrieved_chunk_count: int
    unsupported_reason: str | None
    created_at: datetime
