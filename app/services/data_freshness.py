from datetime import datetime, timedelta, timezone

from app.models.agent import AgentStatus


def freshness_status(
    observed_at: datetime | None,
    max_age: timedelta,
    now: datetime | None = None,
) -> AgentStatus:
    if observed_at is None:
        return AgentStatus.UNAVAILABLE
    current_time = now or datetime.now(timezone.utc)
    if observed_at.tzinfo is None:
        observed_at = observed_at.replace(tzinfo=timezone.utc)
    if current_time.tzinfo is None:
        current_time = current_time.replace(tzinfo=timezone.utc)
    if current_time - observed_at > max_age:
        return AgentStatus.STALE
    return AgentStatus.COMPLETE