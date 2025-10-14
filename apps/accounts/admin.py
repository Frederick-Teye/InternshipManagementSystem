from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin

from apps.accounts.models import OnboardingInvitation, User


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


@admin.register(OnboardingInvitation)
class OnboardingInvitationAdmin(admin.ModelAdmin):
    list_display = ("user", "token", "expires_at", "used", "created_at")
    list_filter = ("used", "expires_at")
    search_fields = ("user__username", "user__email", "token")
    readonly_fields = ("created_at",)
