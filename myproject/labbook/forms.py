from django import forms
from .models import ExperimentNote


class ExperimentNoteForm(forms.ModelForm):
    class Meta:
        model = ExperimentNote
        fields = [
            "code_of_project",
            "title",
            "comments",
            "version_of_protocol",
            "latex_started_at",
            "latex_completed_at",
            "is_latex_loss",
            "optical_density",
            "signal_level",
            "storage_buffer_ph",
            "reminder_date",

            "status",
            "picture",           # оставить, если нужно загружать
            # "owner"  ← не включаем, ставим во view
            # "created_at" ← non-editable, не включаем
            # "updated_at" ← non-editable, не включаем
        ]
        widgets = {
            "comments": forms.Textarea(attrs={"rows": 3}),
            "latex_started_at": forms.DateTimeInput(attrs={"type": "datetime-local"}),
            "latex_completed_at": forms.DateTimeInput(attrs={"type": "datetime-local"}),
            "reminder_date": forms.DateTimeInput(attrs={"type": "datetime-local"}),

            "optical_density": forms.NumberInput(attrs={"step": "0.01", "min": "0", "max": "1"}),
            "signal_level": forms.NumberInput(attrs={"step": "0.01", "min": "0", "max": "1"}),
            "storage_buffer_ph": forms.NumberInput(attrs={"step": "0.01", "min": "0", "max": "14"}),
            "version_of_protocol": forms.NumberInput(attrs={"step": "1", "min": "1"}),
        }


class DateForm(forms.Form):
    """Класс формы для дат."""

    date = forms.DateTimeField(input_formats=["%d/%m/%Y %H:%M"])
