from __future__ import annotations

from django.conf import settings
from django.db import models


class EmployeeProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    job_title = models.CharField(max_length=128, blank=True)
    phone_number = models.CharField(max_length=32, blank=True)
    department = models.CharField(max_length=128, blank=True)
    bio = models.TextField(blank=True)
    is_clinical_supervisor = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Employee Profile"
        verbose_name_plural = "Employee Profiles"

    def __str__(self) -> str:
        return f"{self.user.get_full_name()} ({self.job_title or 'Employee'})"

    @property
    def role(self) -> str:
        return self.user.role
