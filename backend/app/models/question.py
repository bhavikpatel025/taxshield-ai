import enum
import uuid
from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, Enum, Float, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.core.database import Base


class QuestionStatus(str, enum.Enum):
    ANSWERED = "answered"
    UNSUPPORTED = "unsupported"
    FAILED = "failed"


class QuestionHistory(Base):
    __tablename__ = "question_history"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    question_hash = Column(String(64), nullable=False, index=True)
    status = Column(Enum(QuestionStatus), nullable=False)
    confidence = Column(Float, nullable=False, default=0.0)
    retrieved_chunk_count = Column(Integer, nullable=False, default=0)
    unsupported_reason = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    user = relationship("User", back_populates="question_history")
    citations = relationship("CitationRecord", back_populates="question", cascade="all, delete-orphan")


class CitationRecord(Base):
    __tablename__ = "citation_records"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    question_id = Column(UUID(as_uuid=True), ForeignKey("question_history.id"), nullable=False, index=True)
    source_id = Column(String(100), nullable=False)
    source_title = Column(String(255), nullable=False)
    section = Column(String(100), nullable=False)
    source_url = Column(String(500), nullable=True)
    validated = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    question = relationship("QuestionHistory", back_populates="citations")
