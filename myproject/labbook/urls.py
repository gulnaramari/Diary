from django.urls import path
from .apps import LabbookConfig
from .views import ExperimentNoteListView, ExperimentNoteCreateView

app_name = LabbookConfig.name

urlpatterns = [
    path('experiment-notes/', ExperimentNoteListView.as_view(), name='experiment_note'),
    path('experiment-note/new/', ExperimentNoteCreateView.as_view(), name='adding_experiment_note'),

]
