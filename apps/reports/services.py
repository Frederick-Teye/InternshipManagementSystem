"""
Report generation service for PDF and other report types.
"""

from __future__ import annotations

from io import BytesIO
from datetime import datetime, timedelta
from typing import Optional

from django.template.loader import render_to_string
from django.http import HttpResponse
from django.db.models import Avg, Count, Q
from weasyprint import HTML, CSS

from apps.interns.models import InternProfile
from apps.attendance.models import Attendance
from apps.evaluations.models import PerformanceAssessment
from apps.absenteeism.models import AbsenteeismRequest


class ReportService:
    """Service for generating various types of reports"""

    @staticmethod
    def generate_intern_performance_pdf(intern_profile: InternProfile) -> HttpResponse:
        """
        Generate a comprehensive PDF performance report for an intern.

        Args:
            intern_profile: InternProfile instance

        Returns:
            HttpResponse with PDF content
        """
        # Gather all data for the report
        report_data = ReportService._gather_intern_data(intern_profile)

        # Render HTML template
        html_string = render_to_string(
            "reports/intern_performance_report.html", report_data
        )

        # Generate PDF
        html = HTML(string=html_string, base_url=".")
        css = CSS(string=ReportService._get_pdf_styles())

        # Create PDF
        pdf_file = html.write_pdf(stylesheets=[css])

        # Create response
        response = HttpResponse(pdf_file, content_type="application/pdf")
        filename = f"Performance_Report_{intern_profile.user.get_full_name().replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}.pdf"
        response["Content-Disposition"] = f'attachment; filename="{filename}"'

        return response

    @staticmethod
    def _gather_intern_data(intern_profile: InternProfile) -> dict:
        """
        Gather all necessary data for intern performance report.

        Args:
            intern_profile: InternProfile instance

        Returns:
            Dictionary containing all report data
        """
        # Basic intern info
        user = intern_profile.user

        # Attendance statistics
        all_attendance = Attendance.objects.filter(intern=intern_profile)
        total_attendance = all_attendance.count()
        approved_attendance = all_attendance.filter(
            approval_status=Attendance.ApprovalStatus.APPROVED
        ).count()
        rejected_attendance = all_attendance.filter(
            approval_status=Attendance.ApprovalStatus.REJECTED
        ).count()
        pending_attendance = all_attendance.filter(
            approval_status=Attendance.ApprovalStatus.PENDING
        ).count()

        # Calculate attendance rate
        attendance_rate = (
            (approved_attendance / total_attendance * 100)
            if total_attendance > 0
            else 0
        )

        # Assessment statistics
        assessments = PerformanceAssessment.objects.filter(
            intern=intern_profile
        ).order_by("week_number")

        total_assessments = assessments.count()
        completed_assessments = assessments.filter(
            status=PerformanceAssessment.Status.SUBMITTED
        ).count()

        # Calculate average scores (supervisor and intern scores)
        avg_supervisor_score = (
            assessments.filter(supervisor_score__isnull=False).aggregate(
                Avg("supervisor_score")
            )["supervisor_score__avg"]
            or 0
        )

        avg_intern_score = (
            assessments.filter(intern_score__isnull=False).aggregate(
                Avg("intern_score")
            )["intern_score__avg"]
            or 0
        )

        # Absence statistics
        absences = AbsenteeismRequest.objects.filter(intern=intern_profile)
        total_absences = absences.count()
        approved_absences = absences.filter(
            status=AbsenteeismRequest.Status.APPROVED
        ).count()
        rejected_absences = absences.filter(
            status=AbsenteeismRequest.Status.REJECTED
        ).count()
        pending_absences = absences.filter(
            status=AbsenteeismRequest.Status.PENDING
        ).count()

        # Calculate total days absent
        approved_absence_days = sum(
            (absence.end_date - absence.start_date).days + 1
            for absence in absences.filter(status=AbsenteeismRequest.Status.APPROVED)
        )

        # Internship duration
        start_date = intern_profile.start_date
        end_date = intern_profile.end_date or datetime.now().date()
        duration_days = (end_date - start_date).days if start_date else 0

        # Recent assessments (last 5)
        recent_assessments = assessments.filter(
            status=PerformanceAssessment.Status.SUBMITTED
        ).order_by("-assessment_date")[:5]

        return {
            "intern": intern_profile,
            "user": user,
            "report_date": datetime.now(),
            "start_date": start_date,
            "end_date": end_date,
            "duration_days": duration_days,
            # Attendance
            "total_attendance": total_attendance,
            "approved_attendance": approved_attendance,
            "rejected_attendance": rejected_attendance,
            "pending_attendance": pending_attendance,
            "attendance_rate": round(attendance_rate, 1),
            # Assessments
            "total_assessments": total_assessments,
            "completed_assessments": completed_assessments,
            "assessments": recent_assessments,
            # Average scores
            "avg_supervisor_score": round(avg_supervisor_score, 1),
            "avg_intern_score": round(avg_intern_score, 1),
            # Absences
            "total_absences": total_absences,
            "approved_absences": approved_absences,
            "rejected_absences": rejected_absences,
            "pending_absences": pending_absences,
            "approved_absence_days": approved_absence_days,
            # Supervisor info
            "supervisor": intern_profile.internal_supervisor,
            "branch": intern_profile.branch,
        }

    @staticmethod
    def _get_pdf_styles() -> str:
        """
        Return CSS styles for PDF reports.

        Returns:
            CSS string
        """
        return """
            @page {
                size: A4;
                margin: 2cm;
            }
            
            body {
                font-family: 'DejaVu Sans', Arial, sans-serif;
                font-size: 10pt;
                line-height: 1.6;
                color: #333;
            }
            
            .header {
                text-align: center;
                margin-bottom: 30px;
                padding-bottom: 20px;
                border-bottom: 3px solid #0d6efd;
            }
            
            .header h1 {
                color: #0d6efd;
                font-size: 24pt;
                margin: 0 0 10px 0;
            }
            
            .header .subtitle {
                color: #666;
                font-size: 12pt;
            }
            
            .section {
                margin-bottom: 25px;
                page-break-inside: avoid;
            }
            
            .section-title {
                color: #0d6efd;
                font-size: 14pt;
                font-weight: bold;
                margin-bottom: 15px;
                padding-bottom: 5px;
                border-bottom: 2px solid #e9ecef;
            }
            
            .info-grid {
                display: grid;
                grid-template-columns: 1fr 1fr;
                gap: 15px;
                margin-bottom: 20px;
            }
            
            .info-item {
                padding: 10px;
                background: #f8f9fa;
                border-radius: 4px;
            }
            
            .info-label {
                font-weight: bold;
                color: #666;
                font-size: 9pt;
                margin-bottom: 3px;
            }
            
            .info-value {
                font-size: 11pt;
                color: #000;
            }
            
            .stats-grid {
                display: grid;
                grid-template-columns: repeat(4, 1fr);
                gap: 15px;
                margin-bottom: 20px;
            }
            
            .stat-card {
                text-align: center;
                padding: 15px;
                background: #f8f9fa;
                border-radius: 8px;
                border-left: 4px solid #0d6efd;
            }
            
            .stat-value {
                font-size: 20pt;
                font-weight: bold;
                color: #0d6efd;
                margin-bottom: 5px;
            }
            
            .stat-label {
                font-size: 9pt;
                color: #666;
                text-transform: uppercase;
            }
            
            .score-grid {
                display: grid;
                grid-template-columns: repeat(2, 1fr);
                gap: 10px;
                margin-bottom: 20px;
            }
            
            .score-item {
                display: flex;
                justify-content: space-between;
                align-items: center;
                padding: 10px;
                background: #f8f9fa;
                border-radius: 4px;
            }
            
            .score-bar {
                width: 60%;
                height: 20px;
                background: #e9ecef;
                border-radius: 10px;
                overflow: hidden;
            }
            
            .score-fill {
                height: 100%;
                background: linear-gradient(90deg, #0d6efd, #0a58ca);
                transition: width 0.3s;
            }
            
            table {
                width: 100%;
                border-collapse: collapse;
                margin-bottom: 20px;
            }
            
            th, td {
                padding: 10px;
                text-align: left;
                border-bottom: 1px solid #dee2e6;
            }
            
            th {
                background: #f8f9fa;
                font-weight: bold;
                color: #0d6efd;
                font-size: 9pt;
                text-transform: uppercase;
            }
            
            td {
                font-size: 10pt;
            }
            
            .badge {
                display: inline-block;
                padding: 4px 8px;
                border-radius: 4px;
                font-size: 8pt;
                font-weight: bold;
                text-transform: uppercase;
            }
            
            .badge-success {
                background: #d1e7dd;
                color: #0f5132;
            }
            
            .badge-warning {
                background: #fff3cd;
                color: #856404;
            }
            
            .badge-danger {
                background: #f8d7da;
                color: #842029;
            }
            
            .badge-info {
                background: #cfe2ff;
                color: #084298;
            }
            
            .footer {
                margin-top: 40px;
                padding-top: 20px;
                border-top: 2px solid #e9ecef;
                text-align: center;
                font-size: 9pt;
                color: #666;
            }
            
            .signature-section {
                margin-top: 40px;
                display: grid;
                grid-template-columns: 1fr 1fr;
                gap: 40px;
            }
            
            .signature-box {
                padding: 20px;
                border: 1px solid #dee2e6;
                border-radius: 4px;
            }
            
            .signature-line {
                margin-top: 40px;
                border-top: 1px solid #000;
                padding-top: 5px;
                text-align: center;
                font-size: 9pt;
            }
        """
