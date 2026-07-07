from django.shortcuts import render


def lead_assigned_projects(request):
    projects = [
        {
            "id": 1,
            "name": "Website Revamp",
            "team_name": "Frontend Team",
            "status": "Active",
            "status_class": "active",
            "due_date": "20 Jul 2026",
            "task_count": 12,
            "member_count": 5,
            "progress": 68,
        },
        {
            "id": 2,
            "name": "API Integration",
            "team_name": "Backend Team",
            "status": "Pending",
            "status_class": "pending",
            "due_date": "28 Jul 2026",
            "task_count": 9,
            "member_count": 4,
            "progress": 35,
        },
        {
            "id": 3,
            "name": "Mobile Dashboard",
            "team_name": "Product Team",
            "status": "Completed",
            "status_class": "completed",
            "due_date": "10 Jul 2026",
            "task_count": 15,
            "member_count": 6,
            "progress": 100,
        },
    ]

    return render(
        request,
        "lead/assigned_projects.html",
        {
            "projects": projects,
            "lead_name": "Arun Kumar",
        },
    )


def lead_project_workspace(request, project_id):
    project = {
        "id": project_id,
        "name": "Website Revamp",
        "team_name": "Frontend Team",
        "status": "Active",
        "due_date": "20 Jul 2026",
        "task_count": 12,
        "in_progress_count": 5,
        "completed_count": 4,
        "member_count": 5,
        "progress": 68,
    }

    return render(
        request,
        "lead/project_workspace.html",
        {
            "project": project,
        },
    )