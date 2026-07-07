from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import redirect, render
from teams.models import TeamMember


def get_user_dashboard_url(user):
    if hasattr(user, "profile") and user.profile.system_role == "COMPANY_ADMIN":
        return "/company-admin/projects/"
    if user.is_superuser:
        return "/admin/"
    if TeamMember.objects.filter(user=user, team_role="LEAD").exists():
        return "/lead/projects/"
    if TeamMember.objects.filter(user=user, team_role="MEMBER").exists():
        return "/member/projects/"
    return "/login/"


def login_view(request):
    if request.method == "POST":
        user = authenticate(
            request,
            username=request.POST.get("username"),
            password=request.POST.get("password"),
        )
        if user:
            login(request, user)
            return redirect(get_user_dashboard_url(user))
        messages.error(request, "Invalid username or password.")
    return render(request, "accounts/login.html")


def logout_view(request):
    logout(request)
    return redirect("login")