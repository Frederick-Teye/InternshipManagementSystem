from __future__ import annotations

from django.contrib import admin

from apps.notifications.models import Notification, NotificationPreference


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = [
        "title",
        "recipient",
        "category",
        "notification_type",
        "is_read",
        "created_at",
    ]
    list_filter = ["category", "notification_type", "is_read", "created_at"]
    search_fields = [
        "title",
        "message",
        "recipient__email",
        "recipient__first_name",
        "recipient__last_name",
    ]
    readonly_fields = ["created_at", "updated_at", "read_at", "email_sent_at"]
    date_hierarchy = "created_at"

    fieldsets = (
        (
            "Notification Info",
            {
                "fields": (
                    "recipient",
                    "title",
                    "message",
                    "notification_type",
                    "category",
                )
            },
        ),
        ("Status", {"fields": ("is_read", "read_at", "email_sent", "email_sent_at")}),
        ("Action", {"fields": ("action_url",)}),
        (
            "Related Object",
            {"fields": ("content_type", "object_id"), "classes": ("collapse",)},
        ),
        (
            "Timestamps",
            {"fields": ("created_at", "updated_at"), "classes": ("collapse",)},
        ),
    )


@admin.register(NotificationPreference)
class NotificationPreferenceAdmin(admin.ModelAdmin):
    list_display = [
        "user",
        "in_app_notifications",
        "email_on_attendance_approval",
        "email_on_assessment_created",
        "daily_digest",
        "weekly_digest",
    ]
    search_fields = ["user__email", "user__first_name", "user__last_name"]
    list_filter = ["in_app_notifications", "daily_digest", "weekly_digest"]

    fieldsets = (
        ("User", {"fields": ("user",)}),
        (
            "Email Notifications",
            {
                "fields": (
                    "email_on_attendance_approval",
                    "email_on_assessment_created",
                    "email_on_assessment_reviewed",
                    "email_on_absence_status",
                    "email_on_onboarding",
                )
            },
        ),
        ("In-App Notifications", {"fields": ("in_app_notifications",)}),
        ("Digest Preferences", {"fields": ("daily_digest", "weekly_digest")}),
    )
