import uuid
from typing import Optional

from django.apps import apps
from django.core.cache import cache
from django.core.paginator import Paginator

from django_r2 import settings

DJANGO_R2_BUCKET_CACHE_FORMAT = "django_r2:bucket:{bucket_id}"
DJANGO_R2_BUCKET_CACHE_TTL = getattr(
    settings, "DJANGO_R2_BUCKET_CACHE_TTL", 60 * 60 * 24 * 7
)

DJANGO_R2_OBJECT_CACHE_FORMAT = "django_r2:object:{object_id}"
DJANGO_R2_OBJECT_CACHE_TTL = getattr(
    settings, "DJANGO_R2_OBJECT_CACHE_TTL", 60 * 60 * 24 * 7
)


def preflight_object_create(
    filename,
    user,
):
    Object = apps.get_model("objects", "Object")
    obj = Object.objects.create(
        filename=filename,
        added_by=user,
        source=Object.SourceChoices.USER,
    )
    return obj


def postflight_object_update(
    object_data,
    uploaded: bool = False,
    errors: Optional[dict] = None,
    file_data: Optional[dict] = None,
):
    Object = apps.get_model("objects", "Object")
    instance = Object.objects.get(
        id=object_data["object_id"], project__id=object_data["project_id"]
    )
    instance.uploaded = uploaded
    instance.errors = errors
    if isinstance(file_data, dict):
        instance.uploaded_size = file_data.get("size") or None
        instance.uploaded_type = file_data.get("type") or None
        instance.uploaded_duration = file_data.get("duration") or None
        instance.uploaded_width = file_data.get("width") or None
        instance.uploaded_height = file_data.get("height") or None
        instance.uploaded_metadata = file_data
    instance.save()
    return instance


def clear_cache_for_bucket_objects(bucket_id):
    cache_key_base = f"django_r2:bucket:{bucket_id}"
    cache.delete(cache_key_base)


def get_paginated_objects_for_bucket(
    bucket_id: uuid.UUID | str,
    page: int = 1,
    page_size: int = 50,
    force_cache_refresh: bool = False,
):
    Object = apps.get_model("objects", "Object")
    if bucket_id is None:
        return Object.objects.none()
    if str(bucket_id) == "":
        return Object.objects.none()
    cache_key_base = DJANGO_R2_BUCKET_CACHE_FORMAT.format(bucket_id=bucket_id)
    cache_key = f"{cache_key_base}:p{page}:s{page_size}"
    cached_result = cache.get(cache_key)

    if cached_result is not None and not force_cache_refresh:
        return cached_result

    queryset = Object.objects.filter(bucket__id=bucket_id).order_by("-created_at")
    paginator = Paginator(queryset, page_size)
    page_objects = paginator.get_page(page)

    # Cache for 5 minutes (300 seconds)
    cache.set(cache_key, page_objects, 300)
    return page_objects


def get_object_by_id(object_id: uuid.UUID | str, force_cache_refresh: bool = False):
    Object = apps.get_model("objects", "Object")
    cache_key = DJANGO_R2_OBJECT_CACHE_FORMAT.format(object_id=object_id)
    cached_result = cache.get(cache_key)
    if cached_result is not None and not force_cache_refresh:
        return cached_result
    try:
        instance = Object.objects.get(id=object_id)
    except Object.DoesNotExist:
        return None
    cache.set(cache_key, instance, 300)
    return instance
