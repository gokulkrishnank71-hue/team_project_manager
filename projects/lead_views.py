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


def project_status_text(project):
    return project.get_status_display()


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


def lead_projects_queryset(user):
    return (
        Project.objects.filter(
            assigned_teams__team__memberships__user=user,
            assigned_teams__team__memberships__team_role=TeamMember.TeamRole.LEAD,
        )
        .distinct()
        .prefetch_related("tasks", "assigned_teams__team__memberships__user")
    )


def get_lead_project(user, project_id):
    return get_object_or_404(lead_projects_queryset(user), id=project_id)


def project_team_name(project):
    teams = [item.team.name for item in project.assigned_teams.all()]
    return ", ".join(teams) if teams else "No team assigned"


def project_member_users(project):
    users = []
    seen = set()
    for project_team in project.assigned_teams.all():
        for membership in project_team.team.memberships.all():
            if membership.user_id not in seen:
                seen.add(membership.user_id)
                users.append(membership.user)
    return users


def project_progress(project):
    total = project.tasks.count()
    if total == 0:
        return 0
    done = project.tasks.filter(status=Task.Status.DONE).count()
    return round((done / total) * 100)


@login_required
def lead_assigned_projects(request):
    projects = []
    for project in lead_projects_queryset(request.user):
        projects.append(
            {
                "id": project.id,
                "name": project.name,
                "team_name": project_team_name(project),
                "status": project_status_text(project),
                "status_class": project_status_class(project),
                "due_date": date_text(project.due_date),
                "task_count": project.tasks.count(),
                "member_count": len(project_member_users(project)),
                "progress": project_progress(project),
            }
        )

    return render(
        request,
        "lead/assigned_projects.html",
        {
            "projects": projects,
            "lead_name": user_name(request.user),
        },
    )


@login_required
def lead_project_workspace(request, project_id):
    project = get_lead_project(request.user, project_id)
    context = {
        "project": {
            "id": project.id,
            "name": project.name,
            "team_name": project_team_name(project),
            "status": project_status_text(project),
            "due_date": date_text(project.due_date),
            "task_count": project.tasks.count(),
            "in_progress_count": project.tasks.filter(status=Task.Status.IN_PROGRESS).count(),
            "completed_count": project.tasks.filter(status=Task.Status.DONE).count(),
            "member_count": len(project_member_users(project)),
            "progress": project_progress(project),
        }
    }
    return render(request, "lead/project_workspace.html", context)


@login_required
def lead_project_tasks(request, project_id):
    project = get_lead_project(request.user, project_id)

    members = [{"name": user_name(user)} for user in project_member_users(project) if user != request.user]

    tasks = [
        {
            "title": task.title,
            "assignee": user_name(task.assigned_to),
            "due_date": date_text(task.due_date),
            "status": task.get_status_display(),
            "status_class": task_status_class(task),
        }
        for task in project.tasks.select_related("assigned_to").all()
    ]

    return render(
        request,
        "lead/tasks.html",
        {
            "project": {"id": project.id, "name": project.name},
            "members": members,
            "tasks": tasks,
        },
    )


@login_required
def lead_project_members(request, project_id):
    project = get_lead_project(request.user, project_id)

    members = []
    for user in project_member_users(project):
        assigned_tasks = project.tasks.filter(assigned_to=user)
        full_name = user_name(user)
        members.append(
            {
                "initial": full_name[:1].upper(),
                "name": full_name,
                "job_role": user.profile.get_job_role_display() if hasattr(user, "profile") and user.profile.job_role else "Staff",
                "total_tasks": assigned_tasks.count(),
                "in_progress": assigned_tasks.filter(status=Task.Status.IN_PROGRESS).count(),
                "completed": assigned_tasks.filter(status=Task.Status.DONE).count(),
                "progress": 0 if assigned_tasks.count() == 0 else round((assigned_tasks.filter(status=Task.Status.DONE).count() / assigned_tasks.count()) * 100),
            }
        )

    return render(
        request,
        "lead/members.html",
        {
            "project": {"id": project.id, "name": project.name},
            "members": members,
        },
    )


@login_required
def lead_project_status(request, project_id):
    project = get_lead_project(request.user, project_id)
    total_tasks = project.tasks.count()
    completed_tasks = project.tasks.filter(status=Task.Status.DONE).count()

    context = {
        "project": {
            "id": project.id,
            "name": project.name,
            "status": project_status_text(project),
            "progress": project_progress(project),
            "total_tasks": total_tasks,
            "completed_tasks": completed_tasks,
            "remaining_tasks": total_tasks - completed_tasks,
            "due_date": date_text(project.due_date),
        }
    }
    return render(request, "lead/project_status.html", context)


@login_required
def lead_project_activity(request, project_id):
    project = get_lead_project(request.user, project_id)
    activities = [
        {
            "title": item.action,
            "detail": item.message,
            "time": item.created_at.strftime("%d %b %Y %I:%M %p"),
        }
        for item in ActivityLog.objects.filter(project=project).order_by("-created_at")[:20]
    ]

    return render(
        request,
        "lead/activity.html",
        {
            "project": {"id": project.id, "name": project.name},
            "activities": activities,
        },
    )


@login_required
def lead_profile(request, project_id):
    project = get_lead_project(request.user, project_id)
    profile = getattr(request.user, "profile", None)

    lead = {
        "name": user_name(request.user),
        "email": request.user.email,
        "team_role": "Lead",
        "job_role": profile.get_job_role_display() if profile and profile.job_role else "Staff",
        "company": project.company.name,
    }

    return render(
        request,
        "lead/profile.html",
        {
            "project": {"id": project.id, "name": project.name},
            "lead": lead,
        },
    )