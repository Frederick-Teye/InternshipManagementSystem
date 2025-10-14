from __future__ import annotations

from django.db import models


class Holiday(models.Model):
    branch = models.ForeignKey(
        "branches.Branch",
        on_delete=models.CASCADE,
        related_name="holidays",
        null=True,
        blank=True,
        help_text="When blank, holiday applies to all branches.",
    )
    name = models.CharField(max_length=255)
    date = models.DateField()
    is_full_day = models.BooleanField(default=True)
    description = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["date", "name"]
        unique_together = ("branch", "date", "name")

    def __str__(self) -> str:
        scope = self.branch.name if self.branch else "All branches"
        return f"{self.name} ({scope}) on {self.date:%Y-%m-%d}"
