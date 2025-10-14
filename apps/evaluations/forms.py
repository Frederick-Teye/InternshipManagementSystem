from __future__ import annotations

from django import forms
from django.core.validators import MaxValueValidator, MinValueValidator

from apps.evaluations.models import PerformanceAssessment


class SupervisorAssessmentForm(forms.ModelForm):
    """Form for supervisor to assess an intern"""

    supervisor_score = forms.IntegerField(
        label="Score (out of 100)",
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        widget=forms.NumberInput(
            attrs={
                "class": "form-control form-control-lg",
                "placeholder": "Enter score (0-100)",
                "min": "0",
                "max": "100",
            }
        ),
        required=True,
    )

    supervisor_note = forms.CharField(
        label="Assessment Notes",
        widget=forms.Textarea(
            attrs={
                "class": "form-control",
                "rows": 5,
                "placeholder": "Provide detailed feedback on the intern's performance, strengths, areas for improvement, and overall observations...",
            }
        ),
        required=True,
    )

    acknowledgement_note = forms.CharField(
        label="Acknowledgement Note (Optional)",
        widget=forms.Textarea(
            attrs={
                "class": "form-control",
                "rows": 2,
                "placeholder": "Any closing remarks or additional comments...",
            }
        ),
        required=False,
    )

    class Meta:
        model = PerformanceAssessment
        fields = ["supervisor_score", "supervisor_note", "acknowledgement_note"]

    def save(self, commit=True):
        assessment = super().save(commit=False)
        assessment.status = PerformanceAssessment.Status.REVIEWED
        if commit:
            assessment.save()
        return assessment


class InternSelfAssessmentForm(forms.ModelForm):
    """Form for intern to do self-assessment"""

    intern_score = forms.IntegerField(
        label="Self-Assessment Score (out of 100)",
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        widget=forms.NumberInput(
            attrs={
                "class": "form-control form-control-lg",
                "placeholder": "Rate yourself (0-100)",
                "min": "0",
                "max": "100",
            }
        ),
        required=True,
    )

    intern_note = forms.CharField(
        label="Self-Reflection",
        widget=forms.Textarea(
            attrs={
                "class": "form-control",
                "rows": 5,
                "placeholder": "Reflect on your performance this week. What went well? What challenges did you face? What did you learn? What would you like to improve?",
            }
        ),
        required=True,
    )

    class Meta:
        model = PerformanceAssessment
        fields = ["intern_score", "intern_note"]

    def save(self, commit=True):
        assessment = super().save(commit=False)
        if assessment.status == PerformanceAssessment.Status.DRAFT:
            assessment.status = PerformanceAssessment.Status.SUBMITTED
        if commit:
            assessment.save()
        return assessment


class CreateAssessmentForm(forms.ModelForm):
    """Form to create a new assessment period"""

    week_number = forms.IntegerField(
        label="Week Number",
        validators=[MinValueValidator(1)],
        widget=forms.NumberInput(
            attrs={
                "class": "form-control",
                "placeholder": "Enter week number",
                "min": "1",
            }
        ),
        required=True,
    )

    period_start = forms.DateField(
        label="Period Start Date",
        widget=forms.DateInput(
            attrs={
                "class": "form-control",
                "type": "date",
            }
        ),
        required=False,
    )

    period_end = forms.DateField(
        label="Period End Date",
        widget=forms.DateInput(
            attrs={
                "class": "form-control",
                "type": "date",
            }
        ),
        required=False,
    )

    class Meta:
        model = PerformanceAssessment
        fields = ["week_number", "period_start", "period_end"]
