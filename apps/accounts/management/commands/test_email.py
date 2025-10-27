from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from django.conf import settings


class Command(BaseCommand):
    help = "Test email configuration by sending a test email"

    def add_arguments(self, parser):
        parser.add_argument(
            "--to",
            type=str,
            help="Email address to send test email to",
            default="test@example.com",
        )

    def handle(self, *args, **options):
        recipient = options["to"]

        subject = "Test Email from Internship Management System"
        message = f"""
Hello!

This is a test email from your Internship Management System.

Email Configuration Details:
- Backend: {settings.EMAIL_BACKEND}
- Host: {settings.EMAIL_HOST}
- Port: {settings.EMAIL_PORT}
- TLS: {settings.EMAIL_USE_TLS}
- From: {settings.DEFAULT_FROM_EMAIL}

If you received this email, your email configuration is working correctly!

Best regards,
Internship Management System
        """

        try:
            send_mail(
                subject=subject,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[recipient],
                fail_silently=False,
            )
            self.stdout.write(
                self.style.SUCCESS(f"Successfully sent test email to {recipient}")
            )
        except Exception as e:
            self.stderr.write(self.style.ERROR(f"Failed to send email: {str(e)}"))
            self.stderr.write(
                self.style.WARNING(
                    "Make sure your email credentials are configured correctly in docker-compose.yml"
                )
            )
