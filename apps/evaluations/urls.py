from __future__ import annotations

from django.urls import path

from apps.evaluations.views import (
    assess_intern,
    assessment_list,
    create_assessment,
    my_assessments,
    self_assessment,
    view_assessment,
)

app_name = "evaluations"

urlpatterns = [
    # Intern views
    path("my/", my_assessments, name="my_assessments"),
    path("<int:assessment_id>/self-assess/", self_assessment, name="self_assessment"),
    # Supervisor/Manager views
    path("list/", assessment_list, name="assessment_list"),
    path("intern/<int:intern_id>/create/", create_assessment, name="create_assessment"),
    path("<int:assessment_id>/assess/", assess_intern, name="assess_intern"),
    path("<int:assessment_id>/view/", view_assessment, name="view_assessment"),
]
