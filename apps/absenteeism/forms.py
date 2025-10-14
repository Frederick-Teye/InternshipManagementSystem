from __future__ import annotations

from django import forms
from django.core.exceptions import ValidationError

from apps.absenteeism.models import AbsenteeismRequest


class AbsenteeismRequestForm(forms.ModelForm):
    """Form for intern to submit absenteeism request"""

    reason = forms.CharField(
        label="Reason for Absence",
        widget=forms.Textarea(
            attrs={
                "class": "form-control",
                "rows": 4,
                "placeholder": "Please provide a detailed reason for your absence request...",
            }
        ),
        required=True,
    )

    start_date = forms.DateField(
        label="Start Date",
        widget=forms.DateInput(
            attrs={
                "class": "form-control",
                "type": "date",
            }
        ),
        required=True,
    )

    end_date = forms.DateField(
        label="End Date",
        widget=forms.DateInput(
            attrs={
                "class": "form-control",
                "type": "date",
            }
        ),
        required=True,
    )

    supporting_document = forms.FileField(
        label="Supporting Document (Optional)",
        widget=forms.FileInput(
            attrs={
                "class": "form-control",
                "accept": ".pdf,.doc,.docx,.jpg,.jpeg,.png",
            }
        ),
        required=False,
        help_text="Upload medical certificate, official document, etc. (PDF, DOC, DOCX, JPG, PNG)",
    )

    class Meta:
        model = AbsenteeismRequest
        fields = ["start_date", "end_date", "reason", "supporting_document"]

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get("start_date")
        end_date = cleaned_data.get("end_date")

        if start_date and end_date:
            if end_date < start_date:
                raise ValidationError("End date must be on or after the start date.")

        return cleaned_data


class AbsenteeismApprovalForm(forms.Form):
    """Form for supervisor/manager to approve or reject absenteeism request"""

    DECISION_CHOICES = [
        ("approve", "Approve"),
        ("reject", "Reject"),
    ]

    decision = forms.ChoiceField(
        label="Decision",
        choices=DECISION_CHOICES,
        widget=forms.RadioSelect(
            attrs={
                "class": "form-check-input",
            }
        ),
        required=True,
    )

    decision_note = forms.CharField(
        label="Note",
        widget=forms.Textarea(
            attrs={
                "class": "form-control",
                "rows": 3,
                "placeholder": "Provide a note explaining your decision (required for rejection)...",
            }
        ),
        required=False,
    )

    def clean(self):
        cleaned_data = super().clean()
        decision = cleaned_data.get("decision")
        decision_note = cleaned_data.get("decision_note")

        if decision == "reject" and not decision_note:
            raise ValidationError("A note is required when rejecting a request.")

        return cleaned_data
