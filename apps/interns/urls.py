from __future__ import annotations

from django.urls import path

from apps.interns import views

app_name = "interns"

urlpatterns = [
    path("", views.intern_list, name="list"),
    path("<int:intern_id>/", views.intern_detail, name="detail"),
    # Emergency contact management
    path(
        "emergency-contacts/", views.my_emergency_contacts, name="my_emergency_contacts"
    ),
    path(
        "<int:intern_id>/emergency-contacts/",
        views.manage_emergency_contacts,
        name="manage_emergency_contacts",
    ),
]
