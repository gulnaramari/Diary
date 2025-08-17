from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .api_views import ExperimentNoteViewSet
from .views import (
    # HTML-вьюхи
    HomePageView,
    ExperimentNoteListView, ExperimentNoteCreateView,
    ExperimentNoteDetailView, ExperimentNoteUpdateView, ExperimentNoteDeleteView,
    SearchEntries,

)

app_name = "labbook"

router = DefaultRouter()
router.register(r"api/notes", ExperimentNoteViewSet, basename="notes")

urlpatterns = [
    # HTML
    path("", HomePageView.as_view(), name="home"),
    path("notes/", ExperimentNoteListView.as_view(), name="experiment_notes"),
    path("notes/add/", ExperimentNoteCreateView.as_view(), name="experiment_note_add"),
    path("notes/<int:pk>/", ExperimentNoteDetailView.as_view(), name="experiment_note"),
    path("notes/<int:pk>/edit/", ExperimentNoteUpdateView.as_view(), name="experiment_note_edit"),
    path("notes/<int:pk>/delete/", ExperimentNoteDeleteView.as_view(), name="experiment_note_delete"),
    path("notes/search/", SearchEntries.as_view(), name="search_entries"),

    # API
    path("", include(router.urls)),
]
