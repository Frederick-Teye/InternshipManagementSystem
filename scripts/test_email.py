#!/usr/bin/env python
"""
Script to test email functionality in the Internship Management System.
Run this script to verify that email notifications are working correctly.
"""

import os
import sys
import django

# Add the project directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Setup Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from django.core.mail import send_mail
from django.conf import settings
from apps.accounts.services import EmailService
from apps.notifications.services import NotificationService
from apps.accounts.models import User


def test_basic_email():
    """Test basic Django email functionality"""
    print("Testing basic email functionality...")

    try:
        result = send_mail(
            subject="Test Email from IMS",
            message="This is a test email from the Internship Management System.",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=["test@example.com"],
            fail_silently=False,
        )
        print(f"✅ Basic email test: {'SUCCESS' if result else 'FAILED'}")
        return result > 0
    except Exception as e:
        print(f"❌ Basic email test FAILED: {e}")
        return False


def test_email_service():
    """Test the EmailService class"""
    print("\nTesting EmailService...")

    try:
        result = EmailService.send_email(
            subject="Test Email Service",
            message="Testing the EmailService class.",
            recipient_list=["test@example.com"],
        )
        print(f"✅ EmailService test: {'SUCCESS' if result else 'FAILED'}")
        return result
    except Exception as e:
        print(f"❌ EmailService test FAILED: {e}")
        return False


def test_template_email():
    """Test template-based email"""
    print("\nTesting template email...")

    try:
        context = {
            "user_name": "Test User",
            "login_url": "http://localhost:8000",
        }

        result = EmailService.send_template_email(
            subject="Test Template Email",
            template_name="welcome",
            context=context,
            recipient_list=["test@example.com"],
        )
        print(f"✅ Template email test: {'SUCCESS' if result else 'FAILED'}")
        return result
    except Exception as e:
        print(f"❌ Template email test FAILED: {e}")
        return False


def test_notification_email():
    """Test notification email (if user exists)"""
    print("\nTesting notification email...")

    try:
        # Try to find a test user
        user = User.objects.first()
        if not user:
            print("⚠️ No users found - skipping notification email test")
            return False

        # Create a test notification
        notification = NotificationService.create_notification(
            recipient=user,
            title="Test Notification",
            message="This is a test notification to verify email functionality.",
            notification_type="info",
            category="system",
            send_email=True,
        )

        print(
            f"✅ Notification email test: SUCCESS (notification ID: {notification.id})"
        )
        print(f"   Email sent: {notification.email_sent}")
        return True

    except Exception as e:
        print(f"❌ Notification email test FAILED: {e}")
        return False


def main():
    """Run all email tests"""
    print("=" * 60)
    print("IMS EMAIL FUNCTIONALITY TEST")
    print("=" * 60)

    # Check email configuration
    print("\nCurrent email configuration:")
    print(f"EMAIL_BACKEND: {settings.EMAIL_BACKEND}")
    print(f"EMAIL_HOST: {getattr(settings, 'EMAIL_HOST', 'Not set')}")
    print(f"EMAIL_PORT: {getattr(settings, 'EMAIL_PORT', 'Not set')}")
    print(f"EMAIL_USE_TLS: {getattr(settings, 'EMAIL_USE_TLS', 'Not set')}")
    print(f"EMAIL_HOST_USER: {getattr(settings, 'EMAIL_HOST_USER', 'Not set')}")
    print(f"DEFAULT_FROM_EMAIL: {settings.DEFAULT_FROM_EMAIL}")

    # Run tests
    tests = [
        test_basic_email,
        test_email_service,
        test_template_email,
        test_notification_email,
    ]

    results = []
    for test_func in tests:
        try:
            result = test_func()
            results.append(result)
        except Exception as e:
            print(f"❌ Test {test_func.__name__} crashed: {e}")
            results.append(False)

    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)

    passed = sum(results)
    total = len(results)

    print(f"Tests passed: {passed}/{total}")

    if "console" in settings.EMAIL_BACKEND.lower():
        print(
            "\n📧 NOTE: Using console email backend - emails will appear in Django logs, not be delivered."
        )
    elif not getattr(settings, "EMAIL_HOST_USER", ""):
        print(
            "\n⚠️ WARNING: No EMAIL_HOST_USER configured - emails may not be delivered."
        )

    print("\nIf emails are not working:")
    print("1. Check Django logs for email output (if using console backend)")
    print("2. Verify SMTP credentials are correct")
    print("3. Check firewall/network connectivity to email server")
    print("4. Ensure recipient email addresses are valid")


if __name__ == "__main__":
    main()
