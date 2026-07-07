from django.contrib import admin

from .models import Team, TeamMember


class TeamMemberInline(admin.TabularInline):
    model = TeamMember
    extra = 1
    autocomplete_fields = ("user",)


@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ("name", "company", "created_by", "created_at")
    list_filter = ("company", "created_at")
    search_fields = ("name", "company__name", "description")
    autocomplete_fields = ("company", "created_by")
    inlines = [TeamMemberInline]


@admin.register(TeamMember)
class TeamMemberAdmin(admin.ModelAdmin):
    list_display = ("team", "user", "team_role", "joined_at")
    list_filter = ("team_role", "team", "joined_at")
    search_fields = ("team__name", "user__username", "user__email")
    autocomplete_fields = ("team", "user")