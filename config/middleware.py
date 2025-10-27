import logging
from collections.abc import Callable
from typing import Any

from django.http import HttpRequest, HttpResponse


class ActivityLoggingMiddleware:
    """Log authenticated POST-like requests for auditing."""

    _AUDITED_METHODS = {"POST", "PUT", "PATCH", "DELETE"}
    _EXCLUDED_PATH_PREFIXES = (
        "/static/",
        "/media/",
        "/admin/jsi18n",
    )

    def __init__(self, get_response: Callable[[HttpRequest], HttpResponse]) -> None:
        self.get_response = get_response
        self.logger = logging.getLogger("ims.activity")

    def __call__(self, request: HttpRequest) -> HttpResponse:
        response = self.get_response(request)

        try:
            if (
                request.user.is_authenticated
                and request.method in self._AUDITED_METHODS
                and not self._is_excluded_path(request.path)
            ):
                self.logger.info(
                    "action=request user=%s method=%s path=%s status=%s ip=%s",
                    request.user.get_username(),
                    request.method,
                    request.path,
                    response.status_code,
                    self._get_client_ip(request),
                )
        except Exception:  # pragma: no cover - defensive guard
            logging.getLogger(__name__).exception("Failed to write activity log entry")

        return response

    @staticmethod
    def _is_excluded_path(path: str) -> bool:
        return any(
            path.startswith(prefix)
            for prefix in ActivityLoggingMiddleware._EXCLUDED_PATH_PREFIXES
        )

    @staticmethod
    def _get_client_ip(request: HttpRequest) -> str:
        forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        return request.META.get("REMOTE_ADDR", "-")
