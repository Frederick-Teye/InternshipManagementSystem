from __future__ import annotations

import math

from django.db import models
from django.utils import timezone


def haversine_distance_meters(
    lat1: float, lon1: float, lat2: float, lon2: float
) -> float:
    """Return distance in meters between two geographic points."""

    radius = 6371000  # Earth radius in meters
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    a = (
        math.sin(delta_phi / 2) ** 2
        + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2) ** 2
    )
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return radius * c


class Attendance(models.Model):
    class ApprovalStatus(models.TextChoices):
        PENDING = "pending", "Pending"
        APPROVED = "approved", "Approved"
        REJECTED = "rejected", "Rejected"

    intern = models.ForeignKey(
        "interns.InternProfile", on_delete=models.CASCADE, related_name="attendances"
    )
    branch = models.ForeignKey(
        "branches.Branch", on_delete=models.CASCADE, related_name="attendances"
    )
    check_in_time = models.DateTimeField(default=timezone.now)
    check_out_time = models.DateTimeField(null=True, blank=True)
    latitude = models.DecimalField(max_digits=12, decimal_places=9)
    longitude = models.DecimalField(max_digits=12, decimal_places=9)
    location_accuracy_m = models.DecimalField(
        max_digits=12, decimal_places=9, null=True, blank=True
    )
    approval_status = models.CharField(
        max_length=32, choices=ApprovalStatus.choices, default=ApprovalStatus.PENDING
    )
    auto_approved = models.BooleanField(default=False)
    notes = models.TextField(blank=True)
    recorded_by = models.ForeignKey(
        "accounts.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="recorded_attendance_entries",
    )
    approved_by = models.ForeignKey(
        "accounts.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="approved_attendance_entries",
    )
    approved_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-check_in_time"]
        verbose_name_plural = "Attendance Records"

    def __str__(self) -> str:
        return f"Attendance({self.intern.user.get_full_name()} @ {self.branch.name} on {self.check_in_time:%Y-%m-%d})"

    def distance_from_branch(self) -> float | None:
        if self.branch.latitude is None or self.branch.longitude is None:
            return None
        return haversine_distance_meters(
            float(self.latitude),
            float(self.longitude),
            float(self.branch.latitude),
            float(self.branch.longitude),
        )

    def auto_validate(self) -> None:
        distance = self.distance_from_branch()
        if distance is None:
            return
        if distance <= self.branch.proximity_threshold_meters:
            self.approval_status = self.ApprovalStatus.APPROVED
            self.auto_approved = True
            self.approved_at = timezone.now()

    def approve(self, *, approver) -> None:
        self.approval_status = self.ApprovalStatus.APPROVED
        self.approved_by = approver
        self.approved_at = timezone.now()
        self.auto_approved = False

    def reject(self, *, approver, note: str | None = None) -> None:
        self.approval_status = self.ApprovalStatus.REJECTED
        self.approved_by = approver
        self.approved_at = timezone.now()
        self.auto_approved = False
        if note:
            self.notes = note
