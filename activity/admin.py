from django.contrib import admin

from .models import ActivityLog


@admin.register(ActivityLog)
class ActivityLogAdmin(admin.ModelAdmin):
    list_display = ("action", "company", "project", "task", "user", "created_at")
    list_filter = ("company", "project", "task", "created_at")
    search_fields = ("action", "message", "user__username", "project__name", "task__title")
    autocomplete_fields = ("company", "project", "task", "user")