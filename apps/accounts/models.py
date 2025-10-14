from __future__ import annotations

import uuid
from datetime import timedelta

from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.core.mail import send_mail
from django.db import models
from django.utils import timezone


class User(AbstractUser):
    class Roles(models.TextChoices):
        INTERN = "intern", "Intern"
        EMPLOYEE = "employee", "Employee"
        SUPERVISOR = "supervisor", "Supervisor"
        MANAGER = "manager", "Manager"
        ADMIN = "admin", "Administrator"

    email = models.EmailField(unique=True)
    role = models.CharField(
        max_length=32,
        choices=Roles.choices,
        default=Roles.INTERN,
        help_text="Determines the default permissions and dashboard experience.",
    )
    is_onboarded = models.BooleanField(default=False)
    onboarding_token = models.UUIDField(null=True, blank=True, editable=False)
    onboarding_token_expires_at = models.DateTimeField(null=True, blank=True)

    REQUIRED_FIELDS = ["email"]

    def __str__(self) -> str:
        return f"{self.get_full_name()} ({self.get_role_display()})"

    def generate_onboarding_token(self, *, ttl_hours: int = 24) -> uuid.UUID:
        self.onboarding_token = uuid.uuid4()
        self.onboarding_token_expires_at = timezone.now() + timedelta(hours=ttl_hours)
        self.save(update_fields=["onboarding_token", "onboarding_token_expires_at"])
        return self.onboarding_token

    def clear_onboarding_token(self) -> None:
        self.onboarding_token = None
        self.onboarding_token_expires_at = None
        self.save(update_fields=["onboarding_token", "onboarding_token_expires_at"])

    @property
    def onboarding_link_is_valid(self) -> bool:
        if not self.onboarding_token:
            return False
        if not self.onboarding_token_expires_at:
            return False
        return timezone.now() <= self.onboarding_token_expires_at

    def email_user(self, subject: str, message: str, from_email: str | None = None) -> None:
        send_mail(subject, message, from_email, [self.email])


class OnboardingInvitation(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    token = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    expires_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    used = models.BooleanField(default=False)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Onboarding Invitation"
        verbose_name_plural = "Onboarding Invitations"

    def mark_used(self) -> None:
        self.used = True
        self.save(update_fields=["used"])

    @property
    def is_valid(self) -> bool:
        return not self.used and timezone.now() <= self.expires_at

    def __str__(self) -> str:
        return f"Invitation for {self.user.email} (expires {self.expires_at:%Y-%m-%d %H:%M})"
