"""
Tests for notification system including email functionality.
"""

from django.test import TestCase, override_settings
from django.contrib.auth import get_user_model
from django.core import mail
from unittest.mock import patch, MagicMock

from apps.notifications.models import Notification, NotificationPreference
from apps.notifications.services import NotificationService
from apps.accounts.services import EmailService

User = get_user_model()


class NotificationModelTest(TestCase):
    """Test Notification model"""

    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )

    def test_notification_creation(self):
        """Test creating a notification"""
        notification = Notification.objects.create(
            recipient=self.user,
            title="Test Notification",
            message="This is a test message",
            notification_type="info",
            category="general",
        )

        self.assertEqual(notification.recipient, self.user)
        self.assertEqual(notification.title, "Test Notification")
        self.assertEqual(notification.message, "This is a test message")
        self.assertEqual(notification.notification_type, "info")
        self.assertEqual(notification.category, "general")
        self.assertFalse(notification.is_read)
        self.assertFalse(notification.email_sent)

    def test_mark_as_read(self):
        """Test marking notification as read"""
        notification = Notification.objects.create(
            recipient=self.user, title="Test", message="Test"
        )

        self.assertFalse(notification.is_read)
        self.assertIsNone(notification.read_at)

        notification.mark_as_read()

        self.assertTrue(notification.is_read)
        self.assertIsNotNone(notification.read_at)

    def test_notification_str_method(self):
        """Test string representation"""
        notification = Notification.objects.create(
            recipient=self.user, title="Test Notification", message="Test"
        )

        expected = f"Test Notification - {self.user.get_full_name()}"
        self.assertEqual(str(notification), expected)


class NotificationPreferenceTest(TestCase):
    """Test NotificationPreference model"""

    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )

    def test_preference_creation(self):
        """Test creating notification preferences"""
        prefs = NotificationPreference.objects.create(user=self.user)

        # Check default values
        self.assertTrue(prefs.email_on_attendance_approval)
        self.assertTrue(prefs.email_on_assessment_created)
        self.assertTrue(prefs.email_on_assessment_reviewed)
        self.assertTrue(prefs.email_on_absence_status)
        self.assertTrue(prefs.email_on_onboarding)
        self.assertTrue(prefs.in_app_notifications)
        self.assertFalse(prefs.daily_digest)
        self.assertFalse(prefs.weekly_digest)

    def test_preference_str_method(self):
        """Test string representation"""
        prefs = NotificationPreference.objects.create(user=self.user)
        expected = f"Notification Preferences for {self.user.get_full_name()}"
        self.assertEqual(str(prefs), expected)


@override_settings(EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend")
class EmailServiceTest(TestCase):
    """Test EmailService functionality"""

    def setUp(self):
        # Clear any existing emails
        mail.outbox = []

    def test_send_email(self):
        """Test basic email sending"""
        result = EmailService.send_email(
            subject="Test Email",
            message="Test message",
            recipient_list=["test@example.com"],
        )

        self.assertTrue(result)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, "Test Email")
        self.assertEqual(mail.outbox[0].body, "Test message")
        self.assertEqual(mail.outbox[0].to, ["test@example.com"])

    def test_send_email_empty_recipients(self):
        """Test sending email with empty recipient list"""
        result = EmailService.send_email(
            subject="Test", message="Test", recipient_list=[]
        )

        self.assertFalse(result)
        self.assertEqual(len(mail.outbox), 0)

    def test_send_template_email(self):
        """Test template-based email sending"""
        context = {"user_name": "Test User", "login_url": "http://localhost:8000"}

        result = EmailService.send_template_email(
            subject="Welcome",
            template_name="welcome",
            context=context,
            recipient_list=["test@example.com"],
        )

        self.assertTrue(result)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, "Welcome")

    def test_send_notification_email_direct(self):
        """Test direct notification email sending"""
        with patch("django.core.mail.send_mail", return_value=True):
            result = EmailService.send_notification_email_direct(
                subject="Test Direct Email",
                template_name="notifications/email/notification_email.html",
                context={"message": "Test message"},
                recipient_list=["test@example.com"],
            )
            self.assertTrue(result)


@override_settings(EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend")
class NotificationServiceTest(TestCase):
    """Test NotificationService functionality"""

    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )
        # Clear any existing emails
        mail.outbox = []

    def test_create_notification_without_email(self):
        """Test creating notification without email"""
        notification = NotificationService.create_notification(
            recipient=self.user,
            title="Test Notification",
            message="Test message",
            send_email=False,
        )

        self.assertIsInstance(notification, Notification)
        self.assertEqual(notification.recipient, self.user)
        self.assertEqual(notification.title, "Test Notification")
        self.assertFalse(notification.email_sent)
        self.assertEqual(len(mail.outbox), 0)

    def test_create_notification_with_email_enabled(self):
        """Test creating notification with email when user has preferences enabled"""
        # Create preferences with email enabled
        NotificationPreference.objects.create(
            user=self.user, email_on_attendance_approval=True, in_app_notifications=True
        )

        notification = NotificationService.create_notification(
            recipient=self.user,
            title="Test Notification",
            message="Test message",
            category="attendance",
            send_email=True,
        )

        self.assertIsInstance(notification, Notification)
        self.assertTrue(notification.email_sent)
        self.assertIsNotNone(notification.email_sent_at)
        self.assertEqual(len(mail.outbox), 1)

    def test_create_notification_with_email_disabled_preference(self):
        """Test creating notification when user has email disabled for category"""
        # Create preferences with email disabled for attendance
        NotificationPreference.objects.create(
            user=self.user,
            email_on_attendance_approval=False,
            in_app_notifications=True,
        )

        notification = NotificationService.create_notification(
            recipient=self.user,
            title="Test Notification",
            message="Test message",
            category="attendance",
            send_email=True,
        )

        self.assertIsInstance(notification, Notification)
        self.assertFalse(notification.email_sent)
        self.assertEqual(len(mail.outbox), 0)

    def test_should_send_email_logic(self):
        """Test the _should_send_email logic"""
        # Create preferences
        prefs = NotificationPreference.objects.create(
            user=self.user,
            email_on_attendance_approval=True,
            email_on_absence_status=False,
            in_app_notifications=False,  # This should NOT affect email sending
        )

        # Create test notifications
        attendance_notification = Notification(
            recipient=self.user, title="Attendance Test", category="attendance"
        )

        absence_notification = Notification(
            recipient=self.user, title="Absence Test", category="absenteeism"
        )

        # Test attendance should send (enabled)
        should_send_attendance = NotificationService._should_send_email(
            attendance_notification, prefs
        )
        self.assertTrue(should_send_attendance)

        # Test absence should not send (disabled)
        should_send_absence = NotificationService._should_send_email(
            absence_notification, prefs
        )
        self.assertFalse(should_send_absence)

    def test_bulk_notification_creation(self):
        """Test creating notifications for multiple users"""
        user2 = User.objects.create_user(
            username="testuser2", email="test2@example.com", password="testpass123"
        )

        # Enable email for both users
        for user in [self.user, user2]:
            NotificationPreference.objects.create(
                user=user, email_on_assessment_created=True
            )

        notifications = NotificationService.create_bulk_notifications(
            recipients=[self.user, user2],
            title="Bulk Test",
            message="Bulk message",
            category="assessment",
            send_email=True,
        )

        self.assertEqual(len(notifications), 2)
        self.assertEqual(len(mail.outbox), 2)

        for notification in notifications:
            self.assertTrue(notification.email_sent)

    def test_get_unread_count(self):
        """Test getting unread notification count"""
        # Create some notifications
        for i in range(3):
            Notification.objects.create(
                recipient=self.user, title=f"Test {i}", message="Test"
            )

        # Mark one as read
        notification = Notification.objects.first()
        notification.mark_as_read()

        unread_count = NotificationService.get_unread_count(self.user)
        self.assertEqual(unread_count, 2)

    def test_mark_all_as_read(self):
        """Test marking all notifications as read"""
        # Create some notifications
        for i in range(3):
            Notification.objects.create(
                recipient=self.user, title=f"Test {i}", message="Test"
            )

        # Initially all unread
        unread_count = NotificationService.get_unread_count(self.user)
        self.assertEqual(unread_count, 3)

        # Mark all as read
        marked_count = NotificationService.mark_all_as_read(self.user)
        self.assertEqual(marked_count, 3)

        # Check all are now read
        unread_count = NotificationService.get_unread_count(self.user)
        self.assertEqual(unread_count, 0)

    @patch("apps.accounts.services.EmailService.send_notification_email_direct")
    def test_email_sending_error_handling(self, mock_send):
        """Test email sending error handling"""
        # Mock email service to raise exception
        mock_send.side_effect = Exception("Email service error")

        # Create preferences with email enabled
        NotificationPreference.objects.create(
            user=self.user, email_on_attendance_approval=True
        )

        # Should not raise exception, but email_sent should be False
        notification = NotificationService.create_notification(
            recipient=self.user,
            title="Test",
            message="Test",
            category="attendance",
            send_email=True,
        )

        self.assertFalse(notification.email_sent)
        self.assertIsNone(notification.email_sent_at)
