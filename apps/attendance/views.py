from __future__ import annotations

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from apps.accounts.decorators import intern_required, supervisor_or_above
from apps.attendance.forms import (
    AttendanceApprovalForm,
    AttendanceMarkForm,
    CheckOutForm,
)
from apps.attendance.models import Attendance
from apps.interns.models import InternProfile


@login_required
@intern_required
def mark_attendance(request):
    """View for intern to mark attendance with GPS coordinates"""
    try:
        intern_profile = InternProfile.objects.get(user=request.user)
    except InternProfile.DoesNotExist:
        messages.error(
            request,
            "Your intern profile is not set up. Please contact an administrator.",
        )
        return redirect("accounts:dashboard")

    if not intern_profile.branch:
        messages.error(
            request,
            "You have not been assigned to a branch yet. Please contact your supervisor.",
        )
        return redirect("accounts:dashboard")

    # Check if already marked attendance today
    today = timezone.localdate()
    existing_attendance = Attendance.objects.filter(
        intern=intern_profile, check_in_time__date=today
    ).first()

    if existing_attendance:
        messages.info(request, "You have already marked attendance today.")
        return redirect("attendance:my_attendance")

    if request.method == "POST":
        form = AttendanceMarkForm(request.POST, intern_profile=intern_profile)
        if form.is_valid():
            attendance = form.save()

            if attendance.auto_approved:
                messages.success(
                    request,
                    f"✓ Attendance marked successfully! Auto-approved (within {intern_profile.branch.proximity_threshold_meters}m of branch).",
                )
            else:
                distance = attendance.distance_from_branch()
                if distance:
                    messages.warning(
                        request,
                        f"⚠ Attendance recorded but requires approval. You are {distance:.0f}m from the branch location.",
                    )
                else:
                    messages.warning(
                        request, "Attendance recorded and pending supervisor approval."
                    )

            return redirect("attendance:my_attendance")
    else:
        form = AttendanceMarkForm(intern_profile=intern_profile)

    context = {
        "form": form,
        "intern_profile": intern_profile,
        "branch": intern_profile.branch,
        "today": today,
    }
    return render(request, "attendance/mark_attendance.html", context)


@login_required
@intern_required
def my_attendance(request):
    """View attendance history for intern"""
    try:
        intern_profile = InternProfile.objects.get(user=request.user)
    except InternProfile.DoesNotExist:
        messages.error(request, "Your intern profile is not set up.")
        return redirect("accounts:dashboard")

    attendances = Attendance.objects.filter(intern=intern_profile).order_by(
        "-check_in_time"
    )

    # Calculate statistics
    total = attendances.count()
    approved = attendances.filter(
        approval_status=Attendance.ApprovalStatus.APPROVED
    ).count()
    pending = attendances.filter(
        approval_status=Attendance.ApprovalStatus.PENDING
    ).count()
    rejected = attendances.filter(
        approval_status=Attendance.ApprovalStatus.REJECTED
    ).count()

    context = {
        "attendances": attendances,
        "stats": {
            "total": total,
            "approved": approved,
            "pending": pending,
            "rejected": rejected,
        },
    }
    return render(request, "attendance/my_attendance.html", context)


@login_required
@intern_required
def checkout(request, attendance_id):
    """Checkout from attendance"""
    attendance = get_object_or_404(
        Attendance, id=attendance_id, intern__user=request.user
    )

    if attendance.check_out_time:
        messages.warning(request, "You have already checked out for this attendance.")
        return redirect("attendance:my_attendance")

    if request.method == "POST":
        form = CheckOutForm(request.POST)
        if form.is_valid():
            attendance.check_out_time = timezone.now()
            if form.cleaned_data.get("notes"):
                attendance.notes += f"\nCheckout notes: {form.cleaned_data['notes']}"
            attendance.save()
            messages.success(request, "✓ Successfully checked out!")
            return redirect("attendance:my_attendance")
    else:
        form = CheckOutForm()

    context = {
        "attendance": attendance,
        "form": form,
    }
    return render(request, "attendance/checkout.html", context)


@login_required
@supervisor_or_above
def pending_approvals(request):
    """View for supervisors to see pending attendance approvals"""
    # Get interns assigned to this supervisor
    try:
        from apps.supervisors.models import EmployeeProfile

        employee_profile = EmployeeProfile.objects.get(user=request.user)
        assigned_interns = employee_profile.assigned_interns.all()
    except:
        assigned_interns = InternProfile.objects.none()

    # For managers and admins, show all pending
    if request.user.role in ["manager", "admin"]:
        pending_attendances = (
            Attendance.objects.filter(approval_status=Attendance.ApprovalStatus.PENDING)
            .select_related("intern__user", "branch")
            .order_by("-check_in_time")
        )
    else:
        pending_attendances = (
            Attendance.objects.filter(
                intern__in=assigned_interns,
                approval_status=Attendance.ApprovalStatus.PENDING,
            )
            .select_related("intern__user", "branch")
            .order_by("-check_in_time")
        )

    context = {
        "pending_attendances": pending_attendances,
    }
    return render(request, "attendance/pending_approvals.html", context)


@login_required
@supervisor_or_above
def approve_attendance(request, attendance_id):
    """Approve or reject attendance"""
    attendance = get_object_or_404(Attendance, id=attendance_id)

    # Check permission - must be supervisor of this intern or manager/admin
    if request.user.role not in ["manager", "admin"]:
        try:
            from apps.supervisors.models import EmployeeProfile

            employee_profile = EmployeeProfile.objects.get(user=request.user)
            if attendance.intern not in employee_profile.assigned_interns.all():
                messages.error(
                    request, "You do not have permission to approve this attendance."
                )
                return redirect("attendance:pending_approvals")
        except:
            messages.error(
                request, "You do not have permission to approve this attendance."
            )
            return redirect("attendance:pending_approvals")

    if attendance.approval_status != Attendance.ApprovalStatus.PENDING:
        messages.warning(request, "This attendance has already been processed.")
        return redirect("attendance:pending_approvals")

    if request.method == "POST":
        form = AttendanceApprovalForm(request.POST)
        if form.is_valid():
            action = form.cleaned_data["action"]
            note = form.cleaned_data.get("note", "")

            if action == "approve":
                attendance.approve(approver=request.user)
                messages.success(
                    request,
                    f"✓ Attendance approved for {attendance.intern.user.get_full_name()}",
                )
            else:
                attendance.reject(approver=request.user, note=note)
                messages.info(
                    request,
                    f"Attendance rejected for {attendance.intern.user.get_full_name()}",
                )

            attendance.save()
            return redirect("attendance:pending_approvals")
    else:
        form = AttendanceApprovalForm()

    # Calculate distance for display
    distance = attendance.distance_from_branch()

    context = {
        "attendance": attendance,
        "form": form,
        "distance": distance,
    }
    return render(request, "attendance/approve_attendance.html", context)


@login_required
@supervisor_or_above
def attendance_list(request):
    """View all attendance records with filters"""
    attendances = (
        Attendance.objects.all()
        .select_related("intern__user", "branch", "approved_by")
        .order_by("-check_in_time")
    )

    # Apply filters
    status_filter = request.GET.get("status")
    if status_filter:
        attendances = attendances.filter(approval_status=status_filter)

    intern_filter = request.GET.get("intern")
    if intern_filter:
        attendances = attendances.filter(
            Q(intern__user__first_name__icontains=intern_filter)
            | Q(intern__user__last_name__icontains=intern_filter)
            | Q(intern__user__email__icontains=intern_filter)
        )

    date_from = request.GET.get("date_from")
    if date_from:
        attendances = attendances.filter(check_in_time__date__gte=date_from)

    date_to = request.GET.get("date_to")
    if date_to:
        attendances = attendances.filter(check_in_time__date__lte=date_to)

    context = {
        "attendances": attendances,
        "status_choices": Attendance.ApprovalStatus.choices,
    }
    return render(request, "attendance/attendance_list.html", context)
