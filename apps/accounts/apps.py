from django.apps import AppConfig


class AccountsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.accounts"
    verbose_name = "Accounts"

    def ready(self) -> None:
        # Import signal handlers to hook into authentication events.
        from . import signals  # noqa: F401

        return super().ready()
