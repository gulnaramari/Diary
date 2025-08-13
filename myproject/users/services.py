from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from django.urls import reverse
from django.core.mail import send_mail
from config import settings
from users.models import Employee


def email_verification(request, token):
    """Функция отправки письма для подтверждения регистрации пользователя."""
    user = get_object_or_404(Employee, token=token)
    user.is_active = True
    user.save()
    subject = f'Добро пожаловать в наш сервис, {user.last_name} {user.first_name}.'
    message = f'Здравствуйте {user.last_name} {user.first_name}! Спасибо, что зарегистрировались в нашем сервисе!'
    from_email = settings.EMAIL_HOST_USER
    recipient_list = [user.email]
    send_mail(subject, message, from_email, recipient_list)
    return redirect(reverse('users:login'))
