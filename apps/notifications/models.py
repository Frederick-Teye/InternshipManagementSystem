from __future__ import annotations

from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

from apps.accounts.models import User


class Notification(models.Model):
    """
    In-app notification model to track system notifications for users.
    """

    class NotificationType(models.TextChoices):
        INFO = "info", "Information"
        SUCCESS = "success", "Success"
        WARNING = "warning", "Warning"
        ERROR = "error", "Error"

    class NotificationCategory(models.TextChoices):
        ATTENDANCE = "attendance", "Attendance"
        ASSESSMENT = "assessment", "Assessment"
        ABSENTEEISM = "absenteeism", "Absenteeism"
        ONBOARDING = "onboarding", "Onboarding"
        SYSTEM = "system", "System"
        GENERAL = "general", "General"

    recipient = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="notifications",
        help_text="User who will receive this notification",
    )
    
    title = models.CharField(
        max_length=255,
        help_text="Short title for the notification",
    )
    
    message = models.TextField(
        help_text="Detailed notification message",
    )
    
    notification_type = models.CharField(
        max_length=20,
        choices=NotificationType.choices,
        default=NotificationType.INFO,
        help_text="Visual type of notification (info, success, warning, error)",
    )
    
    category = models.CharField(
        max_length=20,
        choices=NotificationCategory.choices,
        default=NotificationCategory.GENERAL,
        help_text="Category of notification for filtering",
    )
    
    is_read = models.BooleanField(
        default=False,
        help_text="Whether the notification has been read",
    )
    
    read_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When the notification was read",
    )
    
    action_url = models.CharField(
        max_length=500,
        blank=True,
        help_text="Optional URL to navigate to when clicked",
    )
    
    # Generic relation to any model (attendance, assessment, etc.)
    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        help_text="Type of related object",
    )
    object_id = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="ID of related object",
    )
    related_object = GenericForeignKey("content_type", "object_id")
    
    email_sent = models.BooleanField(
        default=False,
        help_text="Whether an email notification was sent",
    )
    
    email_sent_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When the email was sent",
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="When the notification was created",
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="When the notification was last updated",
    )

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["recipient", "-created_at"]),
            models.Index(fields=["recipient", "is_read"]),
            models.Index(fields=["category"]),
        ]

    def __str__(self):
        return f"{self.title} - {self.recipient.get_full_name()}"

    def mark_as_read(self):
        """Mark notification as read"""
        from django.utils import timezone
        if not self.is_read:
            self.is_read = True
            self.read_at = timezone.now()
            self.save(update_fields=["is_read", "read_at"])


class NotificationPreference(models.Model):
    """
    User preferences for notification delivery.
    """
    
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="notification_preferences",
        help_text="User these preferences belong to",
    )
    
    # Email preferences
    email_on_attendance_approval = models.BooleanField(
        default=True,
        help_text="Send email when attendance is approved/rejected",
    )
    
    email_on_assessment_created = models.BooleanField(
        default=True,
        help_text="Send email when new assessment is created",
    )
    
    email_on_assessment_reviewed = models.BooleanField(
        default=True,
        help_text="Send email when assessment is reviewed",
    )
    
    email_on_absence_status = models.BooleanField(
        default=True,
        help_text="Send email when absence request status changes",
    )
    
    email_on_onboarding = models.BooleanField(
        default=True,
        help_text="Send email for onboarding events",
    )
    
    # In-app preferences
    in_app_notifications = models.BooleanField(
        default=True,
        help_text="Show in-app notifications",
    )
    
    # Digest preferences
    daily_digest = models.BooleanField(
        default=False,
        help_text="Receive daily digest of notifications",
    )
    
    weekly_digest = models.BooleanField(
        default=False,
        help_text="Receive weekly digest of notifications",
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Notification Preference"
        verbose_name_plural = "Notification Preferences"

    def __str__(self):
        return f"Notification Preferences for {self.user.get_full_name()}"
