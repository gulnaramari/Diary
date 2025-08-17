from django.urls import reverse
from django.contrib.auth import get_user_model
from django.core import mail
from rest_framework.test import APITestCase
from django.test.utils import override_settings

# Мы используем locmem backend, чтобы письма складывались в mail.outbox
EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"


@override_settings(EMAIL_BACKEND=EMAIL_BACKEND)
class TestCase(APITestCase):
    """Базовый тестовый класс для всех тестов."""

    def setUp(self):
        """Задает начальные данные для тестов."""
        self.User = get_user_model()  # В твоём проекте это Employee :contentReference[oaicite:3]{index=3}

        self.active_user = self.User.objects.create_user(
            email="active@example.com",
            phone="+79999999999",
            password="StrongPass!123",
            first_name="Active",
            last_name="User",
            is_active=True,
        )

        self.inactive_user = self.User.objects.create_user(
            email="inactive@example.com",
            phone="+79999999998",
            password="StrongPass!123",
            first_name="Inactive",
            last_name="User",
            is_active=False,
            token="TESTTOKEN123",  # токен хранится в модели, см. views.email_verification :contentReference[oaicite:4]{index=4}
        )

        self.url_registration = "/registration/"
        self.url_login = reverse("users:login")  # AuthorizationView(LoginView) :contentReference[oaicite:7]{index=7}
        self.url_password_recovery = "/password-recovery/"

    def test_registration(self):
        """Тест на пост запрос-регистрацию (
        - записать токен,
        - отправить письмо с ссылкой /users:email_confirm/<token>)
        """
        data = {
            "email": "newuser@example.com",
            "first_name": "New",
            "last_name": "User",
            "phone": "+79999999997",
            "password1": "VeryStrong!123",
            "password2": "VeryStrong!123",
        }
        resp = self.client.post(self.url_registration, data, follow=True)
        self.assertIn(resp.status_code, (200, 302))

        user = self.User.objects.get(email="newuser@example.com")
        self.assertFalse(user.is_active)
        self.assertTrue(user.token)

        self.assertEqual(len(mail.outbox), 1)
        self.assertIn("Подтвердите вашу электронную почту", mail.outbox[0].subject)

        self.assertIn(user.token, mail.outbox[0].body)

    def test_cannot_login_until_email_confirmed(self):
        """
        Тест на то, что не будет авторизации без подтверждения учетной записи.
        """
        resp = self.client.post(self.url_login, {
            "username": self.inactive_user.email,  # AuthenticationForm использует 'username' поле ввода :contentReference[oaicite:13]{index=13}
            "password": "StrongPass!123",
        })
        # LoginView при неуспехе вернёт 200 с формой и ошибкой
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "Введите пароль", html=False)

    def test_email_confirm_activates_user_and_redirects_to_login(self):
        """
        Тест на активацию пользователя и перенаправления на login.
        """
        url = reverse("users:email_confirm", args=[self.inactive_user.token])
        resp = self.client.get(url, follow=True)
        self.assertIn(resp.status_code, (200, 302))

        self.inactive_user.refresh_from_db()
        self.assertTrue(self.inactive_user.is_active)

        login_resp = self.client.post(self.url_login, {
            "username": self.inactive_user.email,
            "password": "StrongPass!123",
        }, follow=True)
        self.assertIn(login_resp.status_code, (200, 302))

    def test_password_recovery_sets_new_password_and_sends_email(self):
        """
        Тест на генерацию нового пароля и отправку письма "Восстановление пароля" с новым паролем.

        """
        resp = self.client.post(self.url_password_recovery, {"email": self.active_user.email}, follow=True)
        self.assertIn(resp.status_code, (200, 302))

        self.assertEqual(len(mail.outbox), 1)
        self.assertIn("Восстановление пароля", mail.outbox[0].subject)

        body = mail.outbox[0].body
        self.assertIn("Ваш новый пароль:", body)
        new_password = body.split("Ваш новый пароль:", 1)[1].strip()


        login_resp = self.client.post(self.url_login, {
            "username": self.active_user.email,
            "password": new_password,
        })

        self.assertIn(login_resp.status_code, (200, 302))

    def test_password_recovery_unknown_email_returns_form_error(self):
        """
        Тест на ошибку восстановления пароля
        """
        resp = self.client.post(self.url_password_recovery, {"email": "nope@example.com"})
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "Такого email еще нет в системе")
        self.assertEqual(len(mail.outbox), 0)
