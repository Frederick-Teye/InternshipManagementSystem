"""
Email services for the Internship Management System
"""

from __future__ import annotations

from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags


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
        try:
            send_mail(
                subject=subject,
                message=message,
                from_email=from_email or settings.DEFAULT_FROM_EMAIL,
                recipient_list=recipient_list,
                html_message=html_message,
                fail_silently=False,
            )
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
