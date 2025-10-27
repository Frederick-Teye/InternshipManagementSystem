from __future__ import annotations

from django.urls import path

from apps.accounts.views import (
    CustomPasswordResetCompleteView,
    CustomPasswordResetConfirmView,
    CustomPasswordResetDoneView,
    CustomPasswordResetView,
    LoginView,
    OnboardingView,
    dashboard_view,
    logout_view,
    profile_view,
    change_password_view,
    test_email_view,
)

app_name = "accounts"

urlpatterns = [
    path("login/", LoginView.as_view(), name="login"),
    path("logout/", logout_view, name="logout"),
    path("onboarding/<uuid:token>/", OnboardingView.as_view(), name="onboarding"),
    path("dashboard/", dashboard_view, name="dashboard"),
    # Profile management
    path("profile/", profile_view, name="profile"),
    path("change-password/", change_password_view, name="change_password"),
    path("test-email/", test_email_view, name="test_email"),
    # Password reset
    path("password-reset/", CustomPasswordResetView.as_view(), name="password_reset"),
    path(
        "password-reset/done/",
        CustomPasswordResetDoneView.as_view(),
        name="password_reset_done",
    ),
    path(
        "password-reset/<uidb64>/<token>/",
        CustomPasswordResetConfirmView.as_view(),
        name="password_reset_confirm",
    ),
    path(
        "password-reset/complete/",
        CustomPasswordResetCompleteView.as_view(),
        name="password_reset_complete",
    ),
]
