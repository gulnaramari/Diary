from django import forms
from .models import ExperimentNote
from django.core.exceptions import ValidationError


class ExperimentNoteForm(forms.ModelForm):
    """Класс формы модели "Запись об эксперименте в рабочем журнале"."""

    reminder_date = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={"type": "datetime-local"}),
        required=False,
        label="Напомнить о завершении термостатирования",
    )

    class Meta:
        """Класс для изменения поведения полей формы модели "Запись об эксперименте в рабочем журнале"."""

        model = ExperimentNote
        fields = ["title", "reminder_date", "comments"]

    def clean_reminder_date(self):
        """Метод проверки поля "Дата напоминания о завершении термостатирования" формы модели "Запись в дневнике"."""
        cleaned_experiment_note_pk = self.instance.pk
        reminder_date = self.cleaned_data.get("reminder_date")

        if (
            ExperimentNote.objects.filter(reminder_date=reminder_date)
            .exclude(id=cleaned_experiment_note_pk)
            .exists()
            and not None
        ):
            raise ValidationError("Данное время уже занято другой записью.")
        return reminder_date

    def __init__(self, *args, **kwargs):
        """Инициализирует поля формы"""
        super(ExperimentNoteForm, self).__init__(*args, **kwargs)
        self.fields["title"].widget.attrs.update(
            {"class": "form-control", "placeholder": "Введите заголовок записи"}
        )
        self.fields["reminder_date"].widget.attrs.update(
            {
                "class": "form-control",
                "aria-label": "Напомнить о завершении термостатирования",
            }
        )
        self.fields["comments"].widget.attrs.update(
            {
                "class": "form-control",
                "id": "exampleFormControlTextarea1",
                "rows": "4",
                "placeholder": "Введите текст записи",
            }
        )


class DateForm(forms.Form):
    """Класс формы для дат."""

    date = forms.DateTimeField(input_formats=["%d/%m/%Y %H:%M"])
