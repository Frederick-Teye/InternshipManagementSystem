from __future__ import annotations

from typing import Any

from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from apps.log.utils import log_activity


User = get_user_model()


def _make_action(instance: Any, created: bool) -> str:
    model_name = instance.__class__.__name__
    return f"Created {model_name}" if created else f"Updated {model_name}"


@receiver(post_save)
def model_post_save(sender, instance, created, **kwargs):
    """Generic handler to log create/update for selected app models."""
    # Only log models we care about to avoid noisy logs
    from apps.interns.models import InternProfile

    # Import other models lazily
    try:
        from apps.attendance.models import Attendance
    except Exception:
        Attendance = None

    try:
        from apps.evaluations.models import PerformanceAssessment
    except Exception:
        PerformanceAssessment = None

    try:
        from apps.absenteeism.models import AbsenteeismRequest
    except Exception:
        AbsenteeismRequest = None

    interesting_models = (
        InternProfile,
        Attendance,
        PerformanceAssessment,
        AbsenteeismRequest,
        User,
    )

    if sender in interesting_models:
        # Try to determine actor if available (e.g., for saves triggered by code, actor is unknown)
        actor = None
        # If instance has a user or actor field, prefer that
        for attr in (
            "user",
            "actor",
            "internal_supervisor",
            "approved_by",
            "assessed_by",
        ):
            if hasattr(instance, attr):
                try:
                    val = getattr(instance, attr)
                    # If it's a related object, try to extract user
                    if hasattr(val, "user"):
                        actor = getattr(val, "user")
                    else:
                        actor = val
                    break
                except Exception:
                    continue

        action = _make_action(instance, created)

        # Minimal metadata: store model and pk
        metadata = {"model": sender.__name__, "pk": str(getattr(instance, "pk", ""))}

        # Record a snapshot of instance fields for reference (non-exhaustive)
        try:
            data = {}
            for field in getattr(instance, "_meta").fields:
                name = field.name
                try:
                    data[name] = getattr(instance, name)
                except Exception:
                    data[name] = None
            metadata["snapshot"] = data
        except Exception:
            pass

        # Log the event
        log_activity(actor=actor, action=action, obj=instance, metadata=metadata)


@receiver(post_delete)
def model_post_delete(sender, instance, **kwargs):
    """Generic handler to log deletions for selected app models."""
    from apps.interns.models import InternProfile

    try:
        from apps.attendance.models import Attendance
    except Exception:
        Attendance = None

    try:
        from apps.evaluations.models import PerformanceAssessment
    except Exception:
        PerformanceAssessment = None

    try:
        from apps.absenteeism.models import AbsenteeismRequest
    except Exception:
        AbsenteeismRequest = None

    interesting_models = (
        InternProfile,
        Attendance,
        PerformanceAssessment,
        AbsenteeismRequest,
        User,
    )

    if sender in interesting_models:
        actor = None
        for attr in (
            "user",
            "actor",
            "internal_supervisor",
            "approved_by",
            "assessed_by",
        ):
            if hasattr(instance, attr):
                try:
                    val = getattr(instance, attr)
                    if hasattr(val, "user"):
                        actor = getattr(val, "user")
                    else:
                        actor = val
                    break
                except Exception:
                    continue

        action = f"Deleted {sender.__name__}"

        metadata = {"model": sender.__name__, "pk": str(getattr(instance, "pk", ""))}

        log_activity(actor=actor, action=action, obj=instance, metadata=metadata)
