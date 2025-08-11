from django.core.validators import FileExtensionValidator
from django.db import models
from users.validators import validate_image_size
from users.models import User


class DiaryEntry(models.Model):
    """Класс модели "Запись в дневнике"."""
    title = models.CharField(max_length=150, verbose_name='Заголовок')
    text = models.TextField(null=True, blank=True, verbose_name='Текст')
    picture = (models.ImageField
               (upload_to='personal_diary/images', null=True, blank=True, verbose_name='Изображение',
                validators=[validate_image_size,
                            FileExtensionValidator(['jpg', 'png'],
                                                   'Расширение файла « %(extension)s » не допускается. '
                                                   'Разрешенные расширения: %(allowed_extensions)s .',
                                                   'Недопустимое расширение!')]))
    reminder_date = models.DateTimeField(verbose_name='Дата напоминания', blank=True, null=True)
    create_at = models.DateField(auto_now_add=True, verbose_name='Дата создания')
    updated_at = models.DateField(auto_now=True, verbose_name='Дата последнего изменения')
    owner = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='Создал',
                              related_name='diary_entry')

    def __str__(self):
        """Метод для описания человеко читаемого вида модели "Запись в дневнике"."""
        return f'\nЗапись в дневнике: {self.title} от {self.updated_at}.'

    class Meta:
        """Класс для изменения поведения полей модели "Запись в дневнике"."""
        verbose_name = 'Запись в дневнике'
        verbose_name_plural = 'Записи в дневнике'
        ordering = ['owner', 'updated_at', 'title']


class Contact(models.Model):
    """Класс модели "Контакты"."""
    legal_address = models.TextField(null=True, blank=True, verbose_name='Юридический адрес')
    mailing_address = models.TextField(null=True, blank=True, verbose_name='Почтовый адрес')
    email = models.EmailField(unique=True, verbose_name='E-mail')
    tel = models.CharField(max_length=50, verbose_name='Телефон')

    def __str__(self):
        """Метод для описания человеко читаемого вида модели "Контакты"."""
        return (f'\n\nЮридический адрес: {self.legal_address}\nПочтовый адрес: {self.mailing_address}'
                f'\nE-mail: {self.email}\nТелефон: {self.tel}.')

    class Meta:
        """Класс для изменения поведения полей модели "Контакты"."""
        verbose_name = 'Контакты'
        verbose_name_plural = 'Контакты'
        ordering = ['mailing_address']
