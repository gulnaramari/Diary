from rest_framework import serializers
from .models import ExperimentNote


class ExperimentNoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExperimentNote
        fields = "__all__"
        read_only_fields = ("id", "owner", "created_at", "updated_at")
