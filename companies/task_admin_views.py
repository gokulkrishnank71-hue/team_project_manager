from datetime import date

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from activity.models import ActivityLog
from tasks.models import Task
from .views import (
    date_text,
    get_project,
    get_project_teams,
    selected_project_context,
    user_name,
)


def project_member_users(project):
    users = []
    seen = set()

    for team in get_project_teams(project):
        for membership in team.memberships.select_related("user", "user__profile"):
            if membership.user_id in seen:
                continue
            seen.add(membership.user_id)
            users.append(membership.user)

    return users


def get_assignee(project, user_id):
    if not user_id:
        return None

    for user in project_member_users(project):
        if str(user.id) == str(user_id):
            return user

    return None


def clean_choice(value, choices, default):
    valid_values = [choice[0] for choice in choices]
    return value if value in valid_values else default


def clean_due_date(value):
    if not value:
        return None

    try:
        return date.fromisoformat(value)
    except ValueError:
        return None


def create_activity(project, user, action, message):
    ActivityLog.objects.create(
        company=project.company,
        project=project,
        user=user,
        action=action,
        message=message,
    )


def task_context(project):
    tasks = project.tasks.select_related("assigned_to")
    members = project_member_users(project)

    return {
        **selected_project_context(project, "tasks"),
        "task_stats": [
            {"label": "Total Tasks", "value": tasks.count(), "color": "blue"},
            {"label": "To Do", "value": tasks.filter(status=Task.Status.TODO).count(), "color": "orange"},
            {"label": "In Progress", "value": tasks.filter(status=Task.Status.IN_PROGRESS).count(), "color": "pink"},
            {"label": "Done", "value": tasks.filter(status=Task.Status.DONE).count(), "color": "green"},
        ],
        "task_actions": [
            "Create task",
            "Assign task to project member",
            "Update task details",
            "Update task status",
            "Update task priority",
            "Delete task",
        ],
        "members": [{"id": user.id, "name": user_name(user)} for user in members],
        "status_choices": Task.Status.choices,
        "priority_choices": Task.Priority.choices,
        "tasks": [
            {
                "id": task.id,
                "title": task.title,
                "description": task.description,
                "assigned_to_id": task.assigned_to_id,
                "member": user_name(task.assigned_to),
                "status": task.get_status_display(),
                "status_value": task.status,
                "priority": task.get_priority_display(),
                "priority_value": task.priority,
                "due": date_text(task.due_date),
                "due_value": task.due_date.isoformat() if task.due_date else "",
            }
            for task in tasks
        ],
    }


@login_required
def project_task_monitoring(request, project_id):
    project = get_project(request, project_id)
    return render(request, "company_admin/task_monitoring.html", task_context(project))


@login_required
def project_task_create(request, project_id):
    project = get_project(request, project_id)

    if request.method != "POST":
        return redirect("company_admin_project_tasks", project_id=project.id)

    title = request.POST.get("title", "").strip()
    if not title:
        messages.error(request, "Task title is required.")
        return redirect("company_admin_project_tasks", project_id=project.id)

    assignee_id = request.POST.get("assigned_to")
    assigned_to = get_assignee(project, assignee_id)

    if assignee_id and not assigned_to:
        messages.error(request, "Selected assignee is not part of this project.")
        return redirect("company_admin_project_tasks", project_id=project.id)

    task = Task.objects.create(
        project=project,
        assigned_to=assigned_to,
        created_by=request.user,
        title=title,
        description=request.POST.get("description", "").strip(),
        status=clean_choice(request.POST.get("status"), Task.Status.choices, Task.Status.TODO),
        priority=clean_choice(request.POST.get("priority"), Task.Priority.choices, Task.Priority.MEDIUM),
        due_date=clean_due_date(request.POST.get("due_date")),
    )

    create_activity(
        project,
        request.user,
        "Task created",
        f'"{task.title}" was created and assigned to {user_name(assigned_to)}.',
    )
    messages.success(request, "Task created successfully.")
    return redirect("company_admin_project_tasks", project_id=project.id)


@login_required
def project_task_update(request, project_id, task_id):
    project = get_project(request, project_id)
    task = get_object_or_404(project.tasks, id=task_id)

    if request.method != "POST":
        return redirect("company_admin_project_tasks", project_id=project.id)

    title = request.POST.get("title", "").strip()
    if not title:
        messages.error(request, "Task title is required.")
        return redirect("company_admin_project_tasks", project_id=project.id)

    assignee_id = request.POST.get("assigned_to")
    assigned_to = get_assignee(project, assignee_id)

    if assignee_id and not assigned_to:
        messages.error(request, "Selected assignee is not part of this project.")
        return redirect("company_admin_project_tasks", project_id=project.id)

    task.title = title
    task.description = request.POST.get("description", "").strip()
    task.assigned_to = assigned_to
    task.status = clean_choice(request.POST.get("status"), Task.Status.choices, task.status)
    task.priority = clean_choice(request.POST.get("priority"), Task.Priority.choices, task.priority)
    task.due_date = clean_due_date(request.POST.get("due_date"))
    task.save()

    create_activity(
        project,
        request.user,
        "Task updated",
        f'"{task.title}" was updated by {user_name(request.user)}.',
    )
    messages.success(request, "Task updated successfully.")
    return redirect("company_admin_project_tasks", project_id=project.id)


@login_required
def project_task_delete(request, project_id, task_id):
    project = get_project(request, project_id)
    task = get_object_or_404(project.tasks, id=task_id)

    if request.method != "POST":
        return redirect("company_admin_project_tasks", project_id=project.id)

    task_title = task.title
    task.delete()

    create_activity(
        project,
        request.user,
        "Task deleted",
        f'"{task_title}" was deleted by {user_name(request.user)}.',
    )
    messages.success(request, "Task deleted successfully.")
    return redirect("company_admin_project_tasks", project_id=project.id)