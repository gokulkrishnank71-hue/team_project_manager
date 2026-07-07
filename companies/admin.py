from django.contrib import admin

from .models import Company


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "phone", "created_by", "created_at")
    list_filter = ("created_at",)
    search_fields = ("name", "email", "phone")
    autocomplete_fields = ("created_by",)