from django.urls import path

from django_r2.buckets import views as buckets_views
from django_r2.objects import views as objects_views
from django_r2.views import upload_complete_view, upload_view

app_name = "django_r2"

urlpatterns = [
    path("", buckets_views.BucketListView.as_view(), name="buckets-list"),
    path(
        "<uuid:bucket_id>/",
        objects_views.ObjectListView.as_view(),
        name="objects-list",
    ),
    path(
        "<uuid:bucket_id>/<uuid:pk>/",
        objects_views.ObjectDetailView.as_view(),
        name="objects-detail",
    ),
    path(
        "<uuid:bucket_id>/<uuid:pk>/download/",
        objects_views.ObjectProxyDownloadView.as_view(),
        name="objects-download",
    ),
    path(
        "<uuid:bucket_id>/<uuid:pk>/delete/",
        objects_views.ObjectDeleteView.as_view(),
        name="objects-delete",
    ),
    path("<uuid:bucket_id>/upload/", upload_view, name="upload"),
    path(
        "<uuid:bucket_id>/upload/complete/",
        upload_complete_view,
        name="complete",
    ),
]
