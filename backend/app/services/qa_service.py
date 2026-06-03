import hashlib
from uuid import UUID

from sqlalchemy.orm import Session

from app.models.question import CitationRecord, QuestionHistory, QuestionStatus
from app.models.usage import UsageType
from app.repositories.qa_repository import QARepository
from app.schemas.qa import AskQuestionRequest, AskQuestionResponse
from app.services.citation_validator import CitationValidator
from app.services.llm_service import MockGroundedLLMService
from app.services.rag_retriever import LocalTaxLawRetriever
from app.services.subscription_service import SubscriptionService


class QAService:
    MIN_VALID_RETRIEVAL_SCORE = 4.0

    def __init__(self, db: Session):
        self.db = db
        self.repository = QARepository(db)
        self.subscriptions = SubscriptionService(db)
        self.retriever = LocalTaxLawRetriever()
        self.llm = MockGroundedLLMService()
        self.citation_validator = CitationValidator()

    def ask(self, user_id: UUID, payload: AskQuestionRequest) -> AskQuestionResponse:
        self.subscriptions.ensure_quota_available(user_id, UsageType.QUESTION)
        chunks = [
            chunk
            for chunk in self.retriever.retrieve(payload.question)
            if chunk.score >= self.MIN_VALID_RETRIEVAL_SCORE
        ]
        llm_response = self.llm.answer(payload.question, chunks)
        validated_citations = self.citation_validator.validate(llm_response.citations, chunks)

        is_supported = bool(validated_citations)
        status = QuestionStatus.ANSWERED if is_supported else QuestionStatus.UNSUPPORTED
        answer = llm_response.answer if is_supported else MockGroundedLLMService.UNSUPPORTED_MESSAGE
        confidence = llm_response.confidence if is_supported else 0.0

        self.subscriptions.enforce_and_increment(user_id, UsageType.QUESTION)
        question_record = QuestionHistory(
            user_id=user_id,
            question_hash=self._hash_question(payload.question),
            status=status,
            confidence=confidence,
            retrieved_chunk_count=len(chunks),
            unsupported_reason=None if is_supported else "No validated citations found",
        )
        self.repository.add_question(question_record)
        self.db.flush()

        for citation in validated_citations:
            self.repository.add_citation(
                CitationRecord(
                    question_id=question_record.id,
                    source_id=citation.source_id,
                    source_title=citation.source_title,
                    section=citation.section,
                    source_url=citation.source_url,
                    validated=citation.validated,
                )
            )

        self.db.commit()
        self.db.refresh(question_record)
        return AskQuestionResponse(
            question_id=question_record.id,
            status=status,
            answer=answer,
            confidence=confidence,
            citations=validated_citations,
        )

    def list_history(self, user_id: UUID) -> list[QuestionHistory]:
        return self.repository.list_history_for_user(user_id)

    @staticmethod
    def _hash_question(question: str) -> str:
        normalized = " ".join(question.strip().lower().split())
        return hashlib.sha256(normalized.encode("utf-8")).hexdigest()
