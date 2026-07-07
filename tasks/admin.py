from django.contrib import admin

from .models import Task, TaskComment


class TaskCommentInline(admin.TabularInline):
    model = TaskComment
    extra = 1
    autocomplete_fields = ("user",)


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ("title", "project", "assigned_to", "status", "priority", "due_date", "created_by", "created_at")
    list_filter = ("status", "priority", "project", "due_date", "created_at")
    search_fields = ("title", "project__name", "assigned_to__username", "assigned_to__email")
    autocomplete_fields = ("project", "assigned_to", "created_by")
    inlines = [TaskCommentInline]


@admin.register(TaskComment)
class TaskCommentAdmin(admin.ModelAdmin):
    list_display = ("task", "user", "created_at")
    list_filter = ("created_at",)
    search_fields = ("task__title", "user__username", "comment")
    autocomplete_fields = ("task", "user")