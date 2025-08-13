from django.core.exceptions import ValidationError


def image_validate(image):
    """Функция для проверки размера загружаемого изображения."""
    max_size = 5 * 1024 * 1024

    if image.size > max_size:
        raise ValidationError(" Размер изображения должен быть меньше 5 МБ.")
