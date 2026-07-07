from django.contrib import admin

from .models import Project, ProjectTeam


class ProjectTeamInline(admin.TabularInline):
    model = ProjectTeam
    extra = 1
    autocomplete_fields = ("team",)


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ("name", "company", "status", "start_date", "due_date", "created_by", "created_at")
    list_filter = ("status", "company", "start_date", "due_date", "created_at")
    search_fields = ("name", "company__name", "description")
    autocomplete_fields = ("company", "created_by")
    inlines = [ProjectTeamInline]


@admin.register(ProjectTeam)
class ProjectTeamAdmin(admin.ModelAdmin):
    list_display = ("project", "team", "assigned_at")
    list_filter = ("project", "team", "assigned_at")
    search_fields = ("project__name", "team__name")
    autocomplete_fields = ("project", "team")