from django.core.validators import FileExtensionValidator
from django.db import models
from django.utils import timezone
from users.models import Employee


class ExperimentNote(models.Model):
    """Класс модели "Запись об эксперименте в рабочем журнале"."""
    code_of_project = models.CharField(max_length=50, unique=True)
    title = models.CharField(max_length=255, verbose_name='Название для PDF/отчётов по эксперименту')
    comments = models.TextField(null=True, blank=True, verbose_name='Особенности эксперимента')
    status = models.CharField(max_length=16, default="draft", verbose_name="Статус записи")
    version_of_protocol = models.IntegerField(default=1,)
    latex_started_at = models.DateTimeField(default=timezone.now, verbose_name="Начало активации латекса")
    latex_completed_at = models.DateTimeField(default=timezone.now, verbose_name="Завершение активации латекса")
    is_latex_loss = models.BooleanField(default=False, verbose_name="Оценка потери латекса во время ресуспендирования")
    owner = models.ForeignKey(Employee, on_delete=models.PROTECT, null=True, blank=True,
                              verbose_name='Ответственный за запись об эксперименте')
    created_at = models.DateField(auto_now_add=True, verbose_name='Дата создания')
    updated_at = models.DateField(auto_now=True, verbose_name='Дата последнего изменения')

    def __str__(self):
        """Метод для описания модели "Запись в рабочем журнале"."""
        return f'\nЗапись об эксперименте: {self.code_of_project} - {self.title} от {self.updated_at}.'

    class Meta:
        """Класс для изменения поведения полей модели "Запись в дневнике"."""
        verbose_name = 'Запись об эксперименте'
        verbose_name_plural = 'Записи об эксперименте'
        ordering = ['owner', 'updated_at', 'title']


class FinalReport(models.Model):
    """Класс модели "Финальный отчет для руководства"."""
    experiment_note = models.ForeignKey(ExperimentNote,
                                        on_delete=models.CASCADE,
                                        verbose_name="принадлежность записи эксперименту",
                                        related_name="final_reports")
    at = models.DateTimeField(default=timezone.now, verbose_name= "Время, когда реально произошло измерение")
    operator = models.ForeignKey("auth.Employee", on_delete=models.PROTECT)
    payload = models.JSONField()
    version_of_protocol = models.IntegerField()
    is_draft = models.BooleanField(default=True)

    def __str__(self):
        """Метод для описания модели "Финальный отчет для руководства"."""
        return f'\nЗапись об эксперименте: {self.operator} - {self.experiment_note} от {self.at}.'

    class Meta:
        """Класс для изменения поведения полей модели "Финальный отчет для руководства"."""
        verbose_name = 'Финальный отчет'
        verbose_name_plural = 'Финальные отчеты'
        ordering = ['operator', 'at']
