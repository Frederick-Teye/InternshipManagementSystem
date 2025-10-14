"""
Forms for user account management
"""

from __future__ import annotations

from django import forms
from django.contrib.auth.forms import PasswordChangeForm
from apps.accounts.models import User


class UserProfileForm(forms.ModelForm):
    """Form for users to edit their profile information"""

    class Meta:
        model = User
        fields = ["first_name", "last_name", "email"]
        widgets = {
            "first_name": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Enter first name"}
            ),
            "last_name": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Enter last name"}
            ),
            "email": forms.EmailInput(
                attrs={"class": "form-control", "placeholder": "Enter email address"}
            ),
        }
        labels = {
            "first_name": "First Name",
            "last_name": "Last Name",
            "email": "Email Address",
        }

    def clean_email(self):
        """Ensure email is unique (excluding current user)"""
        email = self.cleaned_data.get("email")
        if (
            email
            and User.objects.exclude(pk=self.instance.pk).filter(email=email).exists()
        ):
            raise forms.ValidationError("This email address is already in use.")
        return email


class CustomPasswordChangeForm(PasswordChangeForm):
    """Custom password change form with Bootstrap styling"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["old_password"].widget.attrs.update(
            {"class": "form-control", "placeholder": "Enter current password"}
        )
        self.fields["new_password1"].widget.attrs.update(
            {"class": "form-control", "placeholder": "Enter new password"}
        )
        self.fields["new_password2"].widget.attrs.update(
            {"class": "form-control", "placeholder": "Confirm new password"}
        )

        # Update labels
        self.fields["old_password"].label = "Current Password"
        self.fields["new_password1"].label = "New Password"
        self.fields["new_password2"].label = "Confirm New Password"
