from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render

from activity.models import ActivityLog
from projects.models import Project
from tasks.models import Task
from teams.models import TeamMember


def user_name(user):
    if not user:
        return "Unassigned"
    if hasattr(user, "profile") and user.profile.full_name:
        return user.profile.full_name
    return user.get_full_name() or user.username


def date_text(value):
    return value.strftime("%d %b %Y") if value else "-"


def project_status_class(project):
    return {
        "NOT_STARTED": "pending",
        "IN_PROGRESS": "active",
        "ON_HOLD": "pending",
        "COMPLETED": "completed",
    }.get(project.status, "pending")


def task_status_class(task):
    return {
        "TODO": "pending",
        "IN_PROGRESS": "active",
        "DONE": "completed",
    }.get(task.status, "pending")


def member_projects_queryset(user):
    return (
        Project.objects.filter(
            assigned_teams__team__memberships__user=user,
            assigned_teams__team__memberships__team_role=TeamMember.TeamRole.MEMBER,
        )
        .distinct()
        .prefetch_related("tasks", "assigned_teams__team__memberships__user")
    )


def get_member_project(user, project_id):
    return get_object_or_404(member_projects_queryset(user), id=project_id)


def project_team_name(project, user=None):
    if user:
        teams = [
            item.team.name
            for item in project.assigned_teams.all()
            if item.team.memberships.filter(user=user).exists()
        ]
    else:
        teams = [item.team.name for item in project.assigned_teams.all()]
    return ", ".join(teams) if teams else "No team assigned"


def project_lead_name(project):
    for project_team in project.assigned_teams.all():
        lead_membership = project_team.team.memberships.filter(team_role=TeamMember.TeamRole.LEAD).select_related("user").first()
        if lead_membership:
            return user_name(lead_membership.user)
    return "Not assigned"


def my_tasks_queryset(project, user):
    return project.tasks.filter(assigned_to=user)


def my_progress(project, user):
    tasks = my_tasks_queryset(project, user)
    total = tasks.count()
    if total == 0:
        return 0
    done = tasks.filter(status=Task.Status.DONE).count()
    return round((done / total) * 100)


@login_required
def member_assigned_projects(request):
    projects = []
    for project in member_projects_queryset(request.user):
        projects.append(
            {
                "id": project.id,
                "name": project.name,
                "team_name": project_team_name(project, request.user),
                "lead_name": project_lead_name(project),
                "status": project.get_status_display(),
                "status_class": project_status_class(project),
                "due_date": date_text(project.due_date),
                "my_task_count": my_tasks_queryset(project, request.user).count(),
                "my_progress": my_progress(project, request.user),
            }
        )

    return render(
        request,
        "member/assigned_projects.html",
        {
            "projects": projects,
            "member_name": user_name(request.user),
        },
    )


@login_required
def member_project_detail(request, project_id):
    project = get_member_project(request.user, project_id)
    my_tasks = my_tasks_queryset(project, request.user)

    context = {
        "project": {
            "id": project.id,
            "name": project.name,
            "team_name": project_team_name(project, request.user),
            "lead_name": project_lead_name(project),
            "status": project.get_status_display(),
            "due_date": date_text(project.due_date),
            "my_task_count": my_tasks.count(),
            "completed_tasks": my_tasks.filter(status=Task.Status.DONE).count(),
            "in_progress_tasks": my_tasks.filter(status=Task.Status.IN_PROGRESS).count(),
            "my_progress": my_progress(project, request.user),
        }
    }
    return render(request, "member/project_detail.html", context)


@login_required
def member_my_tasks(request, project_id):
    project = get_member_project(request.user, project_id)
    tasks = [
        {
            "id": task.id,
            "title": task.title,
            "due_date": date_text(task.due_date),
            "status": task.get_status_display(),
            "status_class": task_status_class(task),
        }
        for task in my_tasks_queryset(project, request.user)
    ]

    return render(
        request,
        "member/my_tasks.html",
        {
            "project": {"id": project.id, "name": project.name},
            "tasks": tasks,
        },
    )


@login_required
def member_task_detail(request, project_id, task_id):
    project = get_member_project(request.user, project_id)
    task = get_object_or_404(project.tasks.select_related("created_by"), id=task_id, assigned_to=request.user)

    context = {
        "project": {"id": project.id, "name": project.name},
        "task": {
            "id": task.id,
            "title": task.title,
            "description": task.description or "No description added.",
            "assigned_by": user_name(task.created_by),
            "due_date": date_text(task.due_date),
            "status": task.get_status_display(),
        },
    }
    return render(request, "member/task_detail.html", context)


@login_required
def member_activity(request, project_id):
    project = get_member_project(request.user, project_id)
    activities = [
        {
            "title": item.action,
            "detail": item.message,
            "time": item.created_at.strftime("%d %b %Y %I:%M %p"),
        }
        for item in ActivityLog.objects.filter(project=project, user=request.user).order_by("-created_at")[:20]
    ]

    return render(
        request,
        "member/activity.html",
        {
            "project": {"id": project.id, "name": project.name},
            "activities": activities,
        },
    )


@login_required
def member_profile(request, project_id):
    project = get_member_project(request.user, project_id)
    profile = getattr(request.user, "profile", None)

    member = {
        "name": user_name(request.user),
        "email": request.user.email,
        "company": project.company.name,
        "team": project_team_name(project, request.user),
        "team_role": "Member",
        "job_role": profile.get_job_role_display() if profile and profile.job_role else "Staff",
    }

    return render(
        request,
        "member/profile.html",
        {
            "project": {"id": project.id, "name": project.name},
            "member": member,
        },
    )