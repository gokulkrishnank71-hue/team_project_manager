from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.timesince import timesince

from activity.models import ActivityLog
from companies.models import Company
from projects.models import Project
from tasks.models import Task
from teams.models import TeamMember


def get_company(request):
    if hasattr(request.user, "profile") and request.user.profile.company:
        return request.user.profile.company
    return Company.objects.first()


def user_name(user):
    if not user:
        return "Unassigned"
    if hasattr(user, "profile") and user.profile.full_name:
        return user.profile.full_name
    return user.get_full_name() or user.username


def date_text(value):
    return value.strftime("%d %b %Y") if value else "-"


def project_status_class(status):
    return {
        Project.Status.NOT_STARTED: "pending",
        Project.Status.IN_PROGRESS: "active",
        Project.Status.ON_HOLD: "hold",
        Project.Status.COMPLETED: "completed",
    }.get(status, "pending")


def get_project_teams(project):
    return [project_team.team for project_team in project.assigned_teams.all()]


def get_project_team_name(project):
    teams = get_project_teams(project)
    return ", ".join(team.name for team in teams) if teams else "No team assigned"


def get_project_lead(project):
    for team in get_project_teams(project):
        for membership in team.memberships.all():
            if membership.team_role == TeamMember.TeamRole.LEAD:
                return user_name(membership.user)
    return "Not assigned"


def get_project_members(project):
    rows = []
    added_users = set()

    for team in get_project_teams(project):
        for membership in team.memberships.all():
            if membership.user_id in added_users:
                continue

            added_users.add(membership.user_id)
            profile = getattr(membership.user, "profile", None)
            rows.append({
                "name": profile.full_name if profile else user_name(membership.user),
                "job_role": profile.get_job_role_display() if profile and profile.job_role else "Staff",
                "team_role": membership.get_team_role_display(),
                "team": team.name,
                "status": "Inactive" if not membership.user.is_active else "Active",
            })

    return rows


def get_project_progress(project):
    total_tasks = project.tasks.count()
    if total_tasks == 0:
        return 0
    done_tasks = project.tasks.filter(status=Task.Status.DONE).count()
    return round((done_tasks / total_tasks) * 100)


def project_card(project):
    return {
        "id": project.id,
        "name": project.name,
        "team_name": get_project_team_name(project),
        "status": project.get_status_display(),
        "status_class": project_status_class(project.status),
        "due_date": date_text(project.due_date),
        "task_count": project.tasks.count(),
        "member_count": len(get_project_members(project)),
        "progress": get_project_progress(project),
    }


def get_project(request, project_id):
    return get_object_or_404(
        Project.objects.prefetch_related(
            "tasks__assigned_to",
            "assigned_teams__team__memberships__user",
        ).select_related("company", "created_by"),
        id=project_id,
        company=get_company(request),
    )


def selected_project_context(project, active_page):
    return {
        "active_page": active_page,
        "selected_project": project,
        "project": project,
        "team_name": get_project_team_name(project),
        "lead_name": get_project_lead(project),
        "progress": get_project_progress(project),
        "status_class": project_status_class(project.status),
    }


@login_required
def company_admin_overview(request):
    return redirect("project_management")


@login_required
def project_management(request):
    company = get_company(request)
    projects = Project.objects.filter(company=company).prefetch_related(
        "tasks",
        "assigned_teams__team__memberships__user",
    )

    context = {
        "admin_name": user_name(request.user),
        "company": company,
        "projects": [project_card(project) for project in projects],
    }
    return render(request, "company_admin/project_management.html", context)


@login_required
def company_admin_project_detail(request, project_id):
    project = get_project(request, project_id)
    tasks = project.tasks.select_related("assigned_to")
    members = get_project_members(project)

    context = {
        **selected_project_context(project, "dashboard"),
        "stats": [
            {"label": "Total Tasks", "value": tasks.count(), "color": "pink"},
            {"label": "In Progress", "value": tasks.filter(status=Task.Status.IN_PROGRESS).count(), "color": "orange"},
            {"label": "Completed", "value": tasks.filter(status=Task.Status.DONE).count(), "color": "blue"},
            {"label": "Members", "value": len(members), "color": "green"},
        ],
        "blocks": [
            "View project staff",
            "View project teams",
            "Track project tasks",
            "Review project status",
            "View recent activity",
            "Back to project list",
        ],
        "summary": [
            {"label": "Company", "value": project.company.name},
            {"label": "Team", "value": get_project_team_name(project)},
            {"label": "Lead", "value": get_project_lead(project)},
            {"label": "Status", "value": project.get_status_display()},
            {"label": "Start Date", "value": date_text(project.start_date)},
            {"label": "Due Date", "value": date_text(project.due_date)},
            {"label": "Created By", "value": user_name(project.created_by)},
            {"label": "Progress", "value": f"{get_project_progress(project)}%"},
        ],
        "recent_tasks": [
            {
                "title": task.title,
                "member": user_name(task.assigned_to),
                "status": task.get_status_display(),
            }
            for task in tasks[:5]
        ],
    }
    return render(request, "company_admin/dashboard.html", context)


@login_required
def project_staff_management(request, project_id):
    project = get_project(request, project_id)
    members = get_project_members(project)

    context = {
        **selected_project_context(project, "staff"),
        "staff_stats": [
            {"label": "Project Staff", "value": len(members), "color": "pink"},
            {"label": "Active Staff", "value": len([member for member in members if member["status"] == "Active"]), "color": "green"},
            {"label": "Team Leads", "value": len([member for member in members if member["team_role"] == "Lead"]), "color": "blue"},
            {"label": "Teams", "value": len(get_project_teams(project)), "color": "orange"},
        ],
        "staff_actions": [
            "View staff account",
            "View team role",
            "View job role",
            "View assigned team",
            "Track account status",
            "Review project staff",
        ],
        "staff_members": [
            {
                "name": member["name"],
                "role": f'{member["job_role"]} | {member["team_role"]} | {member["team"]}',
                "status": member["status"],
            }
            for member in members
        ],
    }
    return render(request, "company_admin/staff_management.html", context)


@login_required
def project_team_management(request, project_id):
    project = get_project(request, project_id)
    teams = get_project_teams(project)

    context = {
        **selected_project_context(project, "teams"),
        "team_stats": [
            {"label": "Project Teams", "value": len(teams), "color": "orange"},
            {"label": "Team Leads", "value": TeamMember.objects.filter(team__in=teams, team_role=TeamMember.TeamRole.LEAD).count(), "color": "blue"},
            {"label": "Team Members", "value": TeamMember.objects.filter(team__in=teams).count(), "color": "pink"},
            {"label": "Tasks", "value": project.tasks.count(), "color": "green"},
        ],
        "team_actions": [
            "View project teams",
            "View team leads",
            "View team members",
            "Track assigned work",
            "Review team roles",
            "Review project progress",
        ],
        "teams": [
            {
                "name": team.name,
                "lead": user_name(next((m.user for m in team.memberships.all() if m.team_role == TeamMember.TeamRole.LEAD), None)),
                "members": team.memberships.count(),
                "project": project.name,
            }
            for team in teams
        ],
    }
    return render(request, "company_admin/team_management.html", context)


@login_required
def project_task_monitoring(request, project_id):
    project = get_project(request, project_id)
    tasks = project.tasks.select_related("assigned_to")

    context = {
        **selected_project_context(project, "tasks"),
        "task_stats": [
            {"label": "Total Tasks", "value": tasks.count(), "color": "blue"},
            {"label": "To Do", "value": tasks.filter(status=Task.Status.TODO).count(), "color": "orange"},
            {"label": "In Progress", "value": tasks.filter(status=Task.Status.IN_PROGRESS).count(), "color": "pink"},
            {"label": "Done", "value": tasks.filter(status=Task.Status.DONE).count(), "color": "green"},
        ],
        "task_actions": [
            "View project tasks",
            "View assignee name",
            "Track To Do tasks",
            "Track In Progress tasks",
            "Track Done tasks",
            "View due dates",
        ],
        "tasks": [
            {
                "title": task.title,
                "member": user_name(task.assigned_to),
                "status": task.get_status_display(),
                "priority": task.get_priority_display(),
                "due": date_text(task.due_date),
            }
            for task in tasks
        ],
    }
    return render(request, "company_admin/task_monitoring.html", context)


@login_required
def project_status_detail(request, project_id):
    project = get_project(request, project_id)
    tasks = project.tasks.all()

    context = {
        **selected_project_context(project, "status"),
        "status_stats": [
            {"label": "To Do", "value": tasks.filter(status=Task.Status.TODO).count(), "color": "orange"},
            {"label": "In Progress", "value": tasks.filter(status=Task.Status.IN_PROGRESS).count(), "color": "blue"},
            {"label": "Completed", "value": tasks.filter(status=Task.Status.DONE).count(), "color": "green"},
            {"label": "Progress", "value": f"{get_project_progress(project)}%", "color": "pink"},
        ],
        "status_actions": [
            "View project status",
            "View task progress",
            "See lead information",
            "See due date",
            "Review project summary",
            "Track completion",
        ],
        "projects": [
            {
                "name": project.name,
                "lead": get_project_lead(project),
                "status": project.get_status_display(),
            }
        ],
    }
    return render(request, "company_admin/project_status.html", context)


@login_required
def project_recent_activity(request, project_id):
    project = get_project(request, project_id)
    activities = ActivityLog.objects.filter(project=project).select_related("user")[:20]

    context = {
        **selected_project_context(project, "activity"),
        "activities": [
            {
                "title": activity.action,
                "text": activity.message,
                "time": f"{timesince(activity.created_at)} ago",
            }
            for activity in activities
        ],
    }
    return render(request, "company_admin/recent_activity.html", context)