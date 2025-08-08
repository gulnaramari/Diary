from django.contrib import admin
from .models import Employee


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ('id', 'email', 'phone_number')
    list_filter = ('email', 'phone_number')
    search_fields = ('email', 'phone_number')


