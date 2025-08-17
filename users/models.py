from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import FileExtensionValidator
from django.contrib.auth.models import BaseUserManager
from .validators import image_validate


class EmployeeManager(BaseUserManager):
    """Класс менеджера модели "Сотрудник"."""

    def create_user(self, email, phone, password=None, **extra_fields):
        """Метод для создания пользователя."""
        if not email:
            raise ValueError("Укажите адрес электронной почты")
        email = self.normalize_email(email)
        if not phone:
            raise ValueError("Укажите номер телефона")

        user = self.model(email=email, phone=phone, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, phone, password=None, **extra_fields):
        """Метод для создания пользователя с правами суперпользователя."""
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        if extra_fields.get("is_staff") is not True:
            raise ValueError("Суперпользователь должен иметь is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Суперпользователь должен иметь is_superuser=True.")
        return self.create_user(email, phone, password, **extra_fields)


class Employee(AbstractUser):
    """Класс модели "Сотрудник"."""

    email = models.EmailField(
        unique=True, verbose_name="Адрес электронной почты сотрудника"
    )
    avatar = models.ImageField(
        upload_to="users/photos",
        null=True,
        blank=True,
        verbose_name="Фото профиля сотрудника",
        validators=[
            image_validate,
            FileExtensionValidator(
                ["jpg", "png"],
                "Расширение файла « %(extension)s » не допускается. "
                "Разрешенные расширения: %(allowed_extensions)s ."
                "Недопустимое расширение!",
            ),
        ],
    )
    phone = models.CharField(unique=True, max_length=12, verbose_name="Номер телефона")
    username = None

    created_at = models.DateField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateField(
        auto_now=True, verbose_name="Дата последнего изменения"
    )

    token = models.CharField(max_length=128, blank=True, null=True, db_index=True)
    is_active = models.BooleanField(default=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["phone",]

    objects = EmployeeManager()

    def __str__(self):
        """Метод для модели "Сотрудник"."""
        return f"{self.email}"

    class Meta:
        """Класс для изменения поведения полей модели "Сотрудник"."""

        verbose_name = "Сотрудник"
        verbose_name_plural = "Сотрудники"
        ordering = ["email", "phone", "created_at"]
        permissions = [
            ("can_block_user", "Заблокировать/разблокировать сотрудника"),
        ]
