from django.conf import settings
from django.db import models


class Team(models.Model):
    company = models.ForeignKey(
        "companies.Company",
        on_delete=models.CASCADE,
        related_name="teams",
    )
    name = models.CharField(max_length=150)
    description = models.TextField(blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="teams_created",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]
        constraints = [
            models.UniqueConstraint(fields=["company", "name"], name="unique_team_name_per_company"),
        ]

    def __str__(self):
        return self.name


class TeamMember(models.Model):
    class TeamRole(models.TextChoices):
        LEAD = "LEAD", "Lead"
        MEMBER = "MEMBER", "Member"

    team = models.ForeignKey(
        "teams.Team",
        on_delete=models.CASCADE,
        related_name="memberships",
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="team_memberships",
    )
    team_role = models.CharField(max_length=10, choices=TeamRole.choices)
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["team__name", "user__username"]
        constraints = [
            models.UniqueConstraint(fields=["team", "user"], name="unique_user_per_team"),
        ]

    def __str__(self):
        return f"{self.user} - {self.team} - {self.team_role}"