from __future__ import annotations

from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import render
from django.urls import reverse
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib import messages

from apps.accounts.decorators import admin_required, supervisor_required
from apps.log.models import ActivityLog


@login_required
@admin_required
def activity_log_list(request):
    """
    View for displaying activity logs with filtering and pagination.
    Only accessible to admins.
    """
    # Get query parameters
    page = request.GET.get("page", 1)
    search = request.GET.get("search", "")
    action_filter = request.GET.get("action", "")
    user_filter = request.GET.get("user", "")
    date_from = request.GET.get("date_from", "")
    date_to = request.GET.get("date_to", "")

    # Base queryset
    logs = ActivityLog.objects.select_related("actor", "content_type").order_by(
        "-timestamp"
    )

    # Apply filters
    if search:
        logs = logs.filter(
            Q(action__icontains=search)
            | Q(actor__first_name__icontains=search)
            | Q(actor__last_name__icontains=search)
            | Q(actor__email__icontains=search)
        )

    if action_filter:
        logs = logs.filter(action__icontains=action_filter)

    if user_filter:
        logs = logs.filter(actor__id=user_filter)

    if date_from:
        logs = logs.filter(timestamp__date__gte=date_from)

    if date_to:
        logs = logs.filter(timestamp__date__lte=date_to)

    # Pagination
    paginator = Paginator(logs, 25)  # 25 logs per page
    logs_page = paginator.get_page(page)

    # Get unique actions for filter dropdown
    actions = (
        ActivityLog.objects.values_list("action", flat=True)
        .distinct()
        .order_by("action")
    )

    # Get users who have activity logs
    users_with_logs = (
        ActivityLog.objects.exclude(actor__isnull=True)
        .values_list(
            "actor__id", "actor__first_name", "actor__last_name", "actor__email"
        )
        .distinct()
        .order_by("actor__first_name", "actor__last_name")
    )

    context = {
        "logs": logs_page,
        "actions": actions,
        "users": users_with_logs,
        "search": search,
        "action_filter": action_filter,
        "user_filter": user_filter,
        "date_from": date_from,
        "date_to": date_to,
        "total_logs": logs.count(),
    }

    return render(request, "log/activity_log.html", context)


@login_required
@supervisor_required
def user_activity_log(request, user_id=None):
    """
    View for supervisors to see activity logs for their interns or all users.
    """
    # Get query parameters
    page = request.GET.get("page", 1)
    search = request.GET.get("search", "")
    action_filter = request.GET.get("action", "")
    date_from = request.GET.get("date_from", "")
    date_to = request.GET.get("date_to", "")

    # Base queryset - filter by supervisor's interns if user_id not specified
    if user_id:
        logs = (
            ActivityLog.objects.filter(actor__id=user_id)
            .select_related("actor", "content_type")
            .order_by("-timestamp")
        )
    else:
        # For supervisors, show logs for their interns
        if hasattr(request.user, "supervisor_profile"):
            intern_ids = request.user.supervisor_profile.interns.values_list(
                "user__id", flat=True
            )
            logs = (
                ActivityLog.objects.filter(actor__id__in=intern_ids)
                .select_related("actor", "content_type")
                .order_by("-timestamp")
            )
        else:
            logs = ActivityLog.objects.none()

    # Apply filters
    if search:
        logs = logs.filter(
            Q(action__icontains=search)
            | Q(actor__first_name__icontains=search)
            | Q(actor__last_name__icontains=search)
            | Q(actor__email__icontains=search)
        )

    if action_filter:
        logs = logs.filter(action__icontains=action_filter)

    if date_from:
        logs = logs.filter(timestamp__date__gte=date_from)

    if date_to:
        logs = logs.filter(timestamp__date__lte=date_to)

    # Pagination
    paginator = Paginator(logs, 20)  # 20 logs per page for supervisors
    logs_page = paginator.get_page(page)

    # Get unique actions for filter dropdown
    actions = logs.values_list("action", flat=True).distinct().order_by("action")

    context = {
        "logs": logs_page,
        "actions": actions,
        "search": search,
        "action_filter": action_filter,
        "date_from": date_from,
        "date_to": date_to,
        "total_logs": logs.count(),
        "user_id": user_id,
    }

    return render(request, "log/user_activity_log.html", context)


@login_required
def my_activity_log(request):
    """
    View for users to see their own activity logs.
    """
    # Get query parameters
    page = request.GET.get("page", 1)
    search = request.GET.get("search", "")
    action_filter = request.GET.get("action", "")
    date_from = request.GET.get("date_from", "")
    date_to = request.GET.get("date_to", "")

    # Base queryset - only user's own logs
    logs = (
        ActivityLog.objects.filter(actor=request.user)
        .select_related("content_type")
        .order_by("-timestamp")
    )

    # Apply filters
    if search:
        logs = logs.filter(action__icontains=search)

    if action_filter:
        logs = logs.filter(action__icontains=action_filter)

    if date_from:
        logs = logs.filter(timestamp__date__gte=date_from)

    if date_to:
        logs = logs.filter(timestamp__date__lte=date_to)

    # Pagination
    paginator = Paginator(logs, 15)  # 15 logs per page for personal view
    logs_page = paginator.get_page(page)

    # Get unique actions for filter dropdown
    actions = logs.values_list("action", flat=True).distinct().order_by("action")

    context = {
        "logs": logs_page,
        "actions": actions,
        "search": search,
        "action_filter": action_filter,
        "date_from": date_from,
        "date_to": date_to,
        "total_logs": logs.count(),
    }

    return render(request, "log/my_activity_log.html", context)


@require_POST
@login_required
@admin_required
def clear_activity_logs(request):
    """
    AJAX endpoint to clear old activity logs.
    Only accessible to admins.
    """
    days = request.POST.get("days", 30)

    try:
        days = int(days)
        from django.utils import timezone

        cutoff_date = timezone.now() - timezone.timedelta(days=days)

        deleted_count, _ = ActivityLog.objects.filter(
            timestamp__lt=cutoff_date
        ).delete()

        return JsonResponse(
            {
                "success": True,
                "message": f"Successfully deleted {deleted_count} activity logs older than {days} days.",
            }
        )

    except (ValueError, TypeError):
        return JsonResponse(
            {"success": False, "message": "Invalid number of days provided."},
            status=400,
        )
