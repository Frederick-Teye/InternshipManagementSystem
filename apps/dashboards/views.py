from __future__ import annotations

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.db.models import Count, Avg, Q

from apps.accounts.decorators import (
    admin_required,
    employee_required,
    intern_required,
    manager_required,
    supervisor_required,
)
from apps.interns.models import InternProfile
from apps.supervisors.models import EmployeeProfile
from apps.attendance.models import Attendance
from apps.evaluations.models import PerformanceAssessment
from apps.absenteeism.models import AbsenteeismRequest
from apps.branches.models import Branch
from apps.schools.models import School
from apps.accounts.models import User


@login_required
def dashboard(request):
    """Route users to their role-specific dashboard"""
    user = request.user

    if user.is_superuser or user.role == "admin":
        return redirect("dashboards:admin")
    elif user.role == "manager":
        return redirect("dashboards:manager")
    elif user.role == "supervisor":
        return redirect("dashboards:supervisor")
    elif user.role == "intern":
        return redirect("dashboards:intern")
    elif user.role == "employee":
        return redirect("dashboards:employee")
    else:
        # Default to employee dashboard for any other role
        return redirect("dashboards:employee")


@intern_required
def intern_dashboard(request):
    """Intern dashboard view with real data"""
    today = timezone.localdate()
    intern_profile = get_object_or_404(InternProfile, user=request.user)

    # Attendance statistics
    total_attendance = Attendance.objects.filter(intern=intern_profile).count()
    approved_attendance = Attendance.objects.filter(
        intern=intern_profile, approval_status="approved"
    ).count()
    pending_attendance = Attendance.objects.filter(
        intern=intern_profile, approval_status="pending"
    ).count()
    rejected_attendance = Attendance.objects.filter(
        intern=intern_profile, approval_status="rejected"
    ).count()

    # Check if marked attendance today
    has_checked_in_today = Attendance.objects.filter(
        intern=intern_profile, check_in_time__date=today
    ).exists()

    # Assessment statistics
    total_assessments = PerformanceAssessment.objects.filter(
        intern=intern_profile
    ).count()
    pending_self_assessments = PerformanceAssessment.objects.filter(
        intern=intern_profile, status="draft", intern_score__isnull=True
    ).count()
    reviewed_assessments = PerformanceAssessment.objects.filter(
        intern=intern_profile, status="reviewed"
    ).count()

    # Average supervisor score
    avg_score = PerformanceAssessment.objects.filter(
        intern=intern_profile, supervisor_score__isnull=False
    ).aggregate(Avg("supervisor_score"))["supervisor_score__avg"]

    # Absenteeism statistics
    total_absence_requests = AbsenteeismRequest.objects.filter(
        intern=intern_profile
    ).count()
    pending_absence_requests = AbsenteeismRequest.objects.filter(
        intern=intern_profile, status="pending"
    ).count()
    approved_absence_requests = AbsenteeismRequest.objects.filter(
        intern=intern_profile, status="approved"
    ).count()

    # Recent assessments (last 3)
    recent_assessments = PerformanceAssessment.objects.filter(
        intern=intern_profile
    ).order_by("-week_number")[:3]

    # Recent absence requests (last 3)
    recent_absence_requests = AbsenteeismRequest.objects.filter(
        intern=intern_profile
    ).order_by("-submitted_at")[:3]

    context = {
        "today": today,
        "intern_profile": intern_profile,
        "has_checked_in_today": has_checked_in_today,
        # Attendance stats
        "total_attendance": total_attendance,
        "approved_attendance": approved_attendance,
        "pending_attendance": pending_attendance,
        "rejected_attendance": rejected_attendance,
        # Assessment stats
        "total_assessments": total_assessments,
        "pending_self_assessments": pending_self_assessments,
        "reviewed_assessments": reviewed_assessments,
        "average_score": round(avg_score, 1) if avg_score else None,
        # Absence stats
        "total_absence_requests": total_absence_requests,
        "pending_absence_requests": pending_absence_requests,
        "approved_absence_requests": approved_absence_requests,
        # Recent items
        "recent_assessments": recent_assessments,
        "recent_absence_requests": recent_absence_requests,
    }

    return render(request, "dashboards/intern.html", context)


@supervisor_required
def supervisor_dashboard(request):
    """Supervisor dashboard view with real data"""
    today = timezone.localdate()
    employee_profile = get_object_or_404(EmployeeProfile, user=request.user)

    # Get assigned interns
    my_interns = InternProfile.objects.filter(internal_supervisor=employee_profile)
    intern_count = my_interns.count()

    # Pending attendance approvals
    pending_attendance = Attendance.objects.filter(
        intern__internal_supervisor=employee_profile, approval_status="pending"
    ).count()

    # Pending assessments (submitted, awaiting supervisor review)
    pending_assessments = PerformanceAssessment.objects.filter(
        assessed_by=employee_profile, status="submitted", supervisor_score__isnull=True
    ).count()

    # Pending absence requests
    pending_absences = AbsenteeismRequest.objects.filter(
        intern__internal_supervisor=employee_profile, status="pending"
    ).count()

    # Recent activities
    recent_attendance = (
        Attendance.objects.filter(
            intern__internal_supervisor=employee_profile, approval_status="pending"
        )
        .select_related("intern__user")
        .order_by("-check_in_time")[:5]
    )

    recent_assessments = (
        PerformanceAssessment.objects.filter(
            assessed_by=employee_profile, status="submitted"
        )
        .select_related("intern__user")
        .order_by("-created_at")[:5]
    )

    recent_absences = (
        AbsenteeismRequest.objects.filter(
            intern__internal_supervisor=employee_profile, status="pending"
        )
        .select_related("intern__user")
        .order_by("-submitted_at")[:5]
    )

    context = {
        "today": today,
        "employee_profile": employee_profile,
        "intern_count": intern_count,
        "my_interns": my_interns[:10],  # Show first 10
        "pending_attendance": pending_attendance,
        "pending_assessments": pending_assessments,
        "pending_absences": pending_absences,
        "recent_attendance": recent_attendance,
        "recent_assessments": recent_assessments,
        "recent_absences": recent_absences,
    }

    return render(request, "dashboards/supervisor.html", context)


@manager_required
def manager_dashboard(request):
    """Manager dashboard view with system-wide data"""
    today = timezone.localdate()

    # System-wide statistics
    total_interns = InternProfile.objects.count()
    total_supervisors = EmployeeProfile.objects.filter(
        user__role__in=["supervisor", "manager"]
    ).count()
    total_branches = Branch.objects.count()
    total_assessments = PerformanceAssessment.objects.count()

    # Pending items across system
    pending_attendance = Attendance.objects.filter(approval_status="pending").count()
    pending_assessments = PerformanceAssessment.objects.filter(
        status="submitted", supervisor_score__isnull=True
    ).count()
    pending_absences = AbsenteeismRequest.objects.filter(status="pending").count()

    # Active interns (with recent attendance)
    active_interns = (
        InternProfile.objects.filter(
            attendance_records__check_in_time__gte=timezone.now()
            - timezone.timedelta(days=7)
        )
        .distinct()
        .count()
    )

    # Recent system activity
    recent_attendance = Attendance.objects.select_related("intern__user").order_by(
        "-check_in_time"
    )[:10]

    recent_assessments = PerformanceAssessment.objects.select_related(
        "intern__user", "assessed_by__user"
    ).order_by("-created_at")[:10]

    recent_absences = AbsenteeismRequest.objects.select_related(
        "intern__user"
    ).order_by("-submitted_at")[:10]

    context = {
        "today": today,
        "total_interns": total_interns,
        "total_supervisors": total_supervisors,
        "total_branches": total_branches,
        "total_assessments": total_assessments,
        "active_interns": active_interns,
        "pending_attendance": pending_attendance,
        "pending_assessments": pending_assessments,
        "pending_absences": pending_absences,
        "recent_attendance": recent_attendance,
        "recent_assessments": recent_assessments,
        "recent_absences": recent_absences,
    }

    return render(request, "dashboards/manager.html", context)


@admin_required
def admin_dashboard(request):
    """Admin dashboard view with comprehensive system data"""
    today = timezone.localdate()

    # User statistics
    total_users = User.objects.count()
    total_interns = InternProfile.objects.count()
    total_supervisors = EmployeeProfile.objects.count()
    total_branches = Branch.objects.count()
    total_schools = School.objects.count()

    # Activity statistics
    total_attendance = Attendance.objects.count()
    total_assessments = PerformanceAssessment.objects.count()
    total_absences = AbsenteeismRequest.objects.count()

    # Pending items
    pending_attendance = Attendance.objects.filter(approval_status="pending").count()
    pending_assessments = PerformanceAssessment.objects.filter(
        status="submitted", supervisor_score__isnull=True
    ).count()
    pending_absences = AbsenteeismRequest.objects.filter(status="pending").count()

    # Recent activity across the system
    recent_users = User.objects.order_by("-date_joined")[:5]
    recent_attendance = Attendance.objects.select_related(
        "intern__user", "branch"
    ).order_by("-check_in_time")[:10]
    recent_assessments = PerformanceAssessment.objects.select_related(
        "intern__user", "assessed_by__user"
    ).order_by("-created_at")[:10]

    # System health
    active_sessions = User.objects.filter(
        last_login__gte=timezone.now() - timezone.timedelta(days=1)
    ).count()

    context = {
        "today": today,
        "total_users": total_users,
        "total_interns": total_interns,
        "total_supervisors": total_supervisors,
        "total_branches": total_branches,
        "total_schools": total_schools,
        "total_attendance": total_attendance,
        "total_assessments": total_assessments,
        "total_absences": total_absences,
        "pending_attendance": pending_attendance,
        "pending_assessments": pending_assessments,
        "pending_absences": pending_absences,
        "active_sessions": active_sessions,
        "recent_users": recent_users,
        "recent_attendance": recent_attendance,
        "recent_assessments": recent_assessments,
    }

    return render(request, "dashboards/admin.html", context)


@employee_required
def employee_dashboard(request):
    """Employee dashboard view with basic data"""
    today = timezone.localdate()

    try:
        employee_profile = EmployeeProfile.objects.get(user=request.user)
    except EmployeeProfile.DoesNotExist:
        employee_profile = None

    context = {
        "today": today,
        "employee_profile": employee_profile,
    }

    return render(request, "dashboards/employee.html", context)
