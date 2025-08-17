from decimal import Decimal
from datetime import timedelta
from django.core.exceptions import PermissionDenied
from django.test import RequestFactory
from django.utils import timezone
from rest_framework.test import APITestCase
from .models import ExperimentNote
from .forms import ExperimentNoteForm
from .views import (
    ExperimentNoteCreateView,
    ExperimentNoteUpdateView,
    ExperimentNoteDeleteView,
    HomePageView,
)
from users.models import Employee


class TestCase(APITestCase):
    """Базовый тестовый класс для всех тестов."""

    def setUp(self):
        """Задает начальные данные для тестов."""
        self.factory = RequestFactory()

        self.user1 = Employee.objects.create_user(
            email="owner@example.com",
            phone="+79000000000",
            password="Pass!12345",
            is_active=True,
        )
        self.user2 = Employee.objects.create_user(
            email="other@example.com",
            phone="+79000000001",
            password="Pass!12345",
            is_active=True,
        )

        self.client.force_login(self.user1)

        self.t0 = timezone.now().replace(minute=0, second=0, microsecond=0)
        self.started = self.t0
        self.completed = self.started + timedelta(hours=2)
        self.reminder = self.started + timedelta(days=1)

        self.valid_payload = {
            "code_of_project": "NEW-1",
            "title": "Эксперимент по латексу",
            "comments": "Комментарий",
            "status": "draft",
            "version_of_protocol": 1,
            "latex_started_at": self.started,
            "latex_completed_at": self.completed,
            "is_latex_loss": False,
            "optical_density": Decimal("5.00"),
            "signal_level": Decimal("0.50"),
            "storage_buffer_ph": Decimal("7.00"),
            "reminder_date": self.reminder,
        }

    def _create_note(self, owner, **overrides):
        """Тест на создание записи"""
        data = dict(self.valid_payload)
        data.update(overrides)
        note = ExperimentNote(owner=owner, **data)
        note.full_clean()
        note.save()
        return note

    def test_create_sets_owner(self):
        """Тест на присваивание записи владельцу"""
        form = ExperimentNoteForm(
            data={
                "code_of_project": "FORM-1",
                "title": "Через форму",
                "comments": "OK",
                "status": "draft",
                "version_of_protocol": 1,
                "latex_started_at": self.started.strftime("%Y-%m-%d %H:%M"),
                "latex_completed_at": self.completed.strftime("%Y-%m-%d %H:%M"),
                "is_latex_loss": False,
                "optical_density": "5.00",
                "signal_level": "0.50",
                "storage_buffer_ph": "7.00",
                "reminder_date": self.reminder.strftime("%Y-%m-%d %H:%M"),
            }
        )
        self.assertTrue(form.is_valid(), form.errors)

        request = self.factory.post("/labbook/add/", data=form.data)
        request.user = self.user1
        response = ExperimentNoteCreateView.as_view()(request)
        self.assertEqual(response.status_code, 302)

        note = ExperimentNote.objects.get(code_of_project="FORM-1")
        self.assertEqual(note.owner, self.user1)

    def test_update_forbidden_for_non_owner(self):
        """Тест на проверку доступа при попытке редактирования"""
        note = self._create_note(self.user1, code_of_project="OWN-2")
        request = self.factory.post(
            f"/labbook/{note.pk}/edit/",
            data={**self.valid_payload, "title": "Нельзя менять"},
        )
        request.user = self.user2
        with self.assertRaises(PermissionDenied):
            ExperimentNoteUpdateView.as_view()(request, pk=note.pk)

    def test_delete_forbidden_for_non_owner(self):
        """Тест на проверку доступа при попытке удаления"""
        note = self._create_note(self.user1, code_of_project="OWN-3")
        request = self.factory.post(f"/labbook/{note.pk}/delete/")
        request.user = self.user2
        with self.assertRaises(PermissionDenied):
            ExperimentNoteDeleteView.as_view()(request, pk=note.pk)

    def test_homepage_counts_today_updates(self):
        """Тест на подсчет записей при попытке редактирования"""

        n3 = self._create_note(self.user1, code_of_project="YESTER-1")
        ExperimentNote.objects.filter(pk=n3.pk).update(
            updated_at=timezone.now() - timedelta(days=1)
        )

        request = self.factory.get("/home/")
        request.user = self.user1
        response = HomePageView.as_view()(request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context_data["count_entries"], 2)

    def test_form_excludes_owner_created_updated(self):
        """Тест на исключение полей owner/created_at/updated_at"""
        form = ExperimentNoteForm()
        for fld in ("owner", "created_at", "updated_at"):
            self.assertNotIn(fld, form.fields)
