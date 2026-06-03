from uuid import UUID

from sqlalchemy.orm import Session

from app.models.question import CitationRecord, QuestionHistory


class QARepository:
    def __init__(self, db: Session):
        self.db = db

    def add_question(self, question: QuestionHistory) -> QuestionHistory:
        self.db.add(question)
        return question

    def add_citation(self, citation: CitationRecord) -> CitationRecord:
        self.db.add(citation)
        return citation

    def list_history_for_user(self, user_id: UUID, limit: int = 50) -> list[QuestionHistory]:
        return (
            self.db.query(QuestionHistory)
            .filter(QuestionHistory.user_id == user_id)
            .order_by(QuestionHistory.created_at.desc())
            .limit(limit)
            .all()
        )
