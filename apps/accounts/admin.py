import logging

from django.conf import settings
from django.contrib import admin, messages
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from django.urls import reverse

from apps.accounts.services import EmailService
from apps.notifications.services import NotificationService

from apps.accounts.models import OnboardingInvitation, User


logger = logging.getLogger(__name__)


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    list_display = ("username", "email", "role", "is_active", "is_onboarded")
    list_filter = ("role", "is_staff", "is_superuser", "is_active")
    search_fields = ("username", "email", "first_name", "last_name")
    fieldsets = DjangoUserAdmin.fieldsets + (
        (
            "Internship Metadata",
            {
                "fields": (
                    "role",
                    "is_onboarded",
                    "onboarding_token",
                    "onboarding_token_expires_at",
                )
            },
        ),
    )
    readonly_fields = ("onboarding_token", "onboarding_token_expires_at")
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "username",
                    "email",
                    "password1",
                    "password2",
                    "role",
                    "is_staff",
                    "is_superuser",
                    "is_active",
                ),
            },
        ),
    )

    def save_model(self, request, obj, form, change):
        is_new = obj.pk is None
        raw_password = form.cleaned_data.get("password1") if not change else None

        super().save_model(request, obj, form, change)

        if not is_new:
            return

        # Fallback for programmatic creations where password1 is not provided
        if not raw_password:
            raw_password = User.objects.make_random_password()
            obj.set_password(raw_password)
            obj.save(update_fields=["password"])

        try:
            ttl_hours = getattr(settings, "ONBOARDING_LINK_TTL_HOURS", 24)
            token = obj.generate_onboarding_token(ttl_hours=ttl_hours)
            onboarding_path = reverse("accounts:onboarding", kwargs={"token": token})
            onboarding_url = request.build_absolute_uri(onboarding_path)
            login_url = request.build_absolute_uri(reverse("accounts:login"))
            created_by = request.user.get_full_name() or request.user.get_username()

            email_sent = False
            if obj.email:
                email_sent = EmailService.send_onboarding_email(
                    user=obj,
                    temporary_password=raw_password,
                    onboarding_url=onboarding_url,
                    login_url=login_url,
                    expires_at=obj.onboarding_token_expires_at,
                    created_by=created_by,
                )
            else:
                messages.warning(
                    request,
                    "User created without an email address. Onboarding email was not sent.",
                )

            NotificationService.create_notification(
                recipient=obj,
                title="Welcome to the Internship Management System",
                message=(
                    "Your account has been created. "
                    "Please check your email for onboarding instructions."
                ),
                notification_type="info",
                category="onboarding",
                action_url=reverse("accounts:dashboard"),
                send_email=False,
            )

            if email_sent:
                messages.success(
                    request,
                    f"Onboarding email sent to {obj.email}.",
                )
            elif obj.email:
                messages.warning(
                    request,
                    (
                        "User created but sending the onboarding email failed. "
                        "Please verify email settings."
                    ),
                )
        except Exception as exc:  # pragma: no cover - defensive guard
            logger.exception("Failed to send onboarding email for user %s", obj.pk)
            messages.error(
                request,
                "User created but onboarding email could not be sent. Check logs for details.",
            )


@admin.register(OnboardingInvitation)
class OnboardingInvitationAdmin(admin.ModelAdmin):
    list_display = ("user", "token", "expires_at", "used", "created_at")
    list_filter = ("used", "expires_at")
    search_fields = ("user__username", "user__email", "token")
    readonly_fields = ("created_at",)
