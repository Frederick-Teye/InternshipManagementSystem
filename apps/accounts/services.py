"""Email services for the Internship Management System."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags

if TYPE_CHECKING:  # pragma: no cover - import for type checking only
    from apps.accounts.models import User


logger = logging.getLogger(__name__)


class EmailService:
    """Service for sending emails throughout the application"""

    @staticmethod
    def send_email(
        subject: str,
        message: str,
        recipient_list: list[str],
        html_message: str | None = None,
        from_email: str | None = None,
    ) -> bool:
        """
        Send an email with optional HTML content

        Args:
            subject: Email subject
            message: Plain text message
            recipient_list: List of recipient email addresses
            html_message: Optional HTML version of the message
            from_email: Optional sender email (defaults to DEFAULT_FROM_EMAIL)

        Returns:
            bool: True if email was sent successfully
        """
        if not recipient_list:
            logger.warning("Attempted to send email without recipients: %s", subject)
            return False

        valid_recipients = [email for email in recipient_list if email]
        if len(valid_recipients) != len(recipient_list):
            logger.warning(
                "Email recipients contained empty values, email '%s' not sent.", subject
            )
            return False

        try:
            sent_count = send_mail(
                subject=subject,
                message=message,
                from_email=from_email or settings.DEFAULT_FROM_EMAIL,
                recipient_list=valid_recipients,
                html_message=html_message,
                fail_silently=False,
            )
            if sent_count <= 0:
                logger.warning("Email backend returned 0 for '%s'", subject)
                return False
            return True
        except Exception:
            return False

    @staticmethod
    def send_template_email(
        subject: str,
        template_name: str,
        context: dict,
        recipient_list: list[str],
        from_email: str | None = None,
    ) -> bool:
        """
        Send an email using a Django template

        Args:
            subject: Email subject
            template_name: Template name (without .html extension)
            context: Template context variables
            recipient_list: List of recipient email addresses
            from_email: Optional sender email

        Returns:
            bool: True if email was sent successfully
        """
        try:
            if not recipient_list:
                logger.warning(
                    "Attempted to send template email '%s' without recipients.", subject
                )
                return False

            html_message = render_to_string(f"emails/{template_name}.html", context)
            plain_message = strip_tags(html_message)

            return EmailService.send_email(
                subject=subject,
                message=plain_message,
                recipient_list=recipient_list,
                html_message=html_message,
                from_email=from_email,
            )
        except Exception:
            return False

    @staticmethod
    def send_welcome_email(user_email: str, user_name: str) -> bool:
        """Send welcome email to new users"""
        subject = "Welcome to the Internship Management System"
        context = {
            "user_name": user_name,
            "login_url": settings.SITE_URL or "http://localhost:8000",
        }

        return EmailService.send_template_email(
            subject=subject,
            template_name="welcome",
            context=context,
            recipient_list=[user_email],
        )

    @staticmethod
    def send_password_reset_email(user_email: str, reset_url: str) -> bool:
        """Send password reset email"""
        subject = "Password Reset Request"
        context = {
            "reset_url": reset_url,
            "user_email": user_email,
        }

        return EmailService.send_template_email(
            subject=subject,
            template_name="password_reset",
            context=context,
            recipient_list=[user_email],
        )

    @staticmethod
    def send_notification_email(
        recipient,
        notification,
        context: dict | None = None,
    ) -> bool:
        """
        Send notification email to a user

        Args:
            recipient: User instance to send email to
            notification: Notification instance
            context: Additional template context (optional)

        Returns:
            bool: True if email was sent successfully
        """
        subject = f"[IMS] {notification.title}"

        template_context = {
            "notification": notification,
            "user": recipient,
            "site_url": (
                settings.SITE_URL
                if hasattr(settings, "SITE_URL")
                else "http://localhost:8000"
            ),
        }

        if context:
            template_context.update(context)

        return EmailService.send_template_email(
            subject=subject,
            template_name="notification_email",
            context=template_context,
            recipient_list=[recipient.email],
        )

    @staticmethod
    def send_onboarding_email(
        user: "User",
        temporary_password: str,
        onboarding_url: str,
        login_url: str,
        expires_at,
        created_by: str | None = None,
    ) -> bool:
        """
        Send an onboarding email with credentials and onboarding instructions.

        Args:
            user: Newly created user instance.
            temporary_password: The temporary password assigned to the user.
            onboarding_url: Absolute URL to the onboarding flow.
            login_url: Absolute URL to the login page.
            expires_at: Datetime when the onboarding link expires.
            created_by: Optional name of the administrator who created the account.

        Returns:
            bool: True if the email was sent successfully.
        """

        context = {
            "user": user,
            "temporary_password": temporary_password,
            "onboarding_url": onboarding_url,
            "login_url": login_url,
            "expires_at": expires_at,
            "created_by": created_by,
            "site_name": getattr(settings, "SITE_NAME", "Internship Management System"),
        }

        subject = "Your Internship Management System account"

        return EmailService.send_template_email(
            subject=subject,
            template_name="onboarding_invitation",
            context=context,
            recipient_list=[user.email],
        )
