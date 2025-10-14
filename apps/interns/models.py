from __future__ import annotations

from django.conf import settings
from django.db import models
from django.utils import timezone


class InternProfile(models.Model):
    class InternType(models.TextChoices):
        CLINICAL = "clinical", "Clinical"
        NURSING = "nursing", "Nursing"
        PHARMACY = "pharmacy", "Pharmacy"
        LABORATORY = "laboratory", "Laboratory"
        ADMINISTRATIVE = "administrative", "Administrative"
        OTHER = "other", "Other"

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    school = models.ForeignKey("schools.School", on_delete=models.SET_NULL, null=True, blank=True)
    academic_supervisor = models.ForeignKey(
        "schools.AcademicSupervisor",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="Academic supervisor associated with the intern's school.",
    )
    branch = models.ForeignKey("branches.Branch", on_delete=models.SET_NULL, null=True, blank=True)
    internal_supervisor = models.ForeignKey(
        "supervisors.EmployeeProfile",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assigned_interns",
    )
    intern_type = models.CharField(max_length=32, choices=InternType.choices, default=InternType.CLINICAL)
    profile_picture = models.ImageField(upload_to="interns/profile_photos/", blank=True, null=True)
    application_letter = models.FileField(upload_to="interns/application_letters/", blank=True, null=True)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    emergency_contact_name = models.CharField(max_length=128, blank=True)
    emergency_contact_phone = models.CharField(max_length=32, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["user__last_name", "user__first_name"]
        verbose_name = "Intern Profile"
        verbose_name_plural = "Intern Profiles"

    def __str__(self) -> str:
        return f"InternProfile({self.user.get_full_name()})"

    @property
    def is_active(self) -> bool:
        today = timezone.localdate()
        if self.start_date and self.end_date:
            return self.start_date <= today <= self.end_date
        if self.start_date and not self.end_date:
            return self.start_date <= today
        if self.end_date and not self.start_date:
            return today <= self.end_date
        return True
