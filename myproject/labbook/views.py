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
