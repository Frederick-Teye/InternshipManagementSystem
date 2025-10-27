from __future__ import annotations

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Avg, Count, Q
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from apps.accounts.decorators import supervisor_or_above
from apps.absenteeism.models import AbsenteeismRequest
from apps.attendance.models import Attendance
from apps.evaluations.models import PerformanceAssessment
from apps.interns.forms import EmergencyContactForm, InternProfileForm
from apps.interns.models import InternProfile


@login_required
@supervisor_or_above
def intern_list(request):
    """View all interns with search and filtering"""
    interns = InternProfile.objects.select_related(
        "user", "school", "branch", "internal_supervisor__user"
    ).all()

    # Search functionality
    search_query = request.GET.get("search", "")
    if search_query:
        interns = interns.filter(
            Q(user__first_name__icontains=search_query)
            | Q(user__last_name__icontains=search_query)
            | Q(user__email__icontains=search_query)
            | Q(school__name__icontains=search_query)
            | Q(branch__name__icontains=search_query)
        )

    # Filter by status
    status_filter = request.GET.get("status", "all")
    if status_filter == "active":
        interns = interns.filter(
            start_date__lte=timezone.now().date(),
            end_date__gte=timezone.now().date(),
        )
    elif status_filter == "completed":
        interns = interns.filter(end_date__lt=timezone.now().date())
    elif status_filter == "upcoming":
        interns = interns.filter(start_date__gt=timezone.now().date())

    # Filter by branch
    branch_filter = request.GET.get("branch", "")
    if branch_filter:
        interns = interns.filter(branch_id=branch_filter)

    # Filter by school
    school_filter = request.GET.get("school", "")
    if school_filter:
        interns = interns.filter(school_id=school_filter)

    # Annotate with statistics
    interns = interns.annotate(
        total_assessments=Count("assessments"),
        avg_score=Avg("assessments__supervisor_score"),
        total_attendance=Count("attendances"),
        approved_attendance=Count(
            "attendances", filter=Q(attendances__approval_status="approved")
        ),
    )

    # Get unique branches and schools for filters
    from apps.branches.models import Branch
    from apps.schools.models import School

    branches = Branch.objects.all()
    schools = School.objects.all()

    context = {
        "interns": interns.order_by("-start_date"),
        "search_query": search_query,
        "status_filter": status_filter,
        "branch_filter": branch_filter,
        "school_filter": school_filter,
        "branches": branches,
        "schools": schools,
        "total_count": interns.count(),
    }

    return render(request, "interns/intern_list.html", context)


@login_required
@supervisor_or_above
def intern_detail(request, intern_id):
    """View detailed intern profile with complete history"""
    from django.utils import timezone

    intern = get_object_or_404(
        InternProfile.objects.select_related(
            "user",
            "school",
            "branch",
            "internal_supervisor__user",
            "academic_supervisor",
        ),
        id=intern_id,
    )

    # Get all assessments
    assessments = (
        PerformanceAssessment.objects.filter(intern=intern)
        .select_related("assessed_by__user")
        .order_by("-week_number")
    )

    # Assessment statistics
    total_assessments = assessments.count()
    avg_supervisor_score = assessments.aggregate(Avg("supervisor_score"))[
        "supervisor_score__avg"
    ]
    avg_self_score = assessments.aggregate(Avg("intern_score"))["intern_score__avg"]

    # Get all attendance records
    attendance_records = (
        Attendance.objects.filter(intern=intern)
        .select_related("branch", "approved_by")
        .order_by("-check_in_time")
    )

    # Attendance statistics
    total_attendance = attendance_records.count()
    approved_attendance = attendance_records.filter(approval_status="approved").count()
    pending_attendance = attendance_records.filter(approval_status="pending").count()
    rejected_attendance = attendance_records.filter(approval_status="rejected").count()

    # Calculate attendance rate
    attendance_rate = (
        (approved_attendance / total_attendance * 100) if total_attendance > 0 else 0
    )

    # Get absence requests
    absence_requests = (
        AbsenteeismRequest.objects.filter(intern=intern)
        .select_related("approver")
        .order_by("-submitted_at")
    )

    # Absence statistics
    total_absences = absence_requests.count()
    approved_absences = absence_requests.filter(status="approved").count()
    pending_absences = absence_requests.filter(status="pending").count()
    rejected_absences = absence_requests.filter(status="rejected").count()

    # Check if internship is active
    today = timezone.now().date()
    is_active = False
    is_completed = False
    is_upcoming = False
    total_days = None
    days_completed = None
    days_remaining = None

    if intern.start_date and intern.end_date:
        is_active = intern.start_date <= today <= intern.end_date
        is_completed = intern.end_date < today
        is_upcoming = intern.start_date > today

        # Duration calculation
        total_days = (intern.end_date - intern.start_date).days

        if is_active:
            days_completed = (today - intern.start_date).days
            days_remaining = (intern.end_date - today).days
        elif is_upcoming:
            days_remaining = (intern.start_date - today).days

    context = {
        "intern": intern,
        "is_active": is_active,
        "is_completed": is_completed,
        "is_upcoming": is_upcoming,
        # Assessment data
        "assessments": assessments[:10],  # Show last 10
        "total_assessments": total_assessments,
        "avg_supervisor_score": avg_supervisor_score,
        "avg_self_score": avg_self_score,
        # Attendance data
        "attendance_records": attendance_records[:10],  # Show last 10
        "total_attendance": total_attendance,
        "approved_attendance": approved_attendance,
        "pending_attendance": pending_attendance,
        "rejected_attendance": rejected_attendance,
        "attendance_rate": attendance_rate,
        # Absence data
        "absence_requests": absence_requests[:10],  # Show last 10
        "total_absences": total_absences,
        "approved_absences": approved_absences,
        "pending_absences": pending_absences,
        "rejected_absences": rejected_absences,
        # Duration
        "total_days": total_days,
        "days_completed": days_completed,
        "days_remaining": days_remaining,
    }

    return render(request, "interns/intern_detail.html", context)


@login_required
def my_emergency_contacts(request):
    """View for interns to manage their emergency contact information"""
    intern_profile = get_object_or_404(InternProfile, user=request.user)

    if request.method == "POST":
        form = EmergencyContactForm(request.POST, instance=intern_profile)
        if form.is_valid():
            form.save()
            messages.success(
                request,
                "Your emergency contact information has been updated successfully.",
            )
            return redirect("interns:my_emergency_contacts")
    else:
        form = EmergencyContactForm(instance=intern_profile)

    context = {
        "form": form,
        "intern_profile": intern_profile,
    }

    return render(request, "interns/emergency_contacts.html", context)


@login_required
@supervisor_or_above
def manage_emergency_contacts(request, intern_id):
    """View for supervisors/admins to manage intern emergency contact information"""
    intern_profile = get_object_or_404(
        InternProfile.objects.select_related("user"), id=intern_id
    )

    if request.method == "POST":
        form = EmergencyContactForm(request.POST, instance=intern_profile)
        if form.is_valid():
            form.save()
            messages.success(
                request,
                f"Emergency contact information for {intern_profile.user.get_full_name()} has been updated successfully.",
            )
            return redirect("interns:manage_emergency_contacts", intern_id=intern_id)
    else:
        form = EmergencyContactForm(instance=intern_profile)

    context = {
        "form": form,
        "intern_profile": intern_profile,
    }

    return render(request, "interns/manage_emergency_contacts.html", context)
