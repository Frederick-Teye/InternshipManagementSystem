from django.contrib import admin

from apps.branches.models import Branch, BranchEmployeeAssignment


@admin.register(Branch)
class BranchAdmin(admin.ModelAdmin):
    list_display = ("name", "code", "city", "country", "proximity_threshold_meters")
    search_fields = ("name", "code", "city", "country")


@admin.register(BranchEmployeeAssignment)
class BranchEmployeeAssignmentAdmin(admin.ModelAdmin):
    list_display = ("branch", "employee", "role", "is_primary", "active")
    list_filter = ("role", "active", "branch")
    search_fields = (
        "branch__name",
        "branch__code",
        "employee__user__first_name",
        "employee__user__last_name",
        "employee__user__email",
    )
