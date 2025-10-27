from __future__ import annotations

from django import forms
from django.utils import timezone

from apps.attendance.models import Attendance
from apps.interns.models import InternProfile


class AttendanceMarkForm(forms.ModelForm):
    """Form for marking attendance with GPS coordinates"""

    latitude = forms.DecimalField(
        max_digits=12,
        decimal_places=9,
        widget=forms.HiddenInput(),
        required=True,
    )
    longitude = forms.DecimalField(
        max_digits=10,
        decimal_places=7,
        widget=forms.HiddenInput(),
        required=True,
    )
    location_accuracy_m = forms.DecimalField(
        max_digits=10,
        decimal_places=7,
        widget=forms.HiddenInput(),
        required=False,
    )
    notes = forms.CharField(
        widget=forms.Textarea(
            attrs={
                "class": "form-control",
                "rows": 3,
                "placeholder": "Add any notes about your attendance (optional)",
            }
        ),
        required=False,
    )

    class Meta:
        model = Attendance
        fields = ["latitude", "longitude", "location_accuracy_m", "notes"]

    def __init__(self, *args, intern_profile=None, **kwargs):
        self.intern_profile = intern_profile
        super().__init__(*args, **kwargs)

    def save(self, commit=True):
        attendance = super().save(commit=False)
        attendance.intern = self.intern_profile
        attendance.branch = self.intern_profile.branch
        attendance.check_in_time = timezone.now()
        attendance.recorded_by = self.intern_profile.user

        # Auto-validate based on proximity
        attendance.auto_validate()

        if commit:
            attendance.save()
        return attendance


class AttendanceApprovalForm(forms.Form):
    """Form for supervisor to approve/reject attendance"""

    action = forms.ChoiceField(
        choices=[
            ("approve", "Approve"),
            ("reject", "Reject"),
        ],
        widget=forms.RadioSelect(attrs={"class": "form-check-input"}),
        required=True,
    )
    note = forms.CharField(
        widget=forms.Textarea(
            attrs={
                "class": "form-control",
                "rows": 3,
                "placeholder": "Add a note (required for rejection)",
            }
        ),
        required=False,
    )

    def clean(self):
        cleaned_data = super().clean()
        action = cleaned_data.get("action")
        note = cleaned_data.get("note")

        if action == "reject" and not note:
            raise forms.ValidationError("A note is required when rejecting attendance.")

        return cleaned_data


class CheckOutForm(forms.Form):
    """Simple form for checkout"""

    notes = forms.CharField(
        widget=forms.Textarea(
            attrs={
                "class": "form-control",
                "rows": 2,
                "placeholder": "Add checkout notes (optional)",
            }
        ),
        required=False,
    )
