from django.contrib import admin
from .models import Employee


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ("id", "email", "phone")
    list_filter = ("email", "phone")
    search_fields = ("email", "phone")
    readonly_fields = ("last_login", "is_superuser", "token", "password")

    def has_add_permission(self, request):
        return False
