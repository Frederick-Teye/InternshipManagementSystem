from __future__ import annotations

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import (
    PasswordResetView,
    PasswordResetDoneView,
    PasswordResetConfirmView,
    PasswordResetCompleteView,
)
from django.shortcuts import redirect, render
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.debug import sensitive_post_parameters
from django.views.generic import TemplateView

from apps.accounts.models import User


class LoginView(TemplateView):
    template_name = "accounts/login.html"

    @method_decorator(sensitive_post_parameters())
    @method_decorator(csrf_protect)
    @method_decorator(never_cache)
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect("dashboard")
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        username = request.POST.get("username")
        password = request.POST.get("password")

        if not username or not password:
            messages.error(request, "Please provide both username and password.")
            return self.render_to_response(self.get_context_data())

        user = authenticate(request, username=username, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
                messages.success(
                    request, f"Welcome back, {user.get_full_name() or user.username}!"
                )
                return redirect("dashboard")
            else:
                messages.error(
                    request,
                    "Your account is inactive. Please contact an administrator.",
                )
        else:
            messages.error(request, "Invalid username or password.")

        return self.render_to_response(self.get_context_data())


@login_required
def logout_view(request):
    logout(request)
    messages.info(request, "You have been logged out successfully.")
    return redirect("login")


class OnboardingView(TemplateView):
    template_name = "accounts/onboarding.html"

    def get(self, request, token, *args, **kwargs):
        try:
            user = User.objects.get(onboarding_token=token)
        except User.DoesNotExist:
            messages.error(request, "Invalid or expired onboarding link.")
            return redirect("login")

        if not user.onboarding_link_is_valid:
            messages.error(request, "This onboarding link has expired.")
            return redirect("login")

        if user.is_onboarded:
            messages.info(request, "You have already completed onboarding.")
            return redirect("login")

        context = self.get_context_data(user=user)
        return self.render_to_response(context)

    def post(self, request, token, *args, **kwargs):
        try:
            user = User.objects.get(onboarding_token=token)
        except User.DoesNotExist:
            messages.error(request, "Invalid onboarding link.")
            return redirect("login")

        if not user.onboarding_link_is_valid:
            messages.error(request, "This onboarding link has expired.")
            return redirect("login")

        if user.is_onboarded:
            messages.info(request, "You have already completed onboarding.")
            return redirect("login")

        # Process onboarding form
        password1 = request.POST.get("password1")
        password2 = request.POST.get("password2")
        first_name = request.POST.get("first_name", "").strip()
        last_name = request.POST.get("last_name", "").strip()

        if not all([password1, password2, first_name, last_name]):
            messages.error(request, "All fields are required.")
            return self.render_to_response(self.get_context_data(user=user))

        if password1 != password2:
            messages.error(request, "Passwords do not match.")
            return self.render_to_response(self.get_context_data(user=user))

        if len(password1) < 8:
            messages.error(request, "Password must be at least 8 characters long.")
            return self.render_to_response(self.get_context_data(user=user))

        # Update user profile
        user.first_name = first_name
        user.last_name = last_name
        user.set_password(password1)
        user.is_onboarded = True
        user.clear_onboarding_token()
        user.save()

        # Log the user in
        login(request, user)
        messages.success(
            request,
            f"Welcome to the Internship Management System, {user.get_full_name()}!",
        )
        return redirect("dashboard")


@login_required
def dashboard_view(request):
    """Role-based dashboard redirect"""
    user = request.user

    if user.role == User.Roles.ADMIN:
        return redirect("dashboards:admin")
    elif user.role == User.Roles.MANAGER:
        return redirect("dashboards:manager")
    elif user.role == User.Roles.SUPERVISOR:
        return redirect("dashboards:supervisor")
    elif user.role == User.Roles.EMPLOYEE:
        return redirect("dashboards:employee")
    else:  # INTERN
        return redirect("dashboards:intern")


# Custom password reset views with custom templates
class CustomPasswordResetView(PasswordResetView):
    template_name = "accounts/password_reset.html"
    email_template_name = "accounts/password_reset_email.html"
    success_url = reverse_lazy("password_reset_done")


class CustomPasswordResetDoneView(PasswordResetDoneView):
    template_name = "accounts/password_reset_done.html"


class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    template_name = "accounts/password_reset_confirm.html"
    success_url = reverse_lazy("password_reset_complete")


class CustomPasswordResetCompleteView(PasswordResetCompleteView):
    template_name = "accounts/password_reset_complete.html"
