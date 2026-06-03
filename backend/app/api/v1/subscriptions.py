from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.core.database import get_db
from app.models.user import User
from app.schemas.subscription import UsageSummaryResponse
from app.services.subscription_service import SubscriptionService

router = APIRouter(prefix="/subscriptions", tags=["Subscriptions"])


@router.get("/usage", response_model=UsageSummaryResponse)
def get_usage_summary(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> UsageSummaryResponse:
    summary = SubscriptionService(db).get_usage_summary(current_user.id)
    db.commit()
    return summary
