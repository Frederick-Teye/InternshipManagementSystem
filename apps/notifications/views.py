from __future__ import annotations

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.utils import timezone

from apps.notifications.models import Notification, NotificationPreference
from apps.notifications.services import NotificationService


@login_required
def notification_center(request):
    """View all notifications for the logged-in user"""
    notifications = Notification.objects.filter(recipient=request.user).order_by(
        "-created_at"
    )

    # Filter by category if specified
    category = request.GET.get("category")
    if category:
        notifications = notifications.filter(category=category)

    # Filter by read status
    filter_type = request.GET.get("filter", "all")
    if filter_type == "unread":
        notifications = notifications.filter(is_read=False)
    elif filter_type == "read":
        notifications = notifications.filter(is_read=True)

    unread_count = Notification.objects.filter(
        recipient=request.user, is_read=False
    ).count()

    context = {
        "notifications": notifications[:50],  # Limit to 50 most recent
        "unread_count": unread_count,
        "category": category,
        "filter_type": filter_type,
    }

    return render(request, "notifications/notification_center.html", context)


@login_required
def mark_as_read(request, notification_id):
    """Mark a single notification as read"""
    notification = get_object_or_404(
        Notification, id=notification_id, recipient=request.user
    )
    notification.mark_as_read()

    # Redirect to action URL if specified, otherwise back to notification center
    if notification.action_url:
        return redirect(notification.action_url)

    return redirect("notifications:center")


@login_required
def mark_all_as_read(request):
    """Mark all notifications as read for the user"""
    if request.method == "POST":
        count = NotificationService.mark_all_as_read(request.user)

        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return JsonResponse({"success": True, "count": count})

        return redirect("notifications:center")

    return redirect("notifications:center")


@login_required
def get_unread_count(request):
    """API endpoint to get unread notification count (for AJAX)"""
    count = NotificationService.get_unread_count(request.user)
    return JsonResponse({"count": count})


@login_required
def notification_preferences(request):
    """View and update notification preferences"""
    preferences, created = NotificationPreference.objects.get_or_create(
        user=request.user
    )

    if request.method == "POST":
        # Update in-app notifications
        preferences.in_app_notifications = (
            request.POST.get("in_app_notifications") == "on"
        )

        # Update email preferences
        preferences.email_on_attendance_approval = (
            request.POST.get("email_on_attendance_approval") == "on"
        )
        preferences.email_on_assessment_created = (
            request.POST.get("email_on_assessment_created") == "on"
        )
        preferences.email_on_assessment_reviewed = (
            request.POST.get("email_on_assessment_reviewed") == "on"
        )
        preferences.email_on_absence_status = (
            request.POST.get("email_on_absence_status") == "on"
        )
        preferences.email_on_onboarding = (
            request.POST.get("email_on_onboarding") == "on"
        )

        # Update digest preferences
        preferences.daily_digest = request.POST.get("daily_digest") == "on"
        preferences.weekly_digest = request.POST.get("weekly_digest") == "on"

        preferences.save()

        messages.success(request, "✓ Notification preferences updated successfully!")
        return redirect("notifications:preferences")

    context = {
        "preferences": preferences,
    }

    return render(request, "notifications/preferences.html", context)
