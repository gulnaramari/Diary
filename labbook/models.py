from django.core.exceptions import ValidationError
from django.core.validators import (
    FileExtensionValidator,
    MinValueValidator,
    MaxValueValidator,
)
from django.db import models
from django.utils import timezone
from users.models import Employee

from users.validators import image_validate


class ExperimentNote(models.Model):
    """Класс модели "Запись об эксперименте в рабочем журнале"."""

    code_of_project = models.CharField(max_length=50, unique=True)
    title = models.CharField(
        max_length=255, verbose_name="Название для PDF/отчётов по эксперименту"
    )
    comments = models.TextField(
        null=True, blank=True, verbose_name="Особенности эксперимента"
    )
    status = models.CharField(
        max_length=16, default="draft", verbose_name="Статус записи"
    )
    version_of_protocol = models.IntegerField(
        default=1, verbose_name="Версия протокола"
    )

    # Активация латекса
    latex_started_at = models.DateTimeField(
        default=timezone.now, verbose_name="Начало активации латекса"
    )
    latex_completed_at = models.DateTimeField(
        default=timezone.now, verbose_name="Завершение активации латекса"
    )

    # Потери латекса (булево — оставляем как у тебя)
    is_latex_loss = models.BooleanField(
        default=False, verbose_name="Потери латекса во время ресуспендирования"
    )

    optical_density = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        default=0.00,
        validators=[MinValueValidator(0.00), MaxValueValidator(10.00)],
        verbose_name="Оптическая плотность реагента",
    )

    signal_level = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        default=0.00,
        validators=[MinValueValidator(0.00), MaxValueValidator(1.00)],
        verbose_name="Уровень сигнала в реакции",
    )

    # pH буфера: 0.00..14.00, два знака после запятой
    storage_buffer_ph = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        default=0.00,
        validators=[MinValueValidator(0.00), MaxValueValidator(14.00)],
        verbose_name="Значение рН буфера для хранения готового реагента",
    )

    picture = models.ImageField(
        upload_to="labbook/images",
        null=True,
        blank=True,
        verbose_name="Изображение",
        validators=[
            image_validate,
            FileExtensionValidator(
                ["jpg", "png"],
                "Расширение файла « %(extension)s » не допускается. "
                "Разрешенные расширения: %(allowed_extensions)s .",
                "Недопустимое расширение!",
            ),
        ],
    )

    # Напоминание о завершении термостатирования
    reminder_date = models.DateTimeField(
        verbose_name="Дата напоминания о необходимости термостатирования",
        blank=True,
        null=True,
    )

    owner = models.ForeignKey(
        Employee,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        verbose_name="Ответственный за запись об эксперименте",
    )

    # Даты отчёта
    created_at = models.DateField(
        auto_now_add=True, verbose_name="Дата создания отчёта"
    )

    updated_at = models.DateField(
        auto_now=True, verbose_name="Дата последнего изменения"
    )

    def clean(self):
        """Метод валидации данных"""
        errors = {}

        # завершение активации не раньше начала
        if self.latex_started_at and self.latex_completed_at:
            if self.latex_completed_at < self.latex_started_at:
                errors["latex_completed_at"] = (
                    "Завершение активации не может быть раньше начала."
                )

        # завершение отчёта не раньше создания
        if self.created_at and self.updated_at:
            if self.updated_at < self.created_at:
                errors["updated_at"] = (
                    "Дата обновления отчёта не может быть раньше даты создания."
                )

        if errors:
            raise ValidationError(errors)

    def __str__(self):
        return f"\nЗапись об эксперименте: {self.code_of_project} - {self.title} от {self.updated_at}."

    class Meta:
        verbose_name = "Запись об эксперименте"
        verbose_name_plural = "Записи об эксперименте"
        ordering = ["owner", "updated_at", "title"]
