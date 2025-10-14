from __future__ import annotations

from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from django.http import HttpResponse

from apps.interns.models import InternProfile
from apps.attendance.models import Attendance
from apps.evaluations.models import PerformanceAssessment
from apps.accounts.decorators import supervisor_or_above
from apps.reports.services import ReportService


@login_required
def download_intern_report(request, intern_id):
    """
    Download PDF performance report for an intern.

    Permissions:
    - Intern can download their own report
    - Supervisors can download reports for their assigned interns
    - Managers and admins can download any report
    """
    intern_profile = get_object_or_404(InternProfile, id=intern_id)

    # Permission check
    if request.user.role == "intern":
        # Interns can only download their own report
        if intern_profile.user != request.user:
            messages.error(request, "You can only download your own report.")
            return redirect("dashboards:intern_dashboard")
    elif request.user.role == "supervisor":
        # Supervisors can only download reports for their assigned interns
        from apps.supervisors.models import EmployeeProfile

        try:
            employee_profile = EmployeeProfile.objects.get(user=request.user)
            if intern_profile not in employee_profile.assigned_interns.all():
                messages.error(
                    request, "You can only download reports for your assigned interns."
                )
                return redirect("dashboards:supervisor_dashboard")
        except EmployeeProfile.DoesNotExist:
            messages.error(
                request, "You do not have permission to download this report."
            )
            return redirect("dashboards:supervisor_dashboard")
    # Managers and admins can download any report

    # Generate and return PDF
    return ReportService.generate_intern_performance_pdf(intern_profile)


@login_required
@supervisor_or_above
def export_attendance_csv(request):
    """
    Export attendance records as CSV.

    Query parameters:
    - intern_id: Filter by specific intern
    - start_date: Filter from this date
    - end_date: Filter to this date
    - status: Filter by approval status
    """
    queryset = (
        Attendance.objects.all()
        .select_related("intern__user", "intern__branch", "approver")
        .order_by("-check_in_time")
    )

    # Apply filters
    intern_id = request.GET.get("intern_id")
    if intern_id:
        queryset = queryset.filter(intern_id=intern_id)

    start_date = request.GET.get("start_date")
    if start_date:
        queryset = queryset.filter(check_in_time__date__gte=start_date)

    end_date = request.GET.get("end_date")
    if end_date:
        queryset = queryset.filter(check_in_time__date__lte=end_date)

    status = request.GET.get("status")
    if status:
        queryset = queryset.filter(approval_status=status)

    # Permission check for supervisors
    if request.user.role == "supervisor":
        from apps.supervisors.models import EmployeeProfile

        try:
            employee_profile = EmployeeProfile.objects.get(user=request.user)
            queryset = queryset.filter(
                intern__in=employee_profile.assigned_interns.all()
            )
        except EmployeeProfile.DoesNotExist:
            queryset = queryset.none()

    return ReportService.generate_attendance_csv(queryset)


@login_required
@supervisor_or_above
def export_assessments_csv(request):
    """
    Export assessment records as CSV.

    Query parameters:
    - intern_id: Filter by specific intern
    - week_number: Filter by week
    - status: Filter by status
    """
    queryset = (
        PerformanceAssessment.objects.all()
        .select_related("intern__user", "assessed_by__user")
        .order_by("-assessment_date")
    )

    # Apply filters
    intern_id = request.GET.get("intern_id")
    if intern_id:
        queryset = queryset.filter(intern_id=intern_id)

    week_number = request.GET.get("week_number")
    if week_number:
        queryset = queryset.filter(week_number=week_number)

    status = request.GET.get("status")
    if status:
        queryset = queryset.filter(status=status)

    # Permission check for supervisors
    if request.user.role == "supervisor":
        from apps.supervisors.models import EmployeeProfile

        try:
            employee_profile = EmployeeProfile.objects.get(user=request.user)
            queryset = queryset.filter(
                intern__in=employee_profile.assigned_interns.all()
            )
        except EmployeeProfile.DoesNotExist:
            queryset = queryset.none()

    return ReportService.generate_assessments_csv(queryset)
