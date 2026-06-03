from datetime import date
from uuid import UUID

from sqlalchemy.orm import Session

from app.models.subscription import Subscription, SubscriptionStatus
from app.models.usage import UsageType
from app.repositories.subscription_repository import SubscriptionRepository
from app.schemas.subscription import UsageCounter, UsageSummaryResponse


class QuotaExceededError(Exception):
    pass


class SubscriptionService:
    def __init__(self, db: Session):
        self.db = db
        self.repository = SubscriptionRepository(db)

    def ensure_free_subscription(self, user_id: UUID) -> Subscription:
        subscription = self.repository.get_for_user(user_id)
        if subscription:
            return subscription
        return self.repository.create_free_for_user(user_id)

    def get_usage_summary(self, user_id: UUID) -> UsageSummaryResponse:
        subscription = self._get_active_subscription(user_id)
        today = date.today()
        question_usage = self.repository.get_or_create_usage(user_id, UsageType.QUESTION, today)
        upload_usage = self.repository.get_or_create_usage(user_id, UsageType.UPLOAD, today)
        self.db.flush()

        return UsageSummaryResponse(
            plan=subscription.plan,
            status=subscription.status,
            usage_date=today,
            questions=self._counter(question_usage.count, subscription.daily_question_limit),
            uploads=self._counter(upload_usage.count, subscription.daily_upload_limit),
        )

    def enforce_and_increment(self, user_id: UUID, usage_type: UsageType) -> None:
        subscription = self._get_active_subscription(user_id)
        usage = self._get_today_usage(user_id, usage_type)
        limit = self._limit_for_usage_type(subscription, usage_type)
        if limit is not None and usage.count >= limit:
            raise QuotaExceededError(f"Daily {usage_type.value} quota exceeded")
        usage.count += 1

    def ensure_quota_available(self, user_id: UUID, usage_type: UsageType) -> None:
        subscription = self._get_active_subscription(user_id)
        usage = self.repository.get_usage(user_id, usage_type, date.today())
        used = usage.count if usage else 0
        limit = self._limit_for_usage_type(subscription, usage_type)
        if limit is not None and used >= limit:
            raise QuotaExceededError(f"Daily {usage_type.value} quota exceeded")

    def _get_active_subscription(self, user_id: UUID) -> Subscription:
        subscription = self.repository.get_for_user(user_id)
        if not subscription:
            subscription = self.repository.create_free_for_user(user_id)
            self.db.flush()
        if subscription.status != SubscriptionStatus.ACTIVE:
            raise QuotaExceededError("Subscription is not active")
        return subscription

    @staticmethod
    def _counter(used: int, limit: int | None) -> UsageCounter:
        remaining = None if limit is None else max(limit - used, 0)
        return UsageCounter(used=used, limit=limit, remaining=remaining)

    def _get_today_usage(self, user_id: UUID, usage_type: UsageType):
        return self.repository.get_or_create_usage(user_id, usage_type, date.today())

    @staticmethod
    def _limit_for_usage_type(subscription: Subscription, usage_type: UsageType) -> int | None:
        if usage_type == UsageType.QUESTION:
            return subscription.daily_question_limit
        return subscription.daily_upload_limit
