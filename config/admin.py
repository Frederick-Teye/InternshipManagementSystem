from __future__ import annotations

from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html


class CustomAdminSite(admin.AdminSite):
    site_header = "Internship Management System Admin"
    site_title = "IMS Admin"
    index_title = "Welcome to IMS Administration"

    def get_app_list(self, request):
        app_list = super().get_app_list(request)

        # Add a custom "System" app with log files
        system_app = {
            "name": "System",
            "app_label": "system",
            "app_url": "#",
            "has_module_perms": True,
            "models": [
                {
                    "name": "Log Files",
                    "object_name": "LogFile",
                    "perms": {
                        "add": False,
                        "change": False,
                        "delete": False,
                        "view": True,
                    },
                    "admin_url": reverse("admin_logs:log_files_list"),
                    "add_url": None,
                    "view_only": True,
                }
            ],
        }

        # Insert the system app at the beginning
        app_list.insert(0, system_app)
        return app_list


# Create the custom admin site
admin_site = CustomAdminSite(name="admin")
admin.site = admin_site

# Register all existing models with the custom admin site
from django.contrib.auth.admin import UserAdmin, GroupAdmin
from django.contrib.auth.models import User, Group

admin_site.register(User, UserAdmin)
admin_site.register(Group, GroupAdmin)

# Register app models
from apps.accounts.admin import *
from apps.interns.admin import *
from apps.schools.admin import *
from apps.supervisors.admin import *
from apps.branches.admin import *
from apps.evaluations.admin import *
from apps.attendance.admin import *
from apps.absenteeism.admin import *
from apps.holidays.admin import *
from apps.notifications.admin import *
from apps.reports.admin import *
