from django.core.cache import cache
from config.settings import CACHE_ENABLED
from .models import ExperimentNote


def get_from_cache():
    """Получение данных по записям из кэша, если кэш пуст берем из БД."""
    if not CACHE_ENABLED:
        return ExperimentNote.objects.all()
    key = "mailing_list"
    cache_data = cache.get(key)
    if cache_data is not None:
        return cache_data
    cache_data = ExperimentNote.objects.all()
    cache.set(key, cache_data)
    return cache_data
