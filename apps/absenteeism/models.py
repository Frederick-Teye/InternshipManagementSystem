from __future__ import annotations

from django.db import models
from django.utils import timezone


class AbsenteeismRequest(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        APPROVED = "approved", "Approved"
        REJECTED = "rejected", "Rejected"
        CANCELLED = "cancelled", "Cancelled"

    intern = models.ForeignKey("interns.InternProfile", on_delete=models.CASCADE, related_name="absenteeism_requests")
    approver = models.ForeignKey(
        "accounts.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="absenteeism_approvals",
    )
    status = models.CharField(max_length=32, choices=Status.choices, default=Status.PENDING)
    reason = models.TextField()
    start_date = models.DateField()
    end_date = models.DateField()
    supporting_document = models.FileField(upload_to="absenteeism/supporting_documents/", blank=True, null=True)
    submitted_at = models.DateTimeField(auto_now_add=True)
    decision_at = models.DateTimeField(null=True, blank=True)
    decision_note = models.TextField(blank=True)

    class Meta:
        ordering = ["-submitted_at"]

    def __str__(self) -> str:
        return f"AbsenteeismRequest({self.intern.user.get_full_name()} {self.start_date:%Y-%m-%d}→{self.end_date:%Y-%m-%d})"

    def approve(self, approver, note: str | None = None) -> None:
        self.status = self.Status.APPROVED
        self.approver = approver
        self.decision_at = timezone.now()
        self.decision_note = note or ""

    def reject(self, approver, note: str | None = None) -> None:
        self.status = self.Status.REJECTED
        self.approver = approver
        self.decision_at = timezone.now()
        self.decision_note = note or ""

    def cancel(self) -> None:
        self.status = self.Status.CANCELLED
        self.decision_at = timezone.now()
