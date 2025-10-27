from __future__ import annotations

from typing import Any

from django.contrib.contenttypes.models import ContentType
from django.utils import timezone

from apps.log.models import ActivityLog


def log_activity(
    actor: Any | None,
    action: str,
    obj: Any | None = None,
    changes: dict | None = None,
    metadata: dict | None = None,
    request: Any | None = None,
) -> ActivityLog:
    """Create an ActivityLog entry.

    Parameters
    - actor: User instance or None for system actions
    - action: short human readable action description
    - obj: optional model instance that was affected
    - changes: optional dict describing before/after values
    - metadata: optional additional context
    - request: optional HttpRequest (used to extract IP and user agent)

    Returns the created ActivityLog instance.
    """
    content_type = None
    object_id = ""

    if obj is not None:
        try:
            content_type = ContentType.objects.get_for_model(obj)
            # store stringified pk to keep it generic
            object_id = str(getattr(obj, "pk", ""))
        except Exception:
            content_type = None
            object_id = str(getattr(obj, "pk", ""))

    ip_address = None
    user_agent = ""
    if request is not None:
        # X-Forwarded-For may contain multiple IPs - take first
        xff = request.META.get("HTTP_X_FORWARDED_FOR")
        if xff:
            ip_address = xff.split(",")[0].strip()
        else:
            ip_address = request.META.get("REMOTE_ADDR")

        user_agent = request.META.get("HTTP_USER_AGENT", "")[:512]

    def _sanitize(obj):
        """Recursively convert common non-JSON types to JSON-friendly representations."""
        from datetime import date, datetime

        if obj is None:
            return None
        if isinstance(obj, (str, int, float, bool)):
            return obj
        if isinstance(obj, (datetime, date)):
            return obj.isoformat()
        if isinstance(obj, dict):
            return {str(k): _sanitize(v) for k, v in obj.items()}
        if isinstance(obj, (list, tuple, set)):
            return [_sanitize(v) for v in obj]
        # Fallback to string representation for objects (including model instances)
        try:
            return str(obj)
        except Exception:
            return None

    safe_changes = _sanitize(changes) if changes is not None else None
    safe_metadata = _sanitize(metadata) if metadata is not None else None

    log = ActivityLog.objects.create(
        actor=actor if actor is not None else None,
        action=action[:255],
        content_type=content_type,
        object_id=object_id,
        changes=safe_changes,
        metadata=safe_metadata,
        ip_address=ip_address,
        user_agent=user_agent,
        timestamp=timezone.now(),
    )

    return log
