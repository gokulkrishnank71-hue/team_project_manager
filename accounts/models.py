from django.conf import settings
from django.db import models


class UserProfile(models.Model):
    class SystemRole(models.TextChoices):
        COMPANY_ADMIN = "COMPANY_ADMIN", "Company Admin"
        STAFF = "STAFF", "Staff"

    class JobRole(models.TextChoices):
        FRONTEND_DEVELOPER = "FRONTEND_DEVELOPER", "Frontend Developer"
        BACKEND_DEVELOPER = "BACKEND_DEVELOPER", "Backend Developer"
        API_DEVELOPER = "API_DEVELOPER", "API Developer"
        UI_UX_DESIGNER = "UI_UX_DESIGNER", "UI/UX Designer"
        TESTER = "TESTER", "Tester"
        PROJECT_MANAGER = "PROJECT_MANAGER", "Project Manager"

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="profile",
    )
    company = models.ForeignKey(
        "companies.Company",
        on_delete=models.CASCADE,
        related_name="staff_profiles",
        null=True,
        blank=True,
    )
    full_name = models.CharField(max_length=150)
    phone = models.CharField(max_length=20, blank=True)
    system_role = models.CharField(max_length=20, choices=SystemRole.choices)
    job_role = models.CharField(max_length=30, choices=JobRole.choices, blank=True)
    must_change_password = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.full_name} ({self.system_role})"