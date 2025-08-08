import secrets
from django.views.generic import ListView
from django.core.exceptions import PermissionDenied
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.auth.views import LoginView, PasswordResetConfirmView, PasswordResetView
from django.urls import reverse_lazy
from django.views.generic import DetailView
from django.views.generic.edit import FormView, UpdateView, DeleteView
from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator
from django.core.mail import send_mail
from django.utils.crypto import get_random_string
from config.settings import EMAIL_HOST_USER
from .models import Employee
from config import settings
from .forms import EmployeeRegistrationForm, UserAuthorizationForm, ProfilePasswordRecoveryForm, \
    ProfilePasswordResetForm, ProfileChangingPasswordForm, EmployeeUpdateForm


class RegistrationView(FormView):
    """Класс представления вида Generic для эндпоинта создания пользователя."""

    template_name = 'registration.html'
    form_class = EmployeeRegistrationForm
    success_url = reverse_lazy('users:login')

    def form_valid(self, form):
        """Метод вносит изменение в переданную после проверки на валидацию форму регистрации пользователя."""
        user = form.save()
        user.is_active = False
        token = secrets.token_hex(32)
        user.token = token
        user.save()
        print(user.email)
        print("Пользователь зарегистрирован")
        host = self.request.get_host()
        url_for_confirm = f'http://{host}/profile/email-confirm/{token}'
        send_mail(
            subject=f'Добро пожаловать в наш сервис. Подтвердите вашу электронную почту.',
            message=f'Здравствуйте, {user.last_name} {user.first_name}! '
                    f'Для активации вашей учетной записи пройдите по ссылке {url_for_confirm}.',
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[user.email],
        )
        return super().form_valid(form)


class AuthorizationView(LoginView):
    """Представление для эндпоинта авторизации пользователя."""

    form_class = UserAuthorizationForm
    template_name = 'login.html'
    success_url = reverse_lazy('personal_diary:home')


@method_decorator(cache_page(60 * 1), name='dispatch')
class ProfileView(LoginRequiredMixin, DetailView):
    """Класс представления вида Generic для эндпоинта просмотра профиля пользователя."""

    model = Employee
    template_name = 'profile.html'
    context_object_name = 'profile'

    def get_object(self, queryset=None):
        """Метод проверки на доступ к объекту модели "Пользователь"."""
        self.object = super().get_object(queryset)
        if self.object != self.request.user:
            raise PermissionDenied
        return self.object


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    """Класс представления вида Generic для эндпоинта редактирования профиля пользователя."""

    model = Employee
    form_class = EmployeeUpdateForm
    template_name = 'editing_profile.html'
    success_url = reverse_lazy('users:profile')

    def get_object(self, queryset=None):
        """Метод проверки на доступ к объекту модели "Пользователь"."""
        self.object = super().get_object(queryset)
        if self.object != self.request.user:
            raise PermissionDenied
        return self.object


class ProfileDeletingView(DeleteView):
    """Класс представления вида Generic для эндпоинта удаления профиля пользователя."""

    model = Employee
    template_name = 'deleting_profile.html'
    success_url = reverse_lazy('users:profiles')

    def get_object(self, queryset=None):
        """Метод проверки на доступ к объекту модели "Пользователь"."""
        self.object = super().get_object(queryset)
        if self.object != self.request.user and not self.request.user.is_superuser:
            raise PermissionDenied
        return self.object


@method_decorator(cache_page(60 * 1), name='dispatch')
class ProfilesListView(LoginRequiredMixin, ListView):
    """Класс представления вида Generic для эндпоинта списка пользователей."""

    model = Employee
    template_name = 'users.html'

    def test_func(self):
        """Метод для тестирования."""
        return self.request.user.is_superuser


class ProfilePasswordRecoveryView(FormView):
    """Представление для запроса на восстановления пароля."""

    template_name = "password_recovery.html"
    form_class = ProfilePasswordRecoveryForm
    success_url = reverse_lazy("users:login")

    def form_valid(self, form):
        """Метод вносит изменение в переданную после проверки на валидацию форму восстановления пароля пользователя."""

        email = form.cleaned_data["email"]
        user = Employee.objects.get(email=email)
        length = 12
        alphabet = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
        password = get_random_string(length, alphabet)
        user.set_password(password)
        user.save()
        send_mail(
            subject="Восстановление пароля",
            message=f"Ваш новый пароль: {password}",
            from_email=EMAIL_HOST_USER,
            recipient_list=[user.email],
            fail_silently=False,
        )
        return super().form_valid(form)


class ProfilePasswordResetView(SuccessMessageMixin, PasswordResetView):
    """Представление по сбросу пароля."""

    form_class = ProfilePasswordResetForm
    template_name = "users/password_reset.html"
    success_url = reverse_lazy("users:login")
    success_message = "Письмо с инструкцией по восстановлению пароля отправлено на ваш электронный адрес."
    subject_template_name = "users/email/password_subject_reset_mail.txt"
    email_template_name = "users/email/password_reset_mail.html"

    def get_context_data(self, **kwargs):
        """Метод для изменения информации выводимой в представлении."""
        context = super().get_context_data(**kwargs)
        context["title"] = "Запрос на восстановление пароля"
        return context


class ProfileChangingPasswordView(SuccessMessageMixin, PasswordResetConfirmView):
    """Представление установки нового пароля."""

    form_class = ProfileChangingPasswordForm
    template_name = "changing_password.html"
    success_url = reverse_lazy("users:login")
    success_message = "Пароль успешно изменен. Можете авторизоваться на сайте."

    def get_context_data(self, **kwargs):
        """Метод для изменения информации выводимой в представлении."""
        context = super().get_context_data(**kwargs)
        context["title"] = "Установить новый пароль"
        return context

