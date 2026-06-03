from datetime import date

from pydantic import BaseModel, ConfigDict

from app.models.subscription import PlanType, SubscriptionStatus


class UsageCounter(BaseModel):
    used: int
    limit: int | None
    remaining: int | None


class UsageSummaryResponse(BaseModel):
    model_config = ConfigDict(use_enum_values=True)

    plan: PlanType
    status: SubscriptionStatus
    usage_date: date
    questions: UsageCounter
    uploads: UsageCounter
