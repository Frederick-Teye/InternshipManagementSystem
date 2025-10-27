from django.apps import AppConfig


class LogConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.log"
    verbose_name = "Activity Log"

    def ready(self):
        # Import signal handlers to ensure they're registered when Django starts
        try:
            from . import signals  # noqa: F401
        except Exception:
            # If signals cannot be imported during some management commands, fail silently
            pass
