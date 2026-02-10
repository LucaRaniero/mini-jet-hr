from django.contrib import admin

from .models import Employee


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ["last_name", "first_name", "email", "role", "hire_date", "is_active"]
    list_filter = ["role", "is_active", "department"]
    search_fields = ["first_name", "last_name", "email"]
    ordering = ["last_name", "first_name"]
