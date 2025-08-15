from django.views.generic import ListView
from django.core.exceptions import PermissionDenied
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.auth.views import (
    LoginView,
    PasswordResetConfirmView,
    PasswordResetView,
)
from django.urls import reverse_lazy
from django.views.generic import DetailView
from django.views.generic.edit import FormView, UpdateView, DeleteView
from django.core.mail import send_mail
from django.utils.crypto import get_random_string
from .models import Employee
from .forms import (
    EmployeeRegistrationForm,
    UserAuthorizationForm,
    ProfilePasswordRecoveryForm,
    ProfilePasswordResetForm,
    ProfileChangingPasswordForm,
    EmployeeUpdateForm,
)
from django.conf import settings

from django.contrib import messages
from django.http import Http404
from django.shortcuts import redirect
from django.urls import reverse
from .services import activate_user_by_token, send_welcome_email, generate_activation_token


class RegistrationView(FormView):
    """Класс-Generic для эндпоинта создания пользователя."""

    template_name = "registration.html"
    form_class = EmployeeRegistrationForm
    success_url = reverse_lazy("users:login")

    def form_valid(self, form):
        """Метод вносит изменение в переданную после проверки
         на валидацию форму регистрации сотрудника."""
        user = form.save(commit=False)
        user.is_active = False
        user.token = generate_activation_token()
        user.save()

        activation_url = self.request.build_absolute_uri(
            reverse("users:email_confirm", args=[user.token])
        )

        subject = "Подтвердите вашу электронную почту"
        message = (
            f"Здравствуйте, {user.last_name} {user.first_name}!\n"
            f"Для активации вашей учетной записи перейдите по ссылке:\n{activation_url}\n"
        )
        send_mail(subject, message, settings.EMAIL_HOST_USER, [user.email], fail_silently=False)
        return super().form_valid(form)


class AuthorizationView(LoginView):
    """Класс для эндпоинта авторизации сотрудника."""

    form_class = UserAuthorizationForm
    template_name = "login.html"
    success_url = reverse_lazy("labbook:home")


class ProfileView(LoginRequiredMixin, DetailView):
    """Класс-Generic для эндпоинта просмотра профиля сотрудника."""

    model = Employee
    template_name = "profile.html"
    context_object_name = "profile"

    def get_object(self, queryset=None):
        """Метод проверки на доступ к объекту модели сотрудника."""
        self.object = super().get_object(queryset)
        if self.object != self.request.user:
            raise PermissionDenied
        return self.object


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    """Класс-Generic для эндпоинта редактирования профиля сотрудника."""

    model = Employee
    form_class = EmployeeUpdateForm
    template_name = "editing_profile.html"
    success_url = reverse_lazy("users:profile")

    def get_object(self, queryset=None):
        """Метод проверки на доступ к объекту модели сотрудника."""
        self.object = super().get_object(queryset)
        if self.object != self.request.user:
            raise PermissionDenied
        return self.object


class ProfileDeletingView(DeleteView):
    """Класс-Generic для эндпоинта удаления профиля сотрудника."""

    model = Employee
    template_name = "deleting_profile.html"
    success_url = reverse_lazy("users:profiles")

    def get_object(self, queryset=None):
        """Метод проверки на доступ к объекту модели сотрудника."""
        self.object = super().get_object(queryset)
        if self.object != self.request.user and not self.request.user.is_superuser:
            raise PermissionDenied
        return self.object


class ProfilesListView(LoginRequiredMixin, ListView):
    """Класс-Generic для эндпоинта списка сотрудников."""

    model = Employee
    template_name = "users.html"

    def test_func(self):
        """Метод для тестирования."""
        return self.request.user.is_superuser


class ProfilePasswordRecoveryView(FormView):
    """Класс для запроса на восстановления пароля."""

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
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[user.email],
            fail_silently=False,
        )
        return super().form_valid(form)


class ProfilePasswordResetView(SuccessMessageMixin, PasswordResetView):
    """Класс по сбросу пароля."""

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


def email_verification(request, token):
    user = activate_user_by_token(token)
    if not user:
        raise Http404("Ссылка недействительна или уже использована.")

    send_welcome_email(user)

    messages.success(request, "Почта подтверждена. Войдите в аккаунт.")
    return redirect(reverse("users:login"))
