from django.urls import path
from . import lead_views
from . import member_views

urlpatterns = [
    path("lead/projects/", lead_views.lead_assigned_projects, name="lead-assigned-projects"),
    path("lead/projects/<int:project_id>/", lead_views.lead_project_workspace, name="lead-project-workspace"),
    path("lead/projects/<int:project_id>/tasks/", lead_views.lead_project_tasks, name="lead-project-tasks"),
    path("lead/projects/<int:project_id>/members/", lead_views.lead_project_members, name="lead-project-members"),
    path("lead/projects/<int:project_id>/status/", lead_views.lead_project_status, name="lead-project-status"),
    path("lead/projects/<int:project_id>/activity/", lead_views.lead_project_activity, name="lead-project-activity"),
    path("lead/projects/<int:project_id>/profile/", lead_views.lead_profile, name="lead-profile"),

    path("member/projects/", member_views.member_assigned_projects, name="member-assigned-projects"),
    path("member/projects/<int:project_id>/", member_views.member_project_detail, name="member-project-detail"),
    path("member/projects/<int:project_id>/tasks/", member_views.member_my_tasks, name="member-my-tasks"),
    path("member/projects/<int:project_id>/tasks/<int:task_id>/", member_views.member_task_detail, name="member-task-detail"),
    path("member/projects/<int:project_id>/activity/", member_views.member_activity, name="member-activity"),
    path("member/projects/<int:project_id>/profile/", member_views.member_profile, name="member-profile"),
]