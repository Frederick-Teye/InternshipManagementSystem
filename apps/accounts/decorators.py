from __future__ import annotations

from functools import wraps

from django.contrib import messages
from django.http import HttpResponseForbidden
from django.shortcuts import redirect

from apps.accounts.models import User


def role_required(*roles):
    """
    Decorator to restrict access to users with specific roles.

    Usage:
        @role_required(User.Roles.ADMIN, User.Roles.MANAGER)
        def my_view(request):
            ...
    """

    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                messages.warning(request, "Please log in to access this page.")
                return redirect("accounts:login")

            # Superusers have access to everything
            if request.user.is_superuser:
                return view_func(request, *args, **kwargs)

            if request.user.role not in roles:
                messages.error(
                    request, "You don't have permission to access this page."
                )
                return redirect("accounts:dashboard")

            return view_func(request, *args, **kwargs)

        return _wrapped_view

    return decorator


def admin_required(view_func):
    """Decorator to restrict access to admin users only."""
    return role_required(User.Roles.ADMIN)(view_func)


def manager_required(view_func):
    """Decorator to restrict access to manager users only."""
    return role_required(User.Roles.MANAGER)(view_func)


def supervisor_required(view_func):
    """Decorator to restrict access to supervisor users only."""
    return role_required(User.Roles.SUPERVISOR)(view_func)


def employee_required(view_func):
    """Decorator to restrict access to employee users only."""
    return role_required(User.Roles.EMPLOYEE)(view_func)


def intern_required(view_func):
    """Decorator to restrict access to intern users only."""
    return role_required(User.Roles.INTERN)(view_func)


def supervisor_or_above(view_func):
    """Decorator to restrict access to supervisors, managers, and admins."""
    return role_required(User.Roles.SUPERVISOR, User.Roles.MANAGER, User.Roles.ADMIN)(
        view_func
    )


def manager_or_above(view_func):
    """Decorator to restrict access to managers and admins."""
    return role_required(User.Roles.MANAGER, User.Roles.ADMIN)(view_func)


def onboarding_required(view_func):
    """
    Decorator to ensure user has completed onboarding.

    Redirects to onboarding page if not completed.
    """

    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.warning(request, "Please log in to access this page.")
            return redirect("accounts:login")

        if not request.user.is_onboarded:
            messages.info(request, "Please complete your account setup first.")
            if request.user.onboarding_token:
                return redirect(
                    "accounts:onboarding", token=request.user.onboarding_token
                )
            else:
                messages.error(
                    request,
                    "Your account setup is incomplete. Please contact an administrator.",
                )
                return redirect("accounts:login")

        return view_func(request, *args, **kwargs)

    return _wrapped_view
