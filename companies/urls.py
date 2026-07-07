from django.urls import path
from . import task_admin_views
from . import views

urlpatterns = [
    path("company-admin/", views.company_admin_overview, name="company_admin_overview"),
    path("company-admin/projects/", views.project_management, name="project_management"),

    path("company-admin/projects/<int:project_id>/", views.company_admin_project_detail, name="company_admin_project_detail"),
    path("company-admin/projects/<int:project_id>/staff/", views.project_staff_management, name="company_admin_project_staff"),
    path("company-admin/projects/<int:project_id>/teams/", views.project_team_management, name="company_admin_project_teams"),
    path("company-admin/projects/<int:project_id>/tasks/", task_admin_views.project_task_monitoring, name="company_admin_project_tasks"),
    path("company-admin/projects/<int:project_id>/tasks/create/", task_admin_views.project_task_create, name="company_admin_task_create"),
    path("company-admin/projects/<int:project_id>/tasks/<int:task_id>/update/", task_admin_views.project_task_update, name="company_admin_task_update"),
    path("company-admin/projects/<int:project_id>/tasks/<int:task_id>/delete/", task_admin_views.project_task_delete, name="company_admin_task_delete"),
    path("company-admin/projects/<int:project_id>/status/", views.project_status_detail, name="company_admin_project_status"),
    path("company-admin/projects/<int:project_id>/activity/", views.project_recent_activity, name="company_admin_project_activity"),

    path("company-admin/staff/", views.company_admin_overview, name="staff_management"),
    path("company-admin/teams/", views.company_admin_overview, name="team_management"),
    path("company-admin/tasks/", views.company_admin_overview, name="task_monitoring"),
    path("company-admin/status/", views.company_admin_overview, name="project_status"),
    path("company-admin/activity/", views.company_admin_overview, name="recent_activity"),
]