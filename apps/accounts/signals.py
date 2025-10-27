import logging
from typing import Any

from django.contrib.auth import get_user_model
from django.contrib.auth.signals import (
    user_logged_in,
    user_logged_out,
    user_login_failed,
)
from django.dispatch import receiver
from django.http import HttpRequest


logger = logging.getLogger("ims.activity")
User = get_user_model()


def _client_ip(request: HttpRequest | None) -> str:
    if not request:
        return "-"
    forwarded_for = (
        request.META.get("HTTP_X_FORWARDED_FOR") if hasattr(request, "META") else None
    )
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR", "-") if hasattr(request, "META") else "-"


def _user_identifier(user: Any) -> str:
    if isinstance(user, User):
        return user.get_username()
    if isinstance(user, str):
        return user
    return "unknown"


@receiver(user_logged_in)
def log_user_logged_in(sender, request, user, **kwargs):  # type: ignore[override]
    logger.info(
        "login user=%s status=success ip=%s",
        _user_identifier(user),
        _client_ip(request),
    )


@receiver(user_logged_out)
def log_user_logged_out(sender, request, user, **kwargs):  # type: ignore[override]
    logger.info(
        "logout user=%s ip=%s",
        _user_identifier(user),
        _client_ip(request),
    )


@receiver(user_login_failed)
def log_user_login_failed(sender, credentials, request, **kwargs):  # type: ignore[override]
    logger.warning(
        "login user=%s status=failed ip=%s",
        _user_identifier(credentials.get("username")),
        _client_ip(request),
    )
