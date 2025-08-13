import secrets

from django.core.mail import send_mail
from django.db import transaction
from .models import Employee
from django.conf import settings


def generate_activation_token() -> str:
    return secrets.token_hex(32)  # 64-символьный hex


def activate_user_by_token(raw_token: str):
    token = (raw_token or "").strip().strip(".")
    if not token:
        return None
    try:
        with transaction.atomic():
            user = Employee.objects.select_for_update().get(token=token, is_active=False)
            user.is_active = True
            user.token = None
            user.save(update_fields=["is_active", "token"])
            return user
    except Employee.DoesNotExist:
        return None


def send_welcome_email(user: Employee):
    subject = f"Добро пожаловать, {user.last_name} {user.first_name}"
    message = (f"Здравствуйте, {user.last_name} {user.first_name}! "
               f"Регистрация подтверждена.")
    send_mail(subject, message, settings.EMAIL_HOST_USER, [user.email], fail_silently=True)
