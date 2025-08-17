from datetime import datetime
from django.db.models import Q
from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response

from drf_spectacular.utils import (
    extend_schema,
    extend_schema_view,
    OpenApiParameter,
    OpenApiTypes,
    OpenApiExample,
)
from .models import ExperimentNote
from .serialyzer import ExperimentNoteSerializer
from .permissions import IsOwnerOrReadOnly


@extend_schema_view(
    list=extend_schema(
        tags=["Experiment Notes"],
        summary="Список записей текущего пользователя",
        description="Возвращает постраничный список записей, принадлежащих текущему пользователю.",
    ),
    retrieve=extend_schema(
        tags=["Experiment Notes"],
        summary="Получить запись по ID",
        description="Возвращает запись по ID, если она принадлежит текущему пользователю.",
    ),
    create=extend_schema(
        tags=["Experiment Notes"],
        summary="Создать запись",
        description="Создаёт запись и проставляет `owner = текущий пользователь`.",
        examples=[
            OpenApiExample(
                "Пример создания",
                value={
                    "code_of_project": "NEW-1",
                    "title": "Эксперимент",
                    "comments": "Комментарий",
                    "status": "draft",
                    "version_of_protocol": 1,
                    "latex_started_at": "2025-08-01T10:00:00Z",
                    "latex_completed_at": "2025-08-01T12:00:00Z",
                    "is_latex_loss": False,
                    "optical_density": "5.00",
                    "signal_level": "0.50",
                    "storage_buffer_ph": "7.00",
                    "reminder_date": "2025-08-02T09:00:00Z",
                },
            )
        ],
    ),
    update=extend_schema(
        tags=["Experiment Notes"],
        summary="Полное обновление (PUT)",
        description="Полностью заменяет запись. Доступ только владельцу.",
    ),
    partial_update=extend_schema(
        tags=["Experiment Notes"],
        summary="Частичное обновление (PATCH)",
        description="Частично обновляет запись. Доступ только владельцу.",
    ),
    destroy=extend_schema(
        tags=["Experiment Notes"],
        summary="Удалить запись",
        description="Удаляет запись. Доступ только владельцу.",
    ),
)
class ExperimentNoteViewSet(viewsets.ModelViewSet):
    """DRF API для ExperimentNote (полностью документирован для Swagger)."""

    serializer_class = ExperimentNoteSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]

    def get_queryset(self):
        return ExperimentNote.objects.filter(owner=self.request.user).order_by(
            "-updated_at"
        )

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    @extend_schema(
        tags=["Experiment Notes"],
        summary="Поиск по записям",
        description="Ищет подстроку в `title` и `code_of_project` среди записей текущего пользователя.",
        parameters=[
            OpenApiParameter(
                name="search_query",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                required=False,
                description="Подстрока поиска по `title` и `code_of_project`.",
            ),
            OpenApiParameter(
                name="page",
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                required=False,
                description="Номер страницы постраничной выдачи.",
            ),
        ],
        responses={200: ExperimentNoteSerializer(many=True)},
        examples=[
            OpenApiExample(
                "Пример запроса",
                value=None,
                request_only=True,
                summary="?search_query=latex",
            )
        ],
    )
    @action(detail=False, methods=["get"], url_path="search")
    def search(self, request):
        q = request.query_params.get("search_query", "")
        qs = self.get_queryset()
        if q:
            qs = qs.filter(Q(title__icontains=q) | Q(code_of_project__icontains=q))
        page = self.paginate_queryset(qs)
        if page is not None:
            ser = self.get_serializer(page, many=True)
            return self.get_paginated_response(ser.data)
        ser = self.get_serializer(qs, many=True)
        return Response(ser.data)

    @extend_schema(
        tags=["Home"],
        summary="Статистика для главной страницы",
        description="Возвращает количество записей, обновлённых **сегодня** (по дате сервера).",
        responses={200: OpenApiTypes.OBJECT},
        examples=[OpenApiExample("Пример ответа", value={"count_entries": 2})],
    )
    @action(detail=False, methods=["get"], url_path="home-stats")
    def home_stats(self, request):
        count = ExperimentNote.objects.filter(updated_at=datetime.date.today()).count()
        return Response({"count_entries": count})
