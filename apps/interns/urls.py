from __future__ import annotations

from django.urls import path

from apps.interns import views

app_name = "interns"

urlpatterns = [
    path("", views.intern_list, name="list"),
    path("<int:intern_id>/", views.intern_detail, name="detail"),
]
