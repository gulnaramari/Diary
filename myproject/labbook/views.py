import datetime
from django.core.exceptions import PermissionDenied
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db.models import Q
from django.shortcuts import render, redirect
from django.urls import reverse, reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils import timezone
from django.views.generic import ListView, DetailView, View
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from .forms import DateForm, ExperimentNoteForm
from .models import ExperimentNote


class ExperimentNoteListView(LoginRequiredMixin, ListView):
    """Класс-Generic для эндпоинта списка записей об экспериментах в рабочем журнале."""

    paginate_by = 10
    model = ExperimentNote
    template_name = "experiment_notes.html"
    context_object_name = "experiment_notes"

    def get_queryset(self):
        """Метод для изменения запроса к базе данных по объектам модели "Запись об эксперименте в рабочем журнале"."""
        return ExperimentNote.objects.filter(owner=self.request.user)


class ExperimentNoteCreateView(LoginRequiredMixin, CreateView):
    """Класс-Generic для эндпоинта создания записи в рабочем журнале."""

    model = ExperimentNote
    form_class = ExperimentNoteForm
    template_name = "adding_experiment_note.html"
    success_url = reverse_lazy("labbook:home")

    def form_valid(self, form):
        # ✅ ставим владельца до сохранения
        user = self.request.user

        # Если ваш пользовательская модель = Employee (AUTH_USER_MODEL=Employee), то так:
        form.instance.owner = user

        # Если же owner=Employee, а аутентификация идёт через User и есть связь OneToOne:
        # form.instance.owner = getattr(user, "employee", None)
        # if form.instance.owner is None:
        #     form.add_error(None, "Текущий пользователь не привязан к Employee — сохранить нельзя.")
        #     return self.form_invalid(form)

        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["created_today"] = timezone.localdate()
        return ctx


class ExperimentNoteDetailView(LoginRequiredMixin, DetailView):
    """Класс Generic для эндпоинта просмотра записей в рабочем журнале."""

    model = ExperimentNote
    template_name = "experiment_note.html"

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
    template_name = "editing_experiment_note.html"

    def get_object(self, queryset=None):
        """Метод проверки на доступ к объекту "Запись в рабочем журнале"."""
        self.object = super().get_object(queryset)
        if self.object.owner != self.request.user:
            raise PermissionDenied
        return self.object

    def get_success_url(self, **kwargs):
        """Метод переадресации пользователя после выполнения данного представления."""
        return reverse("labbook:experiment_note", args=[self.kwargs.get("pk")])


class ExperimentNoteDeleteView(LoginRequiredMixin, DeleteView):
    """Класс представления вида Generic для эндпоинта удаления записи в в рабочем журнале."""

    model = ExperimentNote
    template_name = "experiment_note_confirm_delete.html"
    success_url = reverse_lazy("labbook:experiment_notes")

    def get_object(self, queryset=None):
        """Метод проверки на доступ к объекту "Запись в рабочем журнале"."""
        self.object = super().get_object(queryset)
        if self.object.owner != self.request.user:
            raise PermissionDenied
        return self.object


class HomePageView(LoginRequiredMixin, ListView):
    """Класс Generic для эндпоинта главной страницы."""

    paginate_by = 14
    model = ExperimentNote
    template_name = "home.html"
    context_object_name = "experiment_notes"

    def get_context_data(self, **kwargs):
        """Метод для изменения информации выводимой в представлении."""
        context_data = super().get_context_data(**kwargs)
        context_data["count_entries"] = len(
            ExperimentNote.objects.filter(updated_at=datetime.date.today())
        )
        return context_data

    def get_queryset(self):
        """Метод для изменения запроса к базе данных по объектам модели "Запись в рабочем журнале"."""
        return ExperimentNote.objects.filter(owner=self.request.user)


def choice_date(self, request):
    """Метод запроса POST для вывода отфильтрованной информации по записям по выбранной дате."""

    if request.method == 'POST':
        form = DateForm(request.POST or None)
        if form.is_valid():
            selected_date = form.cleaned_data.get('datepicker')
            return redirect('labbook:home', kwargs=selected_date)
    else:
        form = DateForm()
    return render(request, 'home.html', {'form': form})


class SearchEntries(LoginRequiredMixin, View):
    """Класс представления вида View для эндпоинта поиска по записям сотрудника."""

    paginate_by = 10
    model = ExperimentNote
    template_name = 'experiment_notes.html'
    context_object_name = 'experiment_notes'

    def get(self, request, *args, **kwargs):
        """Метод запроса GET для вывода отфильтрованной ключевому слову запроса информации по записям."""
        context = {}
        search_query = request.GET.get('search_query')
        user_entries = ExperimentNote.objects.filter(owner=self.request.user)
        if search_query is not None:
            experiment_notes = user_entries.filter(
                Q(title__icontains=search_query) | Q(text__icontains=search_query)).\
                order_by('updated_at')

            context['last_search_query'] = '?search_query=%s' % search_query
            current_page = Paginator(experiment_notes, 10)

            page = request.GET.get('page')
            try:
                context['experiment_notes'] = current_page.page(page)
            except PageNotAnInteger:
                context['experiment_notes'] = current_page.page(1)
            except EmptyPage:
                context['experiment_notes'] = current_page.page(current_page.num_pages)
            return render(request, template_name=self.template_name, context=context)
        elif search_query == '':
            context['last_search_query'] = '?search_query=%s' % search_query
            current_page = Paginator(user_entries, 10)

            page = request.GET.get('page')
            try:
                context['experiment_notes'] = current_page.page(page)
            except PageNotAnInteger:
                context['experiment_notes'] = current_page.page(1)
            except EmptyPage:
                context['experiment_notes'] = current_page.page(current_page.num_pages)

            return render(request, template_name=self.template_name, context=context)
        else:
            context['last_search_query'] = '?search_query=%s' % search_query
            current_page = Paginator(user_entries, 10)

            page = request.GET.get('page')
            try:
                context['experiment_notes'] = current_page.page(page)
            except PageNotAnInteger:
                context['experiment_notes'] = current_page.page(1)
            except EmptyPage:
                context['experiment_notes'] = current_page.page(current_page.num_pages)

            return render(request, template_name=self.template_name, context=context)
