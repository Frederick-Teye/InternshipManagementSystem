from django.contrib import admin

from apps.schools.models import AcademicSupervisor, School


@admin.register(School)
class SchoolAdmin(admin.ModelAdmin):
    list_display = ("name", "city", "country", "contact_email")
    search_fields = ("name", "city", "country")


@admin.register(AcademicSupervisor)
class AcademicSupervisorAdmin(admin.ModelAdmin):
    list_display = ("first_name", "last_name", "email", "school", "is_active")
    list_filter = ("school", "is_active")
    search_fields = ("first_name", "last_name", "email", "school__name")
