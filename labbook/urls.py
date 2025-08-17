from django.urls import include
from django.urls import path
from .apps import LabbookConfig

from .views import (
    ExperimentNoteListView,
    ExperimentNoteCreateView,
    HomePageView,
    ExperimentNoteDetailView,
    ExperimentNoteUpdateView,
    ExperimentNoteDeleteView, choice_date, SearchEntries,
)

app_name = LabbookConfig.name

router = DefaultRouter()
router.register(r"api/notes", ExperimentNoteViewSet, basename="notes")

urlpatterns = [
    path("", HomePageView.as_view(), name="home"),

    path(
        "experiment-notes/", ExperimentNoteListView.as_view(), name="experiment_notes"
    ),
    path(
        "experiment-note/new/",
        ExperimentNoteCreateView.as_view(),
        name="adding_experiment_note",
    ),
    path(
        "experiment-note/<int:pk>/",
        ExperimentNoteDetailView.as_view(),
        name="experiment_note",
    ),
    path(
        "experiment-note/<int:pk>/edit/",
        ExperimentNoteUpdateView.as_view(),
        name="editing_experiment_note",
    ),
    path(
        "experiment-note/<int:pk>/delete/",
        ExperimentNoteDeleteView.as_view(),
        name="deleting_experiment_note",
    ),
    path('choice-date/', choice_date, name='choice_date'),
    path('search-entries/', SearchEntries.as_view(), name='search_entries'),


]
