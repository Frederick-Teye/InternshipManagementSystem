"""
Forms for intern management
"""

from __future__ import annotations

from django import forms

from apps.interns.models import InternProfile


class EmergencyContactForm(forms.ModelForm):
    """Form for managing emergency contact information"""

    class Meta:
        model = InternProfile
        fields = ["emergency_contact_name", "emergency_contact_phone"]
        widgets = {
            "emergency_contact_name": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter emergency contact full name",
                }
            ),
            "emergency_contact_phone": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter emergency contact phone number",
                    "type": "tel",
                }
            ),
        }
        labels = {
            "emergency_contact_name": "Emergency Contact Name",
            "emergency_contact_phone": "Emergency Contact Phone",
        }

    def clean_emergency_contact_phone(self):
        """Validate phone number format"""
        phone = self.cleaned_data.get("emergency_contact_phone", "").strip()

        if phone:
            # Remove any non-digit characters except + and spaces
            cleaned_phone = "".join(c for c in phone if c.isdigit() or c in "+ ")

            # Basic validation - should start with + or digit and be reasonable length
            if not (cleaned_phone.startswith("+") or cleaned_phone[0].isdigit()):
                raise forms.ValidationError(
                    "Phone number must start with a digit or '+'."
                )

            if len(cleaned_phone.replace(" ", "").replace("+", "")) < 7:
                raise forms.ValidationError("Phone number seems too short.")

            if len(cleaned_phone.replace(" ", "").replace("+", "")) > 15:
                raise forms.ValidationError("Phone number seems too long.")

        return phone


class InternProfileForm(forms.ModelForm):
    """Form for editing intern profile information including emergency contacts"""

    class Meta:
        model = InternProfile
        fields = [
            "emergency_contact_name",
            "emergency_contact_phone",
            "school",
            "branch",
            "internal_supervisor",
            "academic_supervisor",
            "start_date",
            "end_date",
        ]
        widgets = {
            "emergency_contact_name": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter emergency contact full name",
                }
            ),
            "emergency_contact_phone": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter emergency contact phone number",
                    "type": "tel",
                }
            ),
            "school": forms.Select(attrs={"class": "form-control"}),
            "branch": forms.Select(attrs={"class": "form-control"}),
            "internal_supervisor": forms.Select(attrs={"class": "form-control"}),
            "academic_supervisor": forms.Select(attrs={"class": "form-control"}),
            "start_date": forms.DateInput(
                attrs={"class": "form-control", "type": "date"}
            ),
            "end_date": forms.DateInput(
                attrs={"class": "form-control", "type": "date"}
            ),
        }
        labels = {
            "emergency_contact_name": "Emergency Contact Name",
            "emergency_contact_phone": "Emergency Contact Phone",
            "school": "School/University",
            "branch": "Branch/Department",
            "internal_supervisor": "Internal Supervisor",
            "academic_supervisor": "Academic Supervisor",
            "start_date": "Internship Start Date",
            "end_date": "Internship End Date",
        }
