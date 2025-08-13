import datetime

from django.core.exceptions import PermissionDenied
from django.urls import reverse, reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView, View
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from .forms import DateForm, ExperimentNoteForm
from .models import ExperimentNote


class ExperimentNoteListView(LoginRequiredMixin, ListView):
    """Класс-Generic для эндпоинта списка записей об экспериментах в рабочем журнале."""

    paginate_by = 10
    model = ExperimentNote
    template_name = 'experiment_note.html'
    context_object_name = 'experiment_notes'

    def get_queryset(self):
        """Метод для изменения запроса к базе данных по объектам модели "Запись об эксперименте в рабочем журнале"."""
        return ExperimentNote.objects.filter(owner=self.request.user)


class ExperimentNoteCreateView(LoginRequiredMixin, CreateView):
    """Класс-Generic для эндпоинта создания записи в рабочем журнале."""

    model = ExperimentNote
    form_class = ExperimentNoteForm
    template_name = 'adding_experiment_note.html'
    success_url = reverse_lazy('labbook:experiment_notes')

    def form_valid(self, form):
        """Метод вносит изменение в переданную после проверки на валидацию форму создания "Запись в рабочем журнале"."""
        experiment_note = form.save()
        experiment_note.owner = self.request.user
        experiment_note.save()
        return super().form_valid(form)


class ExperimentNoteDetailView(LoginRequiredMixin, DetailView):
    """Класс Generic для эндпоинта просмотра записей в рабочем журнале."""

    model = ExperimentNote
    template_name = 'experiment_note.html'

    def get_object(self, queryset=None):
        """Метод проверки на доступ к объекту "Запись в рабочем журнале"."""
        self.object = super().get_object(queryset)
        if self.object.owner != self.request.user:
            raise PermissionDenied
        return self.object


class ExperimentNoteUpdateView(LoginRequiredMixin, UpdateView):
    """Класс представления вида Generic для эндпоинта изменения записи в рабочем журнале."""

    model = ExperimentNote
    form_class = ExperimentNoteForm
    template_name = 'editing_experiment_note.html'

    def get_object(self, queryset=None):
        """Метод проверки на доступ к объекту "Запись в рабочем журнале"."""
        self.object = super().get_object(queryset)
        if self.object.owner != self.request.user:
            raise PermissionDenied
        return self.object

    def get_success_url(self, **kwargs):
        """Метод переадресации пользователя после выполнения данного представления."""
        return reverse('labbook:experiment_note', args=[self.kwargs.get('pk')])


class ExperimentNoteDeleteView(LoginRequiredMixin, DeleteView):
    """Класс представления вида Generic для эндпоинта удаления записи в в рабочем журнале."""

    model = ExperimentNote
    template_name = 'experiment_note_confirm_delete.html'
    success_url = reverse_lazy('labbook:experiment_notes')

    def get_object(self, queryset=None):
        """Метод проверки на доступ к объекту "Запись в рабочем журнале"."""
        self.object = super().get_object(queryset)
        if self.object.owner != self.request.user:
            raise PermissionDenied
        return self.object


class HomePageView(LoginRequiredMixin, ListView):
    """Класс представления вида Generic для эндпоинта главной страницы."""

    paginate_by = 14
    model = ExperimentNote
    template_name = "home.html"
    context_object_name = "experiment_notes"

    def get_context_data(self, **kwargs):
        """Метод для изменения информации выводимой в представлении."""
        context_data = super().get_context_data(**kwargs)
        context_data["count_entries"] = len(ExperimentNote.objects.filter(updated_at=datetime.date.today()))
        return context_data

    def get_queryset(self):
        """Метод для изменения запроса к базе данных по объектам модели "Запись в рабочем журнале"."""
        return ExperimentNote.objects.filter(owner=self.request.user)
