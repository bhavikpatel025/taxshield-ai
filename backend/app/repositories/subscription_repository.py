from datetime import date
from uuid import UUID

from sqlalchemy.orm import Session

from app.models.subscription import PlanType, Subscription, SubscriptionStatus
from app.models.usage import UsageTracking, UsageType


class SubscriptionRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_for_user(self, user_id: UUID) -> Subscription | None:
        return self.db.query(Subscription).filter(Subscription.user_id == user_id).first()

    def create_free_for_user(self, user_id: UUID) -> Subscription:
        subscription = Subscription(
            user_id=user_id,
            plan=PlanType.FREE,
            status=SubscriptionStatus.ACTIVE,
            daily_question_limit=5,
            daily_upload_limit=1,
        )
        self.db.add(subscription)
        return subscription

    def get_usage(self, user_id: UUID, usage_type: UsageType, usage_date: date) -> UsageTracking | None:
        return (
            self.db.query(UsageTracking)
            .filter(
                UsageTracking.user_id == user_id,
                UsageTracking.usage_type == usage_type,
                UsageTracking.usage_date == usage_date,
            )
            .first()
        )

    def get_or_create_usage(self, user_id: UUID, usage_type: UsageType, usage_date: date) -> UsageTracking:
        usage = self.get_usage(user_id, usage_type, usage_date)
        if usage:
            return usage
        usage = UsageTracking(user_id=user_id, usage_type=usage_type, usage_date=usage_date, count=0)
        self.db.add(usage)
        return usage
