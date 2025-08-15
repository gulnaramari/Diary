from django.contrib import admin
from .models import ExperimentNote


@admin.register(ExperimentNote)
class ExperimentNoteAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "code_of_project",
        "title",
        "updated_at",
        "owner__email",
    )
    list_filter = (
        "code_of_project",
        "title",
        "updated_at",
        "owner__email",
    )
    search_fields = (
        "code_of_project",
        "title",
        "updated_at",
        "owner__email",
    )

    def get_owner_email(self, obj):
        return obj.owner.email if obj.owner else "Нет данных"

    get_owner_email.short_description = "E-mail пользователя"
