"""
Notification service for creating and sending notifications.
"""

from __future__ import annotations

from typing import Optional, List
from django.contrib.contenttypes.models import ContentType
from apps.accounts.services import EmailService
from django.template.loader import render_to_string
from django.conf import settings
from django.utils import timezone
from django.urls import reverse

from apps.notifications.models import Notification, NotificationPreference
from apps.accounts.models import User


class NotificationService:
    """Service for managing notifications"""

    @staticmethod
    def create_notification(
        recipient: User,
        title: str,
        message: str,
        notification_type: str = "info",
        category: str = "general",
        action_url: str = "",
        related_object: Optional[object] = None,
        send_email: bool = False,
    ) -> Notification:
        """
        Create a new notification for a user.

        Args:
            recipient: User to receive the notification
            title: Short title
            message: Detailed message
            notification_type: Type (info, success, warning, error)
            category: Category (attendance, assessment, etc.)
            action_url: Optional URL to navigate to
            related_object: Optional related Django model instance
            send_email: Whether to send email notification

        Returns:
            Created Notification instance
        """
        notification_data = {
            "recipient": recipient,
            "title": title,
            "message": message,
            "notification_type": notification_type,
            "category": category,
            "action_url": action_url,
        }

        # Add related object if provided
        if related_object:
            notification_data["content_type"] = ContentType.objects.get_for_model(
                related_object
            )
            notification_data["object_id"] = related_object.pk

        notification = Notification.objects.create(**notification_data)

        # Send email if requested and user has email notifications enabled
        if send_email:
            NotificationService._send_email_notification(notification)

        return notification

    @staticmethod
    def create_bulk_notifications(
        recipients: List[User],
        title: str,
        message: str,
        notification_type: str = "info",
        category: str = "general",
        action_url: str = "",
        send_email: bool = False,
    ) -> List[Notification]:
        """
        Create notifications for multiple users at once.

        Args:
            recipients: List of users to receive notification
            title: Short title
            message: Detailed message
            notification_type: Type (info, success, warning, error)
            category: Category (attendance, assessment, etc.)
            action_url: Optional URL to navigate to
            send_email: Whether to send email notifications

        Returns:
            List of created Notification instances
        """
        notifications = []
        for recipient in recipients:
            notification = NotificationService.create_notification(
                recipient=recipient,
                title=title,
                message=message,
                notification_type=notification_type,
                category=category,
                action_url=action_url,
                send_email=send_email,
            )
            notifications.append(notification)

        return notifications

    @staticmethod
    def _send_email_notification(notification: Notification) -> bool:
        """
        Send email notification to user.

        Args:
            notification: Notification instance to send

        Returns:
            True if email sent successfully, False otherwise
        """
        try:
            # Check user preferences
            preferences = NotificationService._get_or_create_preferences(
                notification.recipient
            )

            # Check if user wants email for this category
            if not NotificationService._should_send_email(notification, preferences):
                return False

            # Prepare email context
            context = {
                "notification": notification,
                "user": notification.recipient,
                "site_url": (
                    settings.SITE_URL
                    if hasattr(settings, "SITE_URL")
                    else "http://localhost:8000"
                ),
            }

            # Send email using EmailService
            success = EmailService.send_notification_email(
                recipient=notification.recipient,
                notification=notification,
                context=context,
            )

            if success:
                # Mark as sent
                notification.email_sent = True
                notification.email_sent_at = timezone.now()
                notification.save(update_fields=["email_sent", "email_sent_at"])

            return success

        except Exception as e:
            print(f"Error sending email notification: {e}")
            return False

    @staticmethod
    def _get_or_create_preferences(user: User) -> NotificationPreference:
        """Get or create notification preferences for a user"""
        preferences, created = NotificationPreference.objects.get_or_create(user=user)
        return preferences

    @staticmethod
    def _should_send_email(
        notification: Notification, preferences: NotificationPreference
    ) -> bool:
        """Check if email should be sent based on user preferences"""
        if not preferences.in_app_notifications:
            return False

        category_mapping = {
            "attendance": preferences.email_on_attendance_approval,
            "assessment": preferences.email_on_assessment_created
            or preferences.email_on_assessment_reviewed,
            "absenteeism": preferences.email_on_absence_status,
            "onboarding": preferences.email_on_onboarding,
        }

        return category_mapping.get(notification.category, True)

    @staticmethod
    def mark_all_as_read(user: User) -> int:
        """
        Mark all notifications as read for a user.

        Args:
            user: User whose notifications to mark as read

        Returns:
            Number of notifications marked as read
        """
        count = Notification.objects.filter(recipient=user, is_read=False).update(
            is_read=True, read_at=timezone.now()
        )
        return count

    @staticmethod
    def get_unread_count(user: User) -> int:
        """
        Get count of unread notifications for a user.

        Args:
            user: User to get unread count for

        Returns:
            Number of unread notifications
        """
        return Notification.objects.filter(recipient=user, is_read=False).count()

    @staticmethod
    def get_recent_notifications(user: User, limit: int = 10) -> List[Notification]:
        """
        Get recent notifications for a user.

        Args:
            user: User to get notifications for
            limit: Maximum number of notifications to return

        Returns:
            List of recent Notification instances
        """
        return list(
            Notification.objects.filter(recipient=user).order_by("-created_at")[:limit]
        )

    # Convenience methods for specific notification types

    @staticmethod
    def notify_attendance_approved(attendance, approver):
        """Notify intern that their attendance was approved"""
        NotificationService.create_notification(
            recipient=attendance.intern.user,
            title="Attendance Approved ✓",
            message=f"Your attendance for {attendance.check_in_time.strftime('%B %d, %Y')} has been approved by {approver.get_full_name()}.",
            notification_type="success",
            category="attendance",
            action_url=reverse("attendance:my_attendance"),
            related_object=attendance,
            send_email=True,
        )

    @staticmethod
    def notify_attendance_rejected(attendance, approver, reason=""):
        """Notify intern that their attendance was rejected"""
        message = f"Your attendance for {attendance.check_in_time.strftime('%B %d, %Y')} was rejected by {approver.get_full_name()}."
        if reason:
            message += f" Reason: {reason}"

        NotificationService.create_notification(
            recipient=attendance.intern.user,
            title="Attendance Rejected",
            message=message,
            notification_type="error",
            category="attendance",
            action_url=reverse("attendance:my_attendance"),
            related_object=attendance,
            send_email=True,
        )

    @staticmethod
    def notify_assessment_created(assessment, creator):
        """Notify intern that a new assessment was created"""
        NotificationService.create_notification(
            recipient=assessment.intern.user,
            title="New Assessment Available",
            message=f"Week {assessment.week_number} assessment has been created by {creator.get_full_name()}. Please complete your self-assessment.",
            notification_type="info",
            category="assessment",
            action_url=reverse("evaluations:view_assessment", args=[assessment.id]),
            related_object=assessment,
            send_email=True,
        )

    @staticmethod
    def notify_assessment_reviewed(assessment, reviewer):
        """Notify intern that their assessment was reviewed"""
        NotificationService.create_notification(
            recipient=assessment.intern.user,
            title="Assessment Reviewed",
            message=f"Your Week {assessment.week_number} assessment has been reviewed by {reviewer.get_full_name()}.",
            notification_type="success",
            category="assessment",
            action_url=reverse("evaluations:view_assessment", args=[assessment.id]),
            related_object=assessment,
            send_email=True,
        )

    @staticmethod
    def notify_absence_approved(absence_request, approver):
        """Notify intern that their absence request was approved"""
        NotificationService.create_notification(
            recipient=absence_request.intern.user,
            title="Absence Request Approved ✓",
            message=f"Your absence request for {absence_request.start_date} to {absence_request.end_date} has been approved by {approver.get_full_name()}.",
            notification_type="success",
            category="absenteeism",
            action_url=reverse("absenteeism:my_requests"),
            related_object=absence_request,
            send_email=True,
        )

    @staticmethod
    def notify_absence_rejected(absence_request, approver, reason=""):
        """Notify intern that their absence request was rejected"""
        message = f"Your absence request for {absence_request.start_date} to {absence_request.end_date} was rejected by {approver.get_full_name()}."
        if reason:
            message += f" Reason: {reason}"

        NotificationService.create_notification(
            recipient=absence_request.intern.user,
            title="Absence Request Rejected",
            message=message,
            notification_type="error",
            category="absenteeism",
            action_url=reverse("absenteeism:my_requests"),
            related_object=absence_request,
            send_email=True,
        )

    @staticmethod
    def notify_supervisor_new_absence_request(absence_request):
        """Notify supervisor of new absence request from intern"""
        if absence_request.intern.internal_supervisor:
            NotificationService.create_notification(
                recipient=absence_request.intern.internal_supervisor.user,
                title="New Absence Request Pending Approval",
                message=f"{absence_request.intern.user.get_full_name()} submitted an absence request for {absence_request.start_date} to {absence_request.end_date}. Reason: {absence_request.reason}",
                notification_type="info",
                category="absenteeism",
                action_url=reverse("absenteeism:pending_requests"),
                related_object=absence_request,
                send_email=True,  # Email supervisors about new absence requests
            )


# Convenience functions for specific notification types (for backward compatibility)


def notify_attendance_approved(attendance):
    """Notify intern that their attendance was approved"""
    NotificationService.create_notification(
        recipient=attendance.intern.user,
        title="Attendance Approved ✓",
        message=f"Your attendance for {attendance.check_in_time.strftime('%B %d, %Y')} has been approved.",
        notification_type="success",
        category="attendance",
        action_url=reverse("attendance:my_attendance"),
        related_object=attendance,
        send_email=True,
    )


def notify_attendance_rejected(attendance, reason=""):
    """Notify intern that their attendance was rejected"""
    message = f"Your attendance for {attendance.check_in_time.strftime('%B %d, %Y')} was rejected."
    if reason:
        message += f" Reason: {reason}"

    NotificationService.create_notification(
        recipient=attendance.intern.user,
        title="Attendance Rejected",
        message=message,
        notification_type="error",
        category="attendance",
        action_url=reverse("attendance:my_attendance"),
        related_object=attendance,
        send_email=True,
    )


def notify_assessment_created(assessment):
    """Notify intern that a new assessment was created"""
    NotificationService.create_notification(
        recipient=assessment.intern.user,
        title="New Assessment Available",
        message=f"Week {assessment.week_number} assessment is ready for your self-assessment.",
        notification_type="info",
        category="assessment",
        action_url=reverse("evaluations:self_assessment", args=[assessment.id]),
        related_object=assessment,
        send_email=True,
    )


def notify_assessment_reviewed(assessment):
    """Notify intern that their assessment was reviewed"""
    NotificationService.create_notification(
        recipient=assessment.intern.user,
        title="Assessment Reviewed",
        message=f"Your Week {assessment.week_number} assessment has been reviewed by your supervisor.",
        notification_type="success",
        category="assessment",
        action_url=reverse("evaluations:view_assessment", args=[assessment.id]),
        related_object=assessment,
        send_email=True,
    )


def notify_absence_approved(absence_request):
    """Notify intern that their absence request was approved"""
    NotificationService.create_notification(
        recipient=absence_request.intern.user,
        title="Absence Request Approved ✓",
        message=f"Your absence request for {absence_request.start_date} to {absence_request.end_date} has been approved.",
        notification_type="success",
        category="absenteeism",
        action_url=reverse("absenteeism:my_requests"),
        related_object=absence_request,
        send_email=True,
    )


def notify_absence_rejected(absence_request, reason=""):
    """Notify intern that their absence request was rejected"""
    message = f"Your absence request for {absence_request.start_date} to {absence_request.end_date} was rejected."
    if reason:
        message += f" Reason: {reason}"

    NotificationService.create_notification(
        recipient=absence_request.intern.user,
        title="Absence Request Rejected",
        message=message,
        notification_type="error",
        category="absenteeism",
        action_url=reverse("absenteeism:my_requests"),
        related_object=absence_request,
        send_email=True,
    )


def notify_supervisor_new_attendance(attendance):
    """Notify supervisor of new pending attendance"""
    if attendance.intern.internal_supervisor:
        NotificationService.create_notification(
            recipient=attendance.intern.internal_supervisor.user,
            title="New Attendance Pending Approval",
            message=f"{attendance.intern.user.get_full_name()} marked attendance on {attendance.check_in_time.strftime('%B %d, %Y')}.",
            notification_type="info",
            category="attendance",
            action_url=reverse("attendance:pending_approvals"),
            related_object=attendance,
            send_email=False,  # Don't email for every attendance
        )


def notify_supervisor_new_assessment(assessment):
    """Notify supervisor that intern submitted self-assessment"""
    if assessment.assessed_by:
        NotificationService.create_notification(
            recipient=assessment.assessed_by.user,
            title="Assessment Ready for Review",
            message=f"{assessment.intern.user.get_full_name()} completed self-assessment for Week {assessment.week_number}.",
            notification_type="info",
            category="assessment",
            action_url=reverse("evaluations:assess_intern", args=[assessment.id]),
            related_object=assessment,
            send_email=True,
        )
