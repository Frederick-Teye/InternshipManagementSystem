from __future__ import annotations

from django.db import models


class Branch(models.Model):
    name = models.CharField(max_length=255, unique=True)
    code = models.CharField(max_length=32, unique=True)
    address_line1 = models.CharField(max_length=255, blank=True)
    address_line2 = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=128, blank=True)
    state = models.CharField(max_length=128, blank=True)
    country = models.CharField(max_length=128, blank=True)
    latitude = models.DecimalField(
        max_digits=12, decimal_places=9, null=True, blank=True
    )
    longitude = models.DecimalField(
        max_digits=12, decimal_places=9, null=True, blank=True
    )
    proximity_threshold_meters = models.PositiveIntegerField(
        default=150,
        help_text="Maximum distance from branch location to auto-approve attendance.",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]

    def __str__(self) -> str:
        return f"{self.name} ({self.code})"


class BranchEmployeeAssignment(models.Model):
    class AssignmentRole(models.TextChoices):
        SUPERVISOR = "supervisor", "Supervisor"
        MANAGER = "manager", "Manager"
        COORDINATOR = "coordinator", "Coordinator"

    branch = models.ForeignKey(
        Branch, on_delete=models.CASCADE, related_name="assignments"
    )
    employee = models.ForeignKey(
        "supervisors.EmployeeProfile",
        on_delete=models.CASCADE,
        related_name="branch_assignments",
    )
    role = models.CharField(max_length=32, choices=AssignmentRole.choices)
    is_primary = models.BooleanField(default=False)
    assigned_at = models.DateTimeField(auto_now_add=True)
    active = models.BooleanField(default=True)

    class Meta:
        unique_together = ("branch", "employee", "role")
        verbose_name = "Branch Employee Assignment"
        verbose_name_plural = "Branch Employee Assignments"

    def __str__(self) -> str:
        return f"{self.employee} → {self.branch} ({self.get_role_display()})"
