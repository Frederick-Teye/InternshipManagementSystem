from __future__ import annotations

from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages

from apps.interns.models import InternProfile
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
