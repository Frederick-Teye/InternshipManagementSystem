from __future__ import annotations

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from apps.absenteeism.forms import AbsenteeismApprovalForm, AbsenteeismRequestForm
from apps.absenteeism.models import AbsenteeismRequest
from apps.accounts.decorators import intern_required, supervisor_or_above
from apps.notifications.services import NotificationService
from apps.interns.models import InternProfile
from apps.supervisors.models import EmployeeProfile


@login_required
@intern_required
def request_absence(request):
    """Intern submits absenteeism request"""
    intern_profile = get_object_or_404(InternProfile, user=request.user)

    if request.method == "POST":
        form = AbsenteeismRequestForm(request.POST, request.FILES)
        if form.is_valid():
            absence_request = form.save(commit=False)
            absence_request.intern = intern_profile
            absence_request.save()

            # Notify supervisor of new absence request
            NotificationService.notify_supervisor_new_absence_request(absence_request)

            messages.success(
                request,
                "Your absence request has been submitted successfully and is pending approval.",
            )
            return redirect("absenteeism:my_requests")
    else:
        form = AbsenteeismRequestForm()

    return render(request, "absenteeism/request_absence.html", {"form": form})


@login_required
@intern_required
def my_requests(request):
    """Intern views their absence requests"""
    intern_profile = get_object_or_404(InternProfile, user=request.user)
    requests = AbsenteeismRequest.objects.filter(intern=intern_profile).select_related(
        "approver"
    )

    # Calculate statistics
    total_requests = requests.count()
    pending_count = requests.filter(status="pending").count()
    approved_count = requests.filter(status="approved").count()
    rejected_count = requests.filter(status="rejected").count()

    return render(
        request,
        "absenteeism/my_requests.html",
        {
            "requests": requests,
            "total_requests": total_requests,
            "pending_count": pending_count,
            "approved_count": approved_count,
            "rejected_count": rejected_count,
        },
    )


@login_required
@intern_required
def cancel_request(request, request_id):
    """Intern cancels their pending absence request"""
    absence_request = get_object_or_404(AbsenteeismRequest, id=request_id)

    # Permission check
    if absence_request.intern.user != request.user:
        messages.error(request, "You cannot cancel this request.")
        return redirect("absenteeism:my_requests")

    # Can only cancel pending requests
    if absence_request.status != AbsenteeismRequest.Status.PENDING:
        messages.error(request, "You can only cancel pending requests.")
        return redirect("absenteeism:my_requests")

    if request.method == "POST":
        absence_request.cancel()
        absence_request.save()
        messages.success(request, "Your absence request has been cancelled.")
        return redirect("absenteeism:my_requests")

    return render(
        request,
        "absenteeism/cancel_request.html",
        {"absence_request": absence_request},
    )


@login_required
@supervisor_or_above
def pending_requests(request):
    """Supervisor/Manager views pending absence requests"""
    # Get employee profile
    try:
        employee_profile = EmployeeProfile.objects.get(user=request.user)
    except EmployeeProfile.DoesNotExist:
        employee_profile = None

    # Role-based filtering
    if request.user.role in ["manager", "admin"]:
        # Managers/admins see all pending requests
        requests = AbsenteeismRequest.objects.filter(status="pending")
    else:
        # Supervisors see only their interns' requests
        if employee_profile:
            requests = AbsenteeismRequest.objects.filter(
                intern__internal_supervisor=employee_profile, status="pending"
            )
        else:
            requests = AbsenteeismRequest.objects.none()

    requests = requests.select_related("intern__user").order_by("submitted_at")

    return render(
        request,
        "absenteeism/pending_requests.html",
        {"requests": requests},
    )


@login_required
@supervisor_or_above
def approve_request(request, request_id):
    """Supervisor/Manager approves or rejects absence request"""
    absence_request = get_object_or_404(
        AbsenteeismRequest.objects.select_related(
            "intern__user", "intern__internal_supervisor__user"
        ),
        id=request_id,
    )

    # Permission check
    if request.user.role == "supervisor":
        employee_profile = get_object_or_404(EmployeeProfile, user=request.user)
        if absence_request.intern.internal_supervisor != employee_profile:
            messages.error(request, "You cannot approve this request.")
            return redirect("absenteeism:pending_requests")
    # Managers and admins can approve any request

    # Can only approve pending requests
    if absence_request.status != AbsenteeismRequest.Status.PENDING:
        messages.error(request, "This request has already been processed.")
        return redirect("absenteeism:request_list")

    if request.method == "POST":
        form = AbsenteeismApprovalForm(request.POST)
        if form.is_valid():
            decision = form.cleaned_data["decision"]
            decision_note = form.cleaned_data.get("decision_note", "")

            if decision == "approve":
                absence_request.approve(approver=request.user, note=decision_note)
                absence_request.save()
                messages.success(
                    request,
                    f"Absence request for {absence_request.intern.user.get_full_name()} has been approved.",
                )
                # Send notification
                NotificationService.notify_absence_approved(
                    absence_request=absence_request, approver=request.user
                )
            else:
                absence_request.reject(approver=request.user, note=decision_note)
                absence_request.save()
                messages.warning(
                    request,
                    f"Absence request for {absence_request.intern.user.get_full_name()} has been rejected.",
                )
                # Send notification
                NotificationService.notify_absence_rejected(
                    absence_request=absence_request,
                    approver=request.user,
                    reason=decision_note,
                )

            return redirect("absenteeism:pending_requests")
    else:
        form = AbsenteeismApprovalForm()

    return render(
        request,
        "absenteeism/approve_request.html",
        {
            "absence_request": absence_request,
            "form": form,
        },
    )


@login_required
@supervisor_or_above
def request_list(request):
    """Supervisor/Manager views all absence requests"""
    # Get employee profile
    try:
        employee_profile = EmployeeProfile.objects.get(user=request.user)
    except EmployeeProfile.DoesNotExist:
        employee_profile = None

    # Role-based filtering
    if request.user.role in ["manager", "admin"]:
        # Managers/admins see all requests
        all_requests = AbsenteeismRequest.objects.all()
    else:
        # Supervisors see only their interns' requests
        if employee_profile:
            all_requests = AbsenteeismRequest.objects.filter(
                intern__internal_supervisor=employee_profile
            )
        else:
            all_requests = AbsenteeismRequest.objects.none()

    # Filter by status if requested
    status_filter = request.GET.get("status", "all")
    if status_filter and status_filter != "all":
        requests = all_requests.filter(status=status_filter)
    else:
        requests = all_requests

    requests = requests.select_related("intern__user", "approver").order_by(
        "-submitted_at"
    )

    # Count by status
    total_count = all_requests.count()
    pending_count = all_requests.filter(status="pending").count()
    approved_count = all_requests.filter(status="approved").count()
    rejected_count = all_requests.filter(status="rejected").count()

    return render(
        request,
        "absenteeism/request_list.html",
        {
            "requests": requests,
            "status_filter": status_filter,
            "total_count": total_count,
            "pending_count": pending_count,
            "approved_count": approved_count,
            "rejected_count": rejected_count,
        },
    )


@login_required
def view_request(request, request_id):
    """View detailed absence request"""
    absence_request = get_object_or_404(
        AbsenteeismRequest.objects.select_related("intern__user", "approver"),
        id=request_id,
    )

    # Permission check
    can_approve = False
    if request.user.role == "intern":
        # Interns can only view their own
        if absence_request.intern.user != request.user:
            messages.error(request, "You cannot view this request.")
            return redirect("absenteeism:my_requests")
    elif request.user.role == "supervisor":
        # Supervisors can only view their interns' requests
        employee_profile = get_object_or_404(EmployeeProfile, user=request.user)
        if absence_request.intern.internal_supervisor != employee_profile:
            messages.error(request, "You cannot view this request.")
            return redirect("absenteeism:request_list")
        can_approve = True
    elif request.user.role in ["manager", "admin"]:
        # Managers and admins can view all
        can_approve = True

    return render(
        request,
        "absenteeism/view_request.html",
        {
            "absence_request": absence_request,
            "can_approve": can_approve,
        },
    )
