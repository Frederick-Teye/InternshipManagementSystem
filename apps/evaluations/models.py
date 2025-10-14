from __future__ import annotations

from django.db import models
from django.utils import timezone


class PerformanceAssessment(models.Model):
    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        SUBMITTED = "submitted", "Submitted"
        REVIEWED = "reviewed", "Reviewed"

    intern = models.ForeignKey(
        "interns.InternProfile",
        on_delete=models.CASCADE,
        related_name="assessments",
    )
    assessed_by = models.ForeignKey(
        "supervisors.EmployeeProfile",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="performed_assessments",
    )
    assessment_date = models.DateField(default=timezone.localdate)
    period_start = models.DateField(null=True, blank=True)
    period_end = models.DateField(null=True, blank=True)
    week_number = models.PositiveIntegerField(help_text="Week number within the internship schedule.")
    status = models.CharField(max_length=32, choices=Status.choices, default=Status.DRAFT)

    supervisor_score = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Supervisor score out of 100.",
    )
    supervisor_note = models.TextField(blank=True)

    intern_score = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Intern self-assessment score out of 100.",
    )
    intern_note = models.TextField(
        blank=True,
        help_text="Intern self-assessment reflection shared with the supervisor.",
    )
    acknowledgement_note = models.TextField(
        blank=True,
        help_text="Optional closing remarks recorded upon completion of assessment.",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-assessment_date", "intern__user__last_name"]
        unique_together = ("intern", "week_number")

    def __str__(self) -> str:
        return f"Assessment for {self.intern.user.get_full_name()} - Week {self.week_number}"

    @property
    def is_completed(self) -> bool:
        return self.status == self.Status.REVIEWED and self.supervisor_score is not None
