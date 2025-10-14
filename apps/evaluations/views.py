from __future__ import annotations

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from apps.accounts.decorators import intern_required, supervisor_or_above
from apps.evaluations.forms import (
    CreateAssessmentForm,
    InternSelfAssessmentForm,
    SupervisorAssessmentForm,
)
from apps.evaluations.models import PerformanceAssessment
from apps.interns.models import InternProfile
from apps.supervisors.models import EmployeeProfile


@login_required
@intern_required
def my_assessments(request):
    """Intern views their own performance assessments."""
    intern_profile = get_object_or_404(InternProfile, user=request.user)
    assessments = PerformanceAssessment.objects.filter(intern=intern_profile).order_by(
        "-week_number"
    )

    # Calculate statistics
    total_assessments = assessments.count()
    completed_count = assessments.filter(status="reviewed").count()
    pending_count = assessments.filter(status__in=["draft", "submitted"]).count()
    reviewed_count = assessments.filter(
        status="reviewed", supervisor_score__isnull=False
    ).count()

    # Calculate average score
    average_score = None
    if reviewed_count > 0:
        total_score = sum(
            [
                a.supervisor_score
                for a in assessments.filter(supervisor_score__isnull=False)
            ]
        )
        average_score = total_score / reviewed_count

    return render(
        request,
        "evaluations/my_assessments.html",
        {
            "assessments": assessments,
            "total_assessments": total_assessments,
            "completed_count": completed_count,
            "pending_count": pending_count,
            "reviewed_count": reviewed_count,
            "average_score": average_score,
        },
    )


@login_required
@intern_required
def self_assessment(request, assessment_id):
    """View for intern to complete self-assessment"""
    assessment = get_object_or_404(
        PerformanceAssessment, id=assessment_id, intern__user=request.user
    )

    if request.method == "POST":
        form = InternSelfAssessmentForm(request.POST, instance=assessment)
        if form.is_valid():
            form.save()
            messages.success(request, "✓ Self-assessment submitted successfully!")
            return redirect("evaluations:my_assessments")
    else:
        form = InternSelfAssessmentForm(instance=assessment)

    context = {
        "form": form,
        "assessment": assessment,
    }
    return render(request, "evaluations/self_assessment.html", context)


@login_required
@supervisor_or_above
def assessment_list(request):
    """Supervisor/Manager views all assessments they can access."""
    from apps.accounts.models import User

    # Role-based filtering
    if request.user.is_superuser or request.user.role in [
        User.Roles.MANAGER,
        User.Roles.ADMIN,
    ]:
        # Superusers/Managers/admins see all assessments
        all_assessments = PerformanceAssessment.objects.all()
        my_interns = InternProfile.objects.all()
    else:
        # Supervisors see only their interns
        # Get employee profile for supervisors
        employee_profile = get_object_or_404(EmployeeProfile, user=request.user)
        all_assessments = PerformanceAssessment.objects.filter(
            assessed_by=employee_profile
        )
        my_interns = InternProfile.objects.filter(internal_supervisor=employee_profile)

    # Filter by status if requested
    status_filter = request.GET.get("status", "all")
    if status_filter and status_filter != "all":
        assessments = all_assessments.filter(status=status_filter)
    else:
        assessments = all_assessments

    assessments = assessments.select_related(
        "intern__user", "assessed_by__user"
    ).order_by("-week_number")

    # Count by status
    total_count = all_assessments.count()
    draft_count = all_assessments.filter(status="draft").count()
    submitted_count = all_assessments.filter(status="submitted").count()
    reviewed_count = all_assessments.filter(status="reviewed").count()

    return render(
        request,
        "evaluations/assessment_list.html",
        {
            "assessments": assessments,
            "my_interns": my_interns,
            "status_filter": status_filter,
            "total_count": total_count,
            "draft_count": draft_count,
            "submitted_count": submitted_count,
            "reviewed_count": reviewed_count,
        },
    )


@login_required
@supervisor_or_above
def create_assessment(request, intern_id):
    """Create a new assessment for an intern"""
    from apps.accounts.models import User

    intern_profile = get_object_or_404(InternProfile, id=intern_id)

    # Check permission
    if not request.user.is_superuser and request.user.role not in [
        User.Roles.MANAGER,
        User.Roles.ADMIN,
    ]:
        try:
            employee_profile = EmployeeProfile.objects.get(user=request.user)
            if intern_profile not in employee_profile.assigned_interns.all():
                messages.error(
                    request,
                    "You can only create assessments for your assigned interns.",
                )
                return redirect("evaluations:assessment_list")
        except EmployeeProfile.DoesNotExist:
            messages.error(request, "You do not have permission to create assessments.")
            return redirect("evaluations:assessment_list")

    if request.method == "POST":
        form = CreateAssessmentForm(request.POST)
        if form.is_valid():
            assessment = form.save(commit=False)
            assessment.intern = intern_profile

            try:
                employee_profile = EmployeeProfile.objects.get(user=request.user)
                assessment.assessed_by = employee_profile
            except EmployeeProfile.DoesNotExist:
                pass

            assessment.assessment_date = timezone.localdate()
            assessment.status = PerformanceAssessment.Status.DRAFT

            try:
                assessment.save()
                messages.success(
                    request,
                    f"✓ Assessment created for {intern_profile.user.get_full_name()}",
                )
                return redirect(
                    "evaluations:assess_intern", assessment_id=assessment.id
                )
            except Exception as e:
                messages.error(request, f"Error creating assessment: {str(e)}")
    else:
        # Auto-calculate next week number
        last_assessment = (
            PerformanceAssessment.objects.filter(intern=intern_profile)
            .order_by("-week_number")
            .first()
        )

        next_week = (last_assessment.week_number + 1) if last_assessment else 1
        form = CreateAssessmentForm(initial={"week_number": next_week})

    context = {
        "form": form,
        "intern_profile": intern_profile,
    }
    return render(request, "evaluations/create_assessment.html", context)


@login_required
@supervisor_or_above
def assess_intern(request, assessment_id):
    """View for supervisor to assess an intern"""
    from apps.accounts.models import User

    assessment = get_object_or_404(PerformanceAssessment, id=assessment_id)

    # Check permission
    if not request.user.is_superuser and request.user.role not in [
        User.Roles.MANAGER,
        User.Roles.ADMIN,
    ]:
        try:
            employee_profile = EmployeeProfile.objects.get(user=request.user)
            if assessment.intern not in employee_profile.assigned_interns.all():
                messages.error(request, "You can only assess your assigned interns.")
                return redirect("evaluations:assessment_list")
        except EmployeeProfile.DoesNotExist:
            messages.error(request, "You do not have permission to assess interns.")
            return redirect("evaluations:assessment_list")

    if request.method == "POST":
        form = SupervisorAssessmentForm(request.POST, instance=assessment)
        if form.is_valid():
            form.save()
            messages.success(
                request,
                f"✓ Assessment completed for {assessment.intern.user.get_full_name()}",
            )
            return redirect("evaluations:assessment_list")
    else:
        form = SupervisorAssessmentForm(instance=assessment)

    context = {
        "form": form,
        "assessment": assessment,
    }
    return render(request, "evaluations/assess_intern.html", context)


@login_required
def view_assessment(request, assessment_id):
    """View detailed assessment with both perspectives."""
    from apps.accounts.models import User

    assessment = get_object_or_404(PerformanceAssessment, id=assessment_id)

    # Permission check and determine if user can assess
    can_assess = False
    if request.user.role == User.Roles.INTERN:
        # Interns can only view their own
        if assessment.intern.user != request.user:
            return HttpResponseForbidden("You cannot view this assessment.")
    elif request.user.role == User.Roles.SUPERVISOR:
        # Supervisors can only view their interns
        employee_profile = get_object_or_404(EmployeeProfile, user=request.user)
        if assessment.assessed_by != employee_profile:
            return HttpResponseForbidden("You cannot view this assessment.")
        can_assess = True
    elif request.user.is_superuser or request.user.role in [
        User.Roles.MANAGER,
        User.Roles.ADMIN,
    ]:
        # Superusers/Managers and admins can view all
        can_assess = True

    return render(
        request,
        "evaluations/view_assessment.html",
        {
            "assessment": assessment,
            "can_assess": can_assess,
        },
    )
