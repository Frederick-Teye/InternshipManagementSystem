from django.contrib import admin

from apps.holidays.models import Holiday


@admin.register(Holiday)
class HolidayAdmin(admin.ModelAdmin):
    list_display = ("name", "date", "branch", "is_full_day")
    list_filter = ("branch", "is_full_day")
    search_fields = ("name", "description", "branch__name")
