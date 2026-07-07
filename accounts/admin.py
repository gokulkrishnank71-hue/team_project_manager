from django.contrib import admin

from .models import UserProfile


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ("full_name", "user", "company", "system_role", "job_role", "must_change_password", "created_at")
    list_filter = ("system_role", "job_role", "must_change_password", "company")
    search_fields = ("full_name", "user__username", "user__email", "phone")
    autocomplete_fields = ("user", "company")