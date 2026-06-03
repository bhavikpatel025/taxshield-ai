from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.core.database import get_db
from app.models.question import QuestionHistory
from app.models.user import User
from app.schemas.qa import AskQuestionRequest, AskQuestionResponse, QuestionHistoryResponse
from app.services.qa_service import QAService
from app.services.subscription_service import QuotaExceededError

router = APIRouter(prefix="/qa", tags=["Tax Q&A"])


@router.post("/ask", response_model=AskQuestionResponse)
def ask_question(
    payload: AskQuestionRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> AskQuestionResponse:
    try:
        return QAService(db).ask(current_user.id, payload)
    except QuotaExceededError as exc:
        raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail=str(exc))


@router.get("/history", response_model=list[QuestionHistoryResponse])
def list_question_history(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[QuestionHistory]:
    return QAService(db).list_history(current_user.id)
